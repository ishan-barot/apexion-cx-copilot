import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """application configuration"""
    
    # flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # database settings
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///apexion_cx.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # openai settings
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # application settings
    APP_NAME = os.getenv('APP_NAME', 'Apexion CX Copilot')
    MAX_QUERY_RESULTS = int(os.getenv('MAX_QUERY_RESULTS', 100))
    
    # logging settings
    LOG_TO_DATABASE = True
    LOG_TO_FILE = True
