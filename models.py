from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Customer(db.Model):
    """customer records with account information"""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    company = db.Column(db.String(200))
    signup_date = db.Column(db.DateTime, default=datetime.utcnow)
    tier = db.Column(db.String(50))  # free, pro, enterprise
    
    # relationships
    tickets = db.relationship('SupportTicket', backref='customer', lazy=True)
    notes = db.relationship('CustomerNote', backref='customer', lazy=True)
    
    def __repr__(self):
        return f'<Customer {self.name}>'

class SupportTicket(db.Model):
    """support ticket records tracking customer issues"""
    __tablename__ = 'support_tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    subject = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(50))  # open, in_progress, resolved, closed
    priority = db.Column(db.String(50))  # low, medium, high, urgent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    # relationships
    interactions = db.relationship('Interaction', backref='ticket', lazy=True)
    
    def __repr__(self):
        return f'<Ticket {self.id}: {self.subject[:30]}>'

class Interaction(db.Model):
    """interaction records tracking agent engagements with tickets"""
    __tablename__ = 'interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('support_tickets.id'), nullable=False)
    interaction_type = db.Column(db.String(50))  # email, chat, phone, note
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    agent_name = db.Column(db.String(200))
    duration_minutes = db.Column(db.Integer)
    
    def __repr__(self):
        return f'<Interaction {self.id}: {self.interaction_type}>'

class CustomerNote(db.Model):
    """unstructured notes about customers and their needs"""
    __tablename__ = 'customer_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    note_text = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tags = db.Column(db.String(500))  # comma-separated tags
    
    def __repr__(self):
        return f'<Note {self.id}>'

class QueryLog(db.Model):
    """comprehensive logs of all queries for analysis and debugging"""
    __tablename__ = 'query_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_question = db.Column(db.Text, nullable=False)
    generated_sql = db.Column(db.Text)
    result_count = db.Column(db.Integer)
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    response_time_ms = db.Column(db.Integer)
    confidence_score = db.Column(db.Float)  # 0-1 scale
    
    def __repr__(self):
        return f'<QueryLog {self.id}>'

class Feedback(db.Model):
    """user feedback on query quality"""
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    query_log_id = db.Column(db.Integer, db.ForeignKey('query_logs.id'), nullable=False)
    rating = db.Column(db.String(20))  # helpful, not_helpful
    comment = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # relationship
    query_log = db.relationship('QueryLog', backref='feedback_entries')
    
    def __repr__(self):
        return f'<Feedback {self.id}: {self.rating}>'
