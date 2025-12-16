import json
import re
from datetime import datetime
from openai import OpenAI
from models import db, QueryLog

class QueryEngine:
    """handles natural language to sql conversion and query execution"""
    
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.schema_info = self._get_schema_info()
    
    def _get_schema_info(self):
        """get database schema information for context"""
        return """
Database Schema:

1. customers table:
   - id: integer (primary key)
   - name: text (customer full name)
   - email: text (unique email address)
   - company: text (company name)
   - signup_date: datetime (when they joined)
   - tier: text (free, pro, or enterprise)

2. support_tickets table:
   - id: integer (primary key)
   - customer_id: integer (foreign key to customers)
   - subject: text (ticket description)
   - status: text (open, in_progress, resolved, closed)
   - priority: text (low, medium, high, urgent)
   - created_at: datetime (when ticket was created)
   - resolved_at: datetime (when ticket was resolved, null if not resolved)

3. interactions table:
   - id: integer (primary key)
   - ticket_id: integer (foreign key to support_tickets)
   - interaction_type: text (email, chat, phone, note)
   - timestamp: datetime (when interaction occurred)
   - agent_name: text (name of support agent)
   - duration_minutes: integer (length of interaction, null for emails/notes)

4. customer_notes table:
   - id: integer (primary key)
   - customer_id: integer (foreign key to customers)
   - note_text: text (unstructured notes about customer)
   - created_by: text (person who created the note)
   - created_at: datetime (when note was created)
   - tags: text (comma-separated tags)

Important relationships:
- customers can have multiple support_tickets
- support_tickets can have multiple interactions
- customers can have multiple customer_notes
"""
    
    def generate_sql(self, user_question, session_id):
        """convert natural language question to sql query"""
        start_time = datetime.now()
        
        try:
            # create prompt for sql generation
            system_prompt = f"""You are a SQL expert helping convert natural language questions into SQLite queries.

{self.schema_info}

Rules:
1. Only generate SELECT queries (no INSERT, UPDATE, DELETE)
2. Use proper JOINs when querying across tables
3. Format dates properly for SQLite
4. Include relevant columns for context
5. Limit results to 100 rows max
6. When searching notes, use LIKE with wildcards for fuzzy matching
7. Return only the SQL query, no explanation

Response format:
{{
    "sql": "your sql query here",
    "confidence": 0.95,
    "reasoning": "brief explanation of query logic",
    "tables_used": ["table1", "table2"]
}}"""

            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_question}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            sql_query = result.get('sql', '')
            confidence = result.get('confidence', 0.5)
            
            # validate sql for safety
            if not self._validate_sql(sql_query):
                raise ValueError("Generated SQL failed safety validation")
            
            # calculate response time
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # log the query
            log_entry = QueryLog(
                session_id=session_id,
                user_question=user_question,
                generated_sql=sql_query,
                success=True,
                response_time_ms=int(response_time),
                confidence_score=confidence
            )
            db.session.add(log_entry)
            db.session.commit()
            
            return {
                'success': True,
                'sql': sql_query,
                'confidence': confidence,
                'reasoning': result.get('reasoning', ''),
                'tables_used': result.get('tables_used', []),
                'log_id': log_entry.id
            }
            
        except Exception as e:
            # log the failure
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            log_entry = QueryLog(
                session_id=session_id,
                user_question=user_question,
                success=False,
                error_message=str(e),
                response_time_ms=int(response_time),
                confidence_score=0.0
            )
            db.session.add(log_entry)
            db.session.commit()
            
            return {
                'success': False,
                'error': str(e),
                'log_id': log_entry.id
            }
    
    def _validate_sql(self, sql):
        """validate sql query for safety"""
        if not sql or not isinstance(sql, str):
            return False
        
        # convert to lowercase for checking
        sql_lower = sql.lower().strip()
        
        # must be a select statement
        if not sql_lower.startswith('select'):
            return False
        
        # block dangerous keywords
        dangerous_keywords = [
            'drop', 'delete', 'insert', 'update', 'alter', 
            'create', 'truncate', 'exec', 'execute', 'pragma'
        ]
        
        for keyword in dangerous_keywords:
            if keyword in sql_lower:
                return False
        
        # check for multiple statements (sql injection attempt)
        if ';' in sql and not sql_lower.strip().endswith(';'):
            return False
        
        return True
    
    def execute_query(self, sql, log_id):
        """safely execute sql query and return results"""
        try:
            # execute query
            result = db.session.execute(db.text(sql))
            rows = result.fetchall()
            columns = result.keys()
            
            # convert to list of dicts
            results = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    # convert datetime to string for json serialization
                    if isinstance(value, datetime):
                        value = value.strftime('%Y-%m-%d %H:%M:%S')
                    row_dict[col] = value
                results.append(row_dict)
            
            # update log with result count
            log_entry = QueryLog.query.get(log_id)
            if log_entry:
                log_entry.result_count = len(results)
                db.session.commit()
            
            return {
                'success': True,
                'results': results,
                'count': len(results),
                'columns': list(columns)
            }
            
        except Exception as e:
            # update log with error
            log_entry = QueryLog.query.get(log_id)
            if log_entry:
                log_entry.success = False
                log_entry.error_message = str(e)
                db.session.commit()
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def summarize_results(self, user_question, sql_query, results, columns):
        """generate human-readable summary of query results"""
        try:
            # prepare results summary
            result_preview = results[:5] if len(results) > 5 else results
            
            prompt = f"""Summarize these query results in plain English for a business user.

User's question: {user_question}

SQL query executed: {sql_query}

Results (showing first 5 of {len(results)} total):
{json.dumps(result_preview, indent=2)}

Provide:
1. A clear answer to the user's question
2. Key findings from the data
3. Cite specific row numbers when referencing data (e.g., "Customer Sarah Johnson (row 1)")
4. If results are empty, explain what this means

Keep the summary concise and actionable. Use natural language, not technical jargon."""

            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that explains data insights clearly."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            # fallback to basic summary
            if len(results) == 0:
                return "No results found for your query."
            else:
                return f"Found {len(results)} results. The data includes columns: {', '.join(columns)}."
    
    def process_query(self, user_question, session_id):
        """complete end-to-end query processing"""
        
        # step 1: generate sql
        sql_result = self.generate_sql(user_question, session_id)
        
        if not sql_result['success']:
            return {
                'success': False,
                'error': sql_result['error'],
                'log_id': sql_result['log_id']
            }
        
        # step 2: execute query
        exec_result = self.execute_query(sql_result['sql'], sql_result['log_id'])
        
        if not exec_result['success']:
            return {
                'success': False,
                'error': exec_result['error'],
                'sql': sql_result['sql'],
                'log_id': sql_result['log_id']
            }
        
        # step 3: summarize results
        summary = self.summarize_results(
            user_question,
            sql_result['sql'],
            exec_result['results'],
            exec_result['columns']
        )
        
        return {
            'success': True,
            'sql': sql_result['sql'],
            'results': exec_result['results'],
            'count': exec_result['count'],
            'columns': exec_result['columns'],
            'summary': summary,
            'confidence': sql_result['confidence'],
            'reasoning': sql_result['reasoning'],
            'log_id': sql_result['log_id']
        }
