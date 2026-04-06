"""
Application configuration
"""
import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///ssl_monitor.db'
    CACHE_EXPIRATION_HOURS = int(os.environ.get('CACHE_EXPIRATION_HOURS') or '24')
    SSL_CHECK_INTERVALS = {
        'critical': 1,      # < 30 days: check every hour
        'warning': 12,      # 30-90 days: check every 12 hours
        'safe': 24          # > 90 days: check daily
    }
    SLACK_WEBHOOK_URL = os.environ.get('SLACKWebhookURL', '')  # For future notifications
