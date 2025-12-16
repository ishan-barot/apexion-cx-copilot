import os
import uuid
from flask import Flask, render_template, request, jsonify, session
from config import Config
from models import db, QueryLog, Feedback
from query_engine import QueryEngine

def create_app():
    """application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # initialize database
    db.init_app(app)
    
    # initialize query engine
    if not app.config['OPENAI_API_KEY']:
        print("WARNING: OPENAI_API_KEY not set. Please add it to your .env file.")
    
    return app

app = create_app()

def get_session_id():
    """get or create session id for tracking user queries"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

@app.route('/')
def index():
    """main query interface"""
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    """process natural language query"""
    try:
        data = request.get_json()
        user_question = data.get('question', '').strip()
        
        if not user_question:
            return jsonify({'success': False, 'error': 'Please enter a question'}), 400
        
        # check if api key is configured
        if not app.config['OPENAI_API_KEY']:
            return jsonify({
                'success': False,
                'error': 'OpenAI API key not configured. Please add OPENAI_API_KEY to your .env file.'
            }), 500
        
        # process query
        engine = QueryEngine(app.config['OPENAI_API_KEY'])
        session_id = get_session_id()
        
        result = engine.process_query(user_question, session_id)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/history')
def history():
    """display query history"""
    session_id = get_session_id()
    
    # get queries for this session
    queries = QueryLog.query.filter_by(
        session_id=session_id
    ).order_by(QueryLog.timestamp.desc()).limit(50).all()
    
    return render_template('history.html', queries=queries)

@app.route('/logs')
def logs():
    """display comprehensive query logs for analysis"""
    # get all logs ordered by most recent
    all_logs = QueryLog.query.order_by(QueryLog.timestamp.desc()).limit(100).all()
    
    # calculate statistics
    total_queries = QueryLog.query.count()
    successful_queries = QueryLog.query.filter_by(success=True).count()
    failed_queries = QueryLog.query.filter_by(success=False).count()
    
    success_rate = (successful_queries / total_queries * 100) if total_queries > 0 else 0
    
    # get feedback stats
    helpful_count = Feedback.query.filter_by(rating='helpful').count()
    not_helpful_count = Feedback.query.filter_by(rating='not_helpful').count()
    total_feedback = helpful_count + not_helpful_count
    
    stats = {
        'total_queries': total_queries,
        'successful_queries': successful_queries,
        'failed_queries': failed_queries,
        'success_rate': round(success_rate, 1),
        'helpful_feedback': helpful_count,
        'not_helpful_feedback': not_helpful_count,
        'total_feedback': total_feedback
    }
    
    return render_template('logs.html', logs=all_logs, stats=stats)

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    """record user feedback on query quality"""
    try:
        data = request.get_json()
        log_id = data.get('log_id')
        rating = data.get('rating')
        comment = data.get('comment', '')
        
        if not log_id or not rating:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        if rating not in ['helpful', 'not_helpful']:
            return jsonify({'success': False, 'error': 'Invalid rating'}), 400
        
        # create feedback entry
        feedback = Feedback(
            query_log_id=log_id,
            rating=rating,
            comment=comment
        )
        db.session.add(feedback)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Feedback recorded'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/schema')
def schema():
    """display database schema information"""
    schema_info = {
        'customers': {
            'description': 'Customer account information',
            'columns': [
                {'name': 'id', 'type': 'Integer', 'description': 'Unique customer identifier'},
                {'name': 'name', 'type': 'String', 'description': 'Customer full name'},
                {'name': 'email', 'type': 'String', 'description': 'Customer email address'},
                {'name': 'company', 'type': 'String', 'description': 'Company name'},
                {'name': 'signup_date', 'type': 'DateTime', 'description': 'When customer joined'},
                {'name': 'tier', 'type': 'String', 'description': 'Account tier (free, pro, enterprise)'}
            ]
        },
        'support_tickets': {
            'description': 'Customer support tickets',
            'columns': [
                {'name': 'id', 'type': 'Integer', 'description': 'Unique ticket identifier'},
                {'name': 'customer_id', 'type': 'Integer', 'description': 'Reference to customer'},
                {'name': 'subject', 'type': 'String', 'description': 'Ticket subject/description'},
                {'name': 'status', 'type': 'String', 'description': 'Status (open, in_progress, resolved, closed)'},
                {'name': 'priority', 'type': 'String', 'description': 'Priority (low, medium, high, urgent)'},
                {'name': 'created_at', 'type': 'DateTime', 'description': 'When ticket was created'},
                {'name': 'resolved_at', 'type': 'DateTime', 'description': 'When ticket was resolved'}
            ]
        },
        'interactions': {
            'description': 'Support interactions with customers',
            'columns': [
                {'name': 'id', 'type': 'Integer', 'description': 'Unique interaction identifier'},
                {'name': 'ticket_id', 'type': 'Integer', 'description': 'Reference to ticket'},
                {'name': 'interaction_type', 'type': 'String', 'description': 'Type (email, chat, phone, note)'},
                {'name': 'timestamp', 'type': 'DateTime', 'description': 'When interaction occurred'},
                {'name': 'agent_name', 'type': 'String', 'description': 'Name of support agent'},
                {'name': 'duration_minutes', 'type': 'Integer', 'description': 'Duration of interaction'}
            ]
        },
        'customer_notes': {
            'description': 'Unstructured notes about customers',
            'columns': [
                {'name': 'id', 'type': 'Integer', 'description': 'Unique note identifier'},
                {'name': 'customer_id', 'type': 'Integer', 'description': 'Reference to customer'},
                {'name': 'note_text', 'type': 'Text', 'description': 'Note content'},
                {'name': 'created_by', 'type': 'String', 'description': 'Who created the note'},
                {'name': 'created_at', 'type': 'DateTime', 'description': 'When note was created'},
                {'name': 'tags', 'type': 'String', 'description': 'Comma-separated tags'}
            ]
        }
    }
    
    return render_template('schema.html', schema=schema_info)

@app.route('/health')
def health():
    """health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'database': 'connected',
        'openai_configured': bool(app.config['OPENAI_API_KEY'])
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
