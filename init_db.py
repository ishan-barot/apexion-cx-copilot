from datetime import datetime, timedelta
from models import db, Customer, SupportTicket, Interaction, CustomerNote
import random

def init_database(app):
    """initialize database with tables and sample data"""
    with app.app_context():
        # drop all existing tables and recreate
        db.drop_all()
        db.create_all()
        
        # add sample customers
        customers_data = [
            {
                'name': 'Sarah Johnson',
                'email': 'sarah.johnson@techcorp.com',
                'company': 'TechCorp Industries',
                'signup_date': datetime.now() - timedelta(days=365),
                'tier': 'enterprise'
            },
            {
                'name': 'Michael Chen',
                'email': 'mchen@innovate.io',
                'company': 'Innovate Labs',
                'signup_date': datetime.now() - timedelta(days=280),
                'tier': 'pro'
            },
            {
                'name': 'Emily Rodriguez',
                'email': 'emily.r@designstudio.com',
                'company': 'Creative Design Studio',
                'signup_date': datetime.now() - timedelta(days=180),
                'tier': 'pro'
            },
            {
                'name': 'David Kim',
                'email': 'dkim@startup.co',
                'company': 'Startup Ventures',
                'signup_date': datetime.now() - timedelta(days=90),
                'tier': 'free'
            },
            {
                'name': 'Lisa Anderson',
                'email': 'l.anderson@consulting.com',
                'company': 'Anderson Consulting Group',
                'signup_date': datetime.now() - timedelta(days=200),
                'tier': 'enterprise'
            },
            {
                'name': 'James Thompson',
                'email': 'jthompson@retail.com',
                'company': 'Thompson Retail Solutions',
                'signup_date': datetime.now() - timedelta(days=150),
                'tier': 'pro'
            },
            {
                'name': 'Maria Garcia',
                'email': 'maria@ecommerce.io',
                'company': 'E-Commerce Plus',
                'signup_date': datetime.now() - timedelta(days=45),
                'tier': 'free'
            },
            {
                'name': 'Robert Wilson',
                'email': 'rwilson@finance.co',
                'company': 'Wilson Financial Services',
                'signup_date': datetime.now() - timedelta(days=320),
                'tier': 'enterprise'
            }
        ]
        
        customers = []
        for data in customers_data:
            customer = Customer(**data)
            db.session.add(customer)
            customers.append(customer)
        
        db.session.commit()
        
        # add support tickets with realistic scenarios
        tickets_data = [
            {
                'customer_id': 1,
                'subject': 'API rate limits causing errors in production',
                'status': 'resolved',
                'priority': 'urgent',
                'created_at': datetime.now() - timedelta(days=30),
                'resolved_at': datetime.now() - timedelta(days=28)
            },
            {
                'customer_id': 1,
                'subject': 'Request for increased storage quota',
                'status': 'resolved',
                'priority': 'medium',
                'created_at': datetime.now() - timedelta(days=60),
                'resolved_at': datetime.now() - timedelta(days=55)
            },
            {
                'customer_id': 2,
                'subject': 'Dashboard not loading properly on Safari',
                'status': 'resolved',
                'priority': 'high',
                'created_at': datetime.now() - timedelta(days=15),
                'resolved_at': datetime.now() - timedelta(days=14)
            },
            {
                'customer_id': 2,
                'subject': 'Need help with webhook integration',
                'status': 'open',
                'priority': 'medium',
                'created_at': datetime.now() - timedelta(days=3),
                'resolved_at': None
            },
            {
                'customer_id': 3,
                'subject': 'Unable to export reports to PDF',
                'status': 'in_progress',
                'priority': 'high',
                'created_at': datetime.now() - timedelta(days=7),
                'resolved_at': None
            },
            {
                'customer_id': 4,
                'subject': 'Questions about upgrading to pro plan',
                'status': 'resolved',
                'priority': 'low',
                'created_at': datetime.now() - timedelta(days=20),
                'resolved_at': datetime.now() - timedelta(days=19)
            },
            {
                'customer_id': 4,
                'subject': 'Login issues with SSO',
                'status': 'open',
                'priority': 'urgent',
                'created_at': datetime.now() - timedelta(days=1),
                'resolved_at': None
            },
            {
                'customer_id': 5,
                'subject': 'Request for custom security audit report',
                'status': 'in_progress',
                'priority': 'high',
                'created_at': datetime.now() - timedelta(days=10),
                'resolved_at': None
            },
            {
                'customer_id': 5,
                'subject': 'Data migration assistance needed',
                'status': 'resolved',
                'priority': 'urgent',
                'created_at': datetime.now() - timedelta(days=90),
                'resolved_at': datetime.now() - timedelta(days=85)
            },
            {
                'customer_id': 6,
                'subject': 'Mobile app crashing on Android 13',
                'status': 'resolved',
                'priority': 'urgent',
                'created_at': datetime.now() - timedelta(days=25),
                'resolved_at': datetime.now() - timedelta(days=22)
            },
            {
                'customer_id': 7,
                'subject': 'Cannot add team members to account',
                'status': 'open',
                'priority': 'medium',
                'created_at': datetime.now() - timedelta(days=5),
                'resolved_at': None
            },
            {
                'customer_id': 8,
                'subject': 'Performance issues with large datasets',
                'status': 'in_progress',
                'priority': 'high',
                'created_at': datetime.now() - timedelta(days=12),
                'resolved_at': None
            },
            {
                'customer_id': 8,
                'subject': 'Request for dedicated support channel',
                'status': 'resolved',
                'priority': 'medium',
                'created_at': datetime.now() - timedelta(days=40),
                'resolved_at': datetime.now() - timedelta(days=38)
            }
        ]
        
        tickets = []
        for data in tickets_data:
            ticket = SupportTicket(**data)
            db.session.add(ticket)
            tickets.append(ticket)
        
        db.session.commit()
        
        # add interactions for tickets
        interaction_types = ['email', 'chat', 'phone', 'note']
        agents = ['Alice Cooper', 'Bob Martinez', 'Carol Davies', 'Dan Lee', 'Emma Wilson']
        
        for ticket in tickets:
            num_interactions = random.randint(2, 6)
            for i in range(num_interactions):
                interaction = Interaction(
                    ticket_id=ticket.id,
                    interaction_type=random.choice(interaction_types),
                    timestamp=ticket.created_at + timedelta(hours=i*8, minutes=random.randint(0, 480)),
                    agent_name=random.choice(agents),
                    duration_minutes=random.randint(5, 45) if random.choice(interaction_types) in ['chat', 'phone'] else None
                )
                db.session.add(interaction)
        
        db.session.commit()
        
        # add customer notes with valuable context
        notes_data = [
            {
                'customer_id': 1,
                'note_text': 'VIP customer - enterprise account with 500+ users. Very technical team, prefers detailed documentation. Main contact is their CTO.',
                'created_by': 'Alice Cooper',
                'created_at': datetime.now() - timedelta(days=100),
                'tags': 'vip,technical,enterprise'
            },
            {
                'customer_id': 1,
                'note_text': 'Mentioned they are evaluating competitors but are happy with our service. Renewal coming up in 3 months.',
                'created_by': 'Bob Martinez',
                'created_at': datetime.now() - timedelta(days=45),
                'tags': 'renewal,competitive,important'
            },
            {
                'customer_id': 2,
                'note_text': 'Growing startup, very engaged with our product. They have featured us in their tech blog and are interested in partnership opportunities.',
                'created_by': 'Carol Davies',
                'created_at': datetime.now() - timedelta(days=80),
                'tags': 'partnership,advocate,growth'
            },
            {
                'customer_id': 3,
                'note_text': 'Design agency using our platform for client projects. Requested white-label options. Could be a good case study.',
                'created_by': 'Alice Cooper',
                'created_at': datetime.now() - timedelta(days=60),
                'tags': 'agency,white-label,case-study'
            },
            {
                'customer_id': 4,
                'note_text': 'Free tier user showing high engagement. Reached out asking about pro features. Good upsell opportunity.',
                'created_by': 'Dan Lee',
                'created_at': datetime.now() - timedelta(days=15),
                'tags': 'upsell,engaged,free-tier'
            },
            {
                'customer_id': 5,
                'note_text': 'Large consulting firm with strict compliance requirements. Need to ensure all security certifications are current. Decision maker is Lisa.',
                'created_by': 'Emma Wilson',
                'created_at': datetime.now() - timedelta(days=120),
                'tags': 'enterprise,compliance,security'
            },
            {
                'customer_id': 5,
                'note_text': 'Requested custom SLA agreement. Legal team reviewing. This could set precedent for other enterprise clients.',
                'created_by': 'Alice Cooper',
                'created_at': datetime.now() - timedelta(days=30),
                'tags': 'legal,sla,enterprise'
            },
            {
                'customer_id': 6,
                'note_text': 'Retail client with seasonal traffic spikes. Need to monitor their usage during Q4 holiday season.',
                'created_by': 'Bob Martinez',
                'created_at': datetime.now() - timedelta(days=90),
                'tags': 'retail,seasonal,monitoring'
            },
            {
                'customer_id': 7,
                'note_text': 'New e-commerce customer. First time using a platform like ours. May need extra onboarding support.',
                'created_by': 'Carol Davies',
                'created_at': datetime.now() - timedelta(days=20),
                'tags': 'new,onboarding,support'
            },
            {
                'customer_id': 8,
                'note_text': 'Financial services client with complex integration needs. Working on custom API endpoints for their use case.',
                'created_by': 'Dan Lee',
                'created_at': datetime.now() - timedelta(days=150),
                'tags': 'finance,integration,custom'
            },
            {
                'customer_id': 8,
                'note_text': 'Very satisfied with dedicated support channel. They have referred two other companies to us.',
                'created_by': 'Emma Wilson',
                'created_at': datetime.now() - timedelta(days=10),
                'tags': 'referral,satisfied,advocate'
            }
        ]
        
        for data in notes_data:
            note = CustomerNote(**data)
            db.session.add(note)
        
        db.session.commit()
        
        print("Database initialized successfully with sample data!")
        print(f"- {len(customers)} customers")
        print(f"- {len(tickets)} support tickets")
        print(f"- Multiple interactions per ticket")
        print(f"- {len(notes_data)} customer notes")

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    init_database(app)
