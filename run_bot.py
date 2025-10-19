#!/usr/bin/env python3
"""
Startup script for Parallel Reactions Telegram Bot
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from parallel_reactions_bot import main as run_bot
from bot_config import validate_config, get_bot_token

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('bot.log')
        ]
    )

def check_environment():
    """Check if environment is properly configured."""
    print("🔍 Checking environment...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    # Check if token is available
    try:
        token = get_bot_token()
        print(f"✅ Bot token found: {token[:10]}...")
    except ValueError as e:
        print(f"❌ {e}")
        print("Please set the TELEGRAM_BOT_TOKEN environment variable")
        return False
    
    # Validate configuration
    if not validate_config():
        print("❌ Configuration validation failed")
        return False
    
    print("✅ Environment check passed")
    return True

def print_banner():
    """Print startup banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                Parallel Reactions Telegram Bot                ║
    ║                                                              ║
    ║  🚀 Features:                                                ║
    ║  • Concurrent message processing                             ║
    ║  • Parallel reaction handling                                ║
    ║  • Real-time task monitoring                                ║
    ║  • Async/await implementation                               ║
    ║                                                              ║
    ║  📋 Commands:                                                ║
    ║  • /start - Show welcome message                            ║
    ║  • /parallel - Start parallel demo                          ║
    ║  • /reactions - Show reaction stats                         ║
    ║  • /status - Check bot status                               ║
    ║  • /stop - Stop active tasks                                ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    """Main startup function."""
    print_banner()
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    try:
        print("🚀 Starting Parallel Reactions Bot...")
        print("Press Ctrl+C to stop the bot")
        print("-" * 60)
        
        # Run the bot
        run_bot()
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
        logger.info("Bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        logger.error(f"Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()