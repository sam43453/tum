#!/usr/bin/env python3
"""
Configuration file for Parallel Reactions Telegram Bot
"""

import os
from typing import Dict, List

# Bot Configuration
BOT_CONFIG = {
    'token_env_var': 'TELEGRAM_BOT_TOKEN',
    'log_level': 'INFO',
    'max_concurrent_tasks': 50,
    'task_timeout': 30,  # seconds
    'reaction_cooldown': 1,  # seconds between reactions
}

# Reaction Configuration
REACTION_CONFIG = {
    'emoji_reactions': [
        '👍', '👎', '❤️', '😂', '😮', '😢', '😡', '🎉',
        '👋', '🔥', '💯', '✨', '🚀', '💪', '🎯', '🌟'
    ],
    'trigger_words': {
        'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon'],
        'positive': ['good', 'great', 'awesome', 'amazing', 'excellent', 'fantastic'],
        'love': ['love', 'like', 'adore', 'enjoy', 'favorite'],
        'funny': ['lol', 'haha', 'funny', 'laugh', 'hilarious', 'comedy'],
        'surprise': ['wow', 'omg', 'incredible', 'unbelievable', 'shocking'],
        'sad': ['sad', 'cry', 'tears', 'depressed', 'upset', 'disappointed'],
        'angry': ['angry', 'mad', 'furious', 'annoyed', 'irritated'],
        'celebration': ['party', 'celebrate', 'congrats', 'congratulations', 'cheers']
    },
    'default_reaction': '✨'
}

# Test Configuration
TEST_CONFIG = {
    'parallel_tasks': 10,
    'reaction_messages': 20,
    'concurrent_users': 5,
    'tasks_per_user': 4,
    'test_timeout': 60  # seconds
}

# Logging Configuration
LOGGING_CONFIG = {
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'level': 'INFO',
    'file': 'bot.log',
    'max_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}

def get_bot_token() -> str:
    """Get bot token from environment variable."""
    token = os.getenv(BOT_CONFIG['token_env_var'])
    if not token:
        raise ValueError(f"Environment variable {BOT_CONFIG['token_env_var']} is required")
    return token

def validate_config() -> bool:
    """Validate configuration settings."""
    try:
        # Check if token is available
        get_bot_token()
        
        # Validate numeric values
        assert BOT_CONFIG['max_concurrent_tasks'] > 0
        assert BOT_CONFIG['task_timeout'] > 0
        assert BOT_CONFIG['reaction_cooldown'] >= 0
        
        # Validate reaction config
        assert len(REACTION_CONFIG['emoji_reactions']) > 0
        assert len(REACTION_CONFIG['trigger_words']) > 0
        
        return True
        
    except Exception as e:
        print(f"Configuration validation failed: {e}")
        return False

if __name__ == "__main__":
    if validate_config():
        print("✅ Configuration is valid")
    else:
        print("❌ Configuration validation failed")