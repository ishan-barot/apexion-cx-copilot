# Apexion CX Copilot

A production-ready Flask application that enables natural language querying of customer experience data using OpenAI's LLM capabilities. Built as a technical showcase demonstrating practical LLM-powered tools and strong software engineering practices.

![Apexion CX Copilot](https://img.shields.io/badge/Flask-3.0.0-blue) ![Python](https://img.shields.io/badge/Python-3.8+-green) ![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange)

## Overview

Apexion CX Copilot transforms how teams interact with customer data by allowing business users to ask questions in plain English instead of writing SQL queries. The system intelligently converts natural language to SQL, executes queries safely, and summarizes results with citations to specific data points.

**Key Capabilities:**
- Natural language to SQL conversion using GPT-4
- Safe query execution with comprehensive SQL injection prevention
- Intelligent result summarization with row-level citations
- Handles both structured tables and unstructured customer notes
- Complete logging system for analysis and improvement
- User feedback mechanism to track query quality
- Query history tracking per user session

## Architecture

```
┌─────────────────┐
│  User Question  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Query Engine   │  ◄── OpenAI GPT-4
│  (NL → SQL)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SQL Validator  │  ◄── Safety checks
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SQLite DB      │  ◄── Execute query
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Summarizer     │  ◄── GPT-4 explanation
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  User Response  │
└─────────────────┘
```

## Database Schema

The system manages a comprehensive CX data model:

### **customers**
Core customer account information including tier (free/pro/enterprise), signup dates, and contact details.

### **support_tickets**
Customer support issues with status tracking (open, in_progress, resolved, closed) and priority levels (low, medium, high, urgent).

### **interactions**
Individual agent engagements with tickets including type (email, chat, phone, note), agent name, and duration.

### **customer_notes**
Unstructured notes about customers with tagging support for flexible categorization (VIP, partnership, upsell opportunities, etc.).

### **query_logs**
Comprehensive logging of all queries including prompts, generated SQL, execution time, confidence scores, and success/failure tracking.

### **feedback**
User feedback ratings (helpful/not helpful) linked to specific queries for quality measurement.

## Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- pip package manager

### Installation

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd apexion-cx-copilot
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

5. **Initialize the database:**
```bash
python init_db.py
```

This creates a SQLite database with sample customer data, support tickets, interactions, and notes.

6. **Run the application:**
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage Examples

### Example Queries

**Customer Analysis:**
- "Show me all enterprise customers who signed up in the last 6 months"
- "Which customers have the most support tickets?"
- "Find customers tagged as VIP or partnership opportunities"

**Ticket Management:**
- "What urgent tickets are currently open?"
- "Show resolved tickets from the past month"
- "Which customer has the longest average resolution time?"

**Agent Performance:**
- "Which agent handled the most phone interactions?"
- "Show me the average interaction duration by agent"
- "Who resolved the most high priority tickets?"

**Unstructured Data:**
- "Find customers interested in white-label options"
- "Show me notes mentioning compliance or security"
- "Which customers are up for renewal soon?"

### Understanding Results

The system provides three types of information:

1. **Summary**: Plain English explanation of findings with row citations
   - Example: "Customer Sarah Johnson (row 1) has 2 urgent tickets..."

2. **SQL Query**: The actual query generated for transparency and learning
   - Formatted and syntax-highlighted for readability

3. **Data Table**: Raw results with row numbers for citation reference
   - Scrollable, sortable interface for detailed analysis

## Security Features

- **SQL Injection Prevention**: Multi-layer validation ensures only SELECT queries are executed
- **Query Sanitization**: Blocks dangerous keywords (DROP, DELETE, INSERT, etc.)
- **Statement Isolation**: Prevents multiple statement execution
- **Read-Only Access**: No data modification operations allowed
- **API Key Protection**: Environment-based configuration keeps credentials secure

## Monitoring & Analytics

### Query Logs Dashboard

Track system performance and user behavior:
- Total queries processed
- Success/failure rates
- Average response times
- Confidence score distributions
- User feedback metrics

### Feedback Loop

Users rate every query result as "Helpful" or "Not Helpful":
- Identifies problematic query patterns
- Guides model improvement efforts
- Tracks user satisfaction over time

## 🛠️ Development

### Project Structure

```
apexion-cx-copilot/
├── app.py                 # Flask application and routes
├── models.py              # SQLAlchemy database models
├── query_engine.py        # NL to SQL conversion logic
├── init_db.py            # Database initialization script
├── config.py             # Configuration management
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variable template
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── history.html
│   ├── logs.html
│   └── schema.html
└── static/               # CSS and static assets
    └── style.css
```

### Adding New Features

**To add a new table:**
1. Define model in `models.py`
2. Update schema info in `query_engine.py`
3. Add sample data in `init_db.py`
4. Document in `schema.html`

**To modify query logic:**
1. Update system prompt in `query_engine.py`
2. Adjust validation rules in `_validate_sql()`
3. Test with diverse queries

### Testing Queries

The application includes a `/health` endpoint for monitoring:
```bash
curl http://localhost:5000/health
```

Returns:
```json
{
  "status": "healthy",
  "database": "connected",
  "openai_configured": true
}
```

## Customization

### Styling

All styles are in `static/style.css`. The design uses CSS variables for easy theming:

```css
:root {
    --primary-color: #2563eb;
    --success-color: #10b981;
    --error-color: #ef4444;
    /* ... more variables */
}
```

### Sample Data

Modify `init_db.py` to customize sample data:
- Add more customers, tickets, or notes
- Change date ranges for time-based queries
- Adjust customer tiers and priorities

## 📝 Best Practices Demonstrated

This project showcases several software engineering best practices:

**Clean Code**: Descriptive variable names, clear function purposes, comprehensive comments  
**Separation of Concerns**: Models, logic, and presentation layers are distinct  
**Error Handling**: Graceful degradation with user-friendly error messages  
**Security First**: Multiple layers of SQL injection prevention  
**Observability**: Comprehensive logging for debugging and analysis  
**User Experience**: Clear feedback, loading states, and helpful examples  
**Documentation**: Extensive inline comments and user-facing docs  
**Configuration Management**: Environment-based settings for flexibility  

## Troubleshooting

### "OpenAI API key not configured" error

Ensure your `.env` file exists and contains a valid API key:
```bash
OPENAI_API_KEY=sk-...
```

Restart the Flask application after making changes.

### "No module named 'flask'" error

Activate your virtual environment:
```bash
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

### Database not initializing

Delete any existing database file and reinitialize:
```bash
rm apexion_cx.db
python init_db.py
```

### Low confidence warnings

This is normal for complex or ambiguous queries. The system flags queries when it's less certain about the SQL translation. You can:
- Rephrase the question more specifically
- Check the generated SQL for accuracy
- Provide feedback to help improve the system

## Deployment

For production deployment:

1. **Change SECRET_KEY** in `.env` to a secure random value
2. **Use a production WSGI server** like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn app:app
   ```
3. **Configure HTTPS** with a reverse proxy (nginx, Apache)
4. **Use PostgreSQL** instead of SQLite for better concurrency
5. **Set up monitoring** for the `/health` endpoint
6. **Enable rate limiting** to prevent API abuse

## License

This project is available for portfolio and educational purposes. Feel free to use it as inspiration for your own projects.

## Contributing

This is a portfolio project, but feedback and suggestions are welcome! Feel free to open issues or submit pull requests.

## 👤 Author

Built by Ishan Barot (me) as a technical demonstration project.  
Website: [apexion.app](https://apexion.app)

## Acknowledgments

- OpenAI for providing the GPT-4 API
- Flask community for the excellent web framework
- SQLAlchemy for powerful ORM capabilities

---

**Built with Flask + OpenAI • [apexion.app](https://apexion.app)**
