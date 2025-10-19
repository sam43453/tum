#!/usr/bin/env python3
"""
Parallel Reactions Telegram Bot

A Telegram bot that can handle multiple reactions simultaneously using asyncio
and concurrent processing. This bot demonstrates parallel processing capabilities
for handling multiple user interactions at the same time.
"""

import asyncio
import logging
import os
import random
import time
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from telegram.error import TelegramError

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

class ParallelReactionsBot:
    """A Telegram bot that handles parallel reactions and concurrent processing."""
    
    def __init__(self):
        self.active_tasks: Dict[int, Set[asyncio.Task]] = {}
        self.reaction_counts: Dict[str, int] = {}
        self.user_sessions: Dict[int, Dict] = {}
        self.emoji_reactions = ['👍', '👎', '❤️', '😂', '😮', '😢', '😡', '🎉']
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command with parallel processing demo."""
        user_id = update.effective_user.id
        self.user_sessions[user_id] = {
            'start_time': datetime.now(),
            'reaction_count': 0,
            'active_tasks': 0
        }
        
        welcome_text = (
            "🚀 **Parallel Reactions Bot** 🚀\n\n"
            "This bot demonstrates parallel processing capabilities!\n\n"
            "**Available Commands:**\n"
            "/start - Show this welcome message\n"
            "/parallel - Start parallel reaction demo\n"
            "/reactions - Show available reactions\n"
            "/status - Check bot status\n"
            "/stop - Stop all active tasks\n\n"
            "**Features:**\n"
            "• Concurrent message processing\n"
            "• Parallel reaction handling\n"
            "• Real-time task monitoring\n"
            "• Async/await implementation"
        )
        
        keyboard = [
            [InlineKeyboardButton("🚀 Start Parallel Demo", callback_data="start_parallel")],
            [InlineKeyboardButton("📊 Show Reactions", callback_data="show_reactions")],
            [InlineKeyboardButton("📈 Status", callback_data="show_status")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def parallel_demo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Start parallel processing demonstration."""
        user_id = update.effective_user.id
        
        # Create multiple concurrent tasks
        tasks = []
        for i in range(5):
            task = asyncio.create_task(self._parallel_task(update, context, i))
            tasks.append(task)
            
            # Track active tasks
            if user_id not in self.active_tasks:
                self.active_tasks[user_id] = set()
            self.active_tasks[user_id].add(task)
        
        await update.message.reply_text(
            "🔄 Starting 5 parallel tasks...\n"
            "Each task will process independently and report back!"
        )
        
        # Wait for all tasks to complete
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Clean up completed tasks
            if user_id in self.active_tasks:
                for task in tasks:
                    self.active_tasks[user_id].discard(task)
                if not self.active_tasks[user_id]:
                    del self.active_tasks[user_id]
            
            # Report results
            success_count = sum(1 for result in results if not isinstance(result, Exception))
            await update.message.reply_text(
                f"✅ Parallel processing complete!\n"
                f"Successfully completed: {success_count}/5 tasks\n"
                f"All tasks ran concurrently using asyncio."
            )
            
        except Exception as e:
            logger.error(f"Error in parallel demo: {e}")
            await update.message.reply_text(f"❌ Error in parallel processing: {str(e)}")
    
    async def _parallel_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE, task_id: int) -> str:
        """Simulate a parallel task with random processing time."""
        try:
            # Simulate work with random delay
            delay = random.uniform(1, 3)
            await asyncio.sleep(delay)
            
            # Simulate some processing
            result = f"Task {task_id + 1} completed in {delay:.2f}s"
            
            # Send intermediate update
            await update.message.reply_text(f"⚡ Task {task_id + 1} finished!")
            
            return result
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            raise
    
    async def reactions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show available reactions and their counts."""
        if not self.reaction_counts:
            await update.message.reply_text("No reactions recorded yet. Try the /parallel command!")
            return
        
        reaction_text = "📊 **Reaction Statistics:**\n\n"
        for emoji, count in sorted(self.reaction_counts.items(), key=lambda x: x[1], reverse=True):
            reaction_text += f"{emoji} - {count} times\n"
        
        await update.message.reply_text(reaction_text, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show bot status and active tasks."""
        user_id = update.effective_user.id
        active_task_count = len(self.active_tasks.get(user_id, set()))
        total_reactions = sum(self.reaction_counts.values())
        
        status_text = (
            f"🤖 **Bot Status**\n\n"
            f"**Your Session:**\n"
            f"• Active Tasks: {active_task_count}\n"
            f"• Total Reactions: {total_reactions}\n"
            f"• Session Start: {self.user_sessions.get(user_id, {}).get('start_time', 'N/A')}\n\n"
            f"**Global Stats:**\n"
            f"• Total Users: {len(self.user_sessions)}\n"
            f"• Total Active Tasks: {sum(len(tasks) for tasks in self.active_tasks.values())}\n"
            f"• Bot Uptime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Stop all active tasks for the user."""
        user_id = update.effective_user.id
        
        if user_id in self.active_tasks:
            # Cancel all active tasks
            for task in self.active_tasks[user_id]:
                if not task.done():
                    task.cancel()
            
            task_count = len(self.active_tasks[user_id])
            del self.active_tasks[user_id]
            
            await update.message.reply_text(f"🛑 Stopped {task_count} active tasks.")
        else:
            await update.message.reply_text("ℹ️ No active tasks to stop.")
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle inline keyboard button presses."""
        query = update.callback_query
        await query.answer()
        
        if query.data == "start_parallel":
            await self.parallel_demo_command(update, context)
        elif query.data == "show_reactions":
            await self.reactions_command(update, context)
        elif query.data == "show_status":
            await self.status_command(update, context)
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle regular text messages with parallel reaction processing."""
        user_id = update.effective_user.id
        message_text = update.message.text.lower()
        
        # Process message in parallel with multiple reaction types
        tasks = []
        
        # Add reaction based on message content
        if any(word in message_text for word in ['hello', 'hi', 'hey']):
            tasks.append(self._add_reaction(update, '👋'))
        if any(word in message_text for word in ['good', 'great', 'awesome', 'amazing']):
            tasks.append(self._add_reaction(update, '👍'))
        if any(word in message_text for word in ['love', 'like', 'adore']):
            tasks.append(self._add_reaction(update, '❤️'))
        if any(word in message_text for word in ['lol', 'haha', 'funny', 'laugh']):
            tasks.append(self._add_reaction(update, '😂'))
        if any(word in message_text for word in ['wow', 'omg', 'incredible']):
            tasks.append(self._add_reaction(update, '😮'))
        if any(word in message_text for word in ['sad', 'cry', 'tears']):
            tasks.append(self._add_reaction(update, '😢'))
        if any(word in message_text for word in ['angry', 'mad', 'furious']):
            tasks.append(self._add_reaction(update, '😡'))
        if any(word in message_text for word in ['party', 'celebrate', 'congrats']):
            tasks.append(self._add_reaction(update, '🎉'))
        
        # If no specific reactions, add a random one
        if not tasks:
            random_emoji = random.choice(self.emoji_reactions)
            tasks.append(self._add_reaction(update, random_emoji))
        
        # Process all reactions in parallel
        if tasks:
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
                
                # Update user session
                if user_id in self.user_sessions:
                    self.user_sessions[user_id]['reaction_count'] += len(tasks)
                
                # Send confirmation
                reaction_emojis = [task for task in tasks if hasattr(task, '_emoji')]
                if reaction_emojis:
                    await update.message.reply_text(
                        f"✨ Added {len(tasks)} parallel reactions to your message!"
                    )
                    
            except Exception as e:
                logger.error(f"Error processing reactions: {e}")
                await update.message.reply_text("❌ Error processing reactions.")
    
    async def _add_reaction(self, update: Update, emoji: str) -> None:
        """Add a reaction to the message (simulated)."""
        try:
            # Simulate reaction processing time
            await asyncio.sleep(random.uniform(0.1, 0.5))
            
            # Update reaction count
            self.reaction_counts[emoji] = self.reaction_counts.get(emoji, 0) + 1
            
            # Store emoji for confirmation
            self._emoji = emoji
            
        except Exception as e:
            logger.error(f"Error adding reaction {emoji}: {e}")
            raise
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors in the bot."""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ An error occurred while processing your request. Please try again."
            )


def main():
    """Main function to run the bot."""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is required")
        return
    
    # Create bot instance
    bot = ParallelReactionsBot()
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("parallel", bot.parallel_demo_command))
    application.add_handler(CommandHandler("reactions", bot.reactions_command))
    application.add_handler(CommandHandler("status", bot.status_command))
    application.add_handler(CommandHandler("stop", bot.stop_command))
    application.add_handler(CallbackQueryHandler(bot.handle_callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_text_message))
    
    # Add error handler
    application.add_error_handler(bot.error_handler)
    
    # Start the bot
    logger.info("Starting Parallel Reactions Bot...")
    application.run_polling()


if __name__ == "__main__":
    main()