#!/usr/bin/env python3
"""
Demo script for Parallel Reactions Telegram Bot

This script demonstrates the bot's capabilities without requiring a real Telegram token.
It simulates the bot's parallel processing and reaction handling features.
"""

import asyncio
import logging
import random
from datetime import datetime
from typing import Dict, List

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class DemoBot:
    """Demo version of the Parallel Reactions Bot."""
    
    def __init__(self):
        self.reaction_counts: Dict[str, int] = {}
        self.emoji_reactions = ['👍', '👎', '❤️', '😂', '😮', '😢', '😡', '🎉']
        self.trigger_words = {
            'greeting': ['hello', 'hi', 'hey', 'good morning'],
            'positive': ['good', 'great', 'awesome', 'amazing'],
            'love': ['love', 'like', 'adore'],
            'funny': ['lol', 'haha', 'funny', 'laugh'],
            'surprise': ['wow', 'omg', 'incredible'],
            'sad': ['sad', 'cry', 'tears'],
            'angry': ['angry', 'mad', 'furious'],
            'celebration': ['party', 'celebrate', 'congrats']
        }
    
    async def simulate_parallel_processing(self, num_tasks: int = 5) -> List[Dict]:
        """Simulate parallel processing with multiple tasks."""
        logger.info(f"🚀 Starting {num_tasks} parallel tasks...")
        
        start_time = datetime.now()
        
        # Create concurrent tasks
        tasks = []
        for i in range(num_tasks):
            task = asyncio.create_task(self._simulate_task(i))
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        # Analyze results
        successful_tasks = sum(1 for result in results if not isinstance(result, Exception))
        
        logger.info(f"✅ Parallel processing completed!")
        logger.info(f"   - Success rate: {(successful_tasks/num_tasks)*100:.2f}%")
        logger.info(f"   - Total time: {total_time:.2f}s")
        logger.info(f"   - Average time per task: {total_time/num_tasks:.2f}s")
        
        return results
    
    async def _simulate_task(self, task_id: int) -> Dict:
        """Simulate a single task with random processing time."""
        # Simulate work with random delay
        delay = random.uniform(0.5, 2.0)
        await asyncio.sleep(delay)
        
        # Simulate some processing
        result = {
            'task_id': task_id,
            'processing_time': delay,
            'status': 'completed',
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"⚡ Task {task_id + 1} completed in {delay:.2f}s")
        return result
    
    async def simulate_reaction_processing(self, messages: List[str]) -> Dict:
        """Simulate reaction processing for multiple messages."""
        logger.info(f"🎭 Processing {len(messages)} messages for reactions...")
        
        start_time = datetime.now()
        reaction_results = []
        
        # Process messages in parallel
        tasks = []
        for i, message in enumerate(messages):
            task = asyncio.create_task(self._simulate_reaction(message, i))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        # Count reactions
        reaction_types = {}
        successful_reactions = 0
        
        for result in results:
            if not isinstance(result, Exception) and isinstance(result, dict):
                successful_reactions += 1
                reaction_type = result.get('reaction_type', 'unknown')
                reaction_types[reaction_type] = reaction_types.get(reaction_type, 0) + 1
                
                # Update global reaction counts
                emoji = result.get('emoji', '✨')
                self.reaction_counts[emoji] = self.reaction_counts.get(emoji, 0) + 1
        
        logger.info(f"✨ Reaction processing completed!")
        logger.info(f"   - Success rate: {(successful_reactions/len(messages))*100:.2f}%")
        logger.info(f"   - Total time: {total_time:.2f}s")
        logger.info(f"   - Reaction types: {reaction_types}")
        
        return {
            'total_messages': len(messages),
            'successful_reactions': successful_reactions,
            'total_time': total_time,
            'reaction_types': reaction_types,
            'results': results
        }
    
    async def _simulate_reaction(self, message: str, message_id: int) -> Dict:
        """Simulate reaction processing for a single message."""
        # Simulate processing time
        delay = random.uniform(0.1, 0.5)
        await asyncio.sleep(delay)
        
        # Determine reaction based on message content
        message_lower = message.lower()
        reaction_type = 'random'
        emoji = '✨'
        
        for category, words in self.trigger_words.items():
            if any(word in message_lower for word in words):
                reaction_type = category
                break
        
        # Assign emoji based on reaction type
        emoji_map = {
            'greeting': '👋',
            'positive': '👍',
            'love': '❤️',
            'funny': '😂',
            'surprise': '😮',
            'sad': '😢',
            'angry': '😡',
            'celebration': '🎉',
            'random': '✨'
        }
        
        emoji = emoji_map.get(reaction_type, '✨')
        
        return {
            'message_id': message_id,
            'message': message,
            'reaction_type': reaction_type,
            'emoji': emoji,
            'processing_time': delay
        }
    
    async def simulate_concurrent_users(self, num_users: int = 3, tasks_per_user: int = 2) -> Dict:
        """Simulate multiple users interacting concurrently."""
        logger.info(f"👥 Simulating {num_users} users with {tasks_per_user} tasks each...")
        
        start_time = datetime.now()
        
        # Create tasks for each user
        all_tasks = []
        for user_id in range(num_users):
            for task_id in range(tasks_per_user):
                task = asyncio.create_task(
                    self._simulate_user_interaction(user_id, task_id)
                )
                all_tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*all_tasks, return_exceptions=True)
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        # Analyze results
        successful_interactions = sum(1 for result in results if not isinstance(result, Exception))
        total_interactions = len(all_tasks)
        
        logger.info(f"👥 Concurrent users simulation completed!")
        logger.info(f"   - Success rate: {(successful_interactions/total_interactions)*100:.2f}%")
        logger.info(f"   - Total time: {total_time:.2f}s")
        logger.info(f"   - Interactions per second: {total_interactions/total_time:.2f}")
        
        return {
            'num_users': num_users,
            'tasks_per_user': tasks_per_user,
            'total_interactions': total_interactions,
            'successful_interactions': successful_interactions,
            'total_time': total_time
        }
    
    async def _simulate_user_interaction(self, user_id: int, task_id: int) -> Dict:
        """Simulate a user interaction."""
        # Simulate interaction time
        delay = random.uniform(0.2, 1.0)
        await asyncio.sleep(delay)
        
        return {
            'user_id': user_id,
            'task_id': task_id,
            'interaction_time': delay,
            'timestamp': datetime.now().isoformat()
        }
    
    def print_reaction_stats(self):
        """Print current reaction statistics."""
        if not self.reaction_counts:
            print("📊 No reactions recorded yet.")
            return
        
        print("\n📊 **Reaction Statistics:**")
        print("-" * 30)
        for emoji, count in sorted(self.reaction_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"{emoji} - {count} times")
    
    async def run_demo(self):
        """Run the complete demo."""
        print("🤖 **Parallel Reactions Bot Demo**")
        print("=" * 50)
        print("This demo shows the bot's parallel processing capabilities")
        print("without requiring a real Telegram token.\n")
        
        # Demo 1: Parallel Processing
        print("1️⃣ **Parallel Processing Demo**")
        print("-" * 30)
        await self.simulate_parallel_processing(5)
        
        # Demo 2: Reaction Processing
        print("\n2️⃣ **Reaction Processing Demo**")
        print("-" * 30)
        test_messages = [
            "Hello there!",
            "This is amazing!",
            "I love this bot",
            "Haha that's funny",
            "Wow incredible!",
            "I'm so sad today",
            "I'm angry about this",
            "Let's party!",
            "Good morning",
            "Great work"
        ]
        await self.simulate_reaction_processing(test_messages)
        
        # Demo 3: Concurrent Users
        print("\n3️⃣ **Concurrent Users Demo**")
        print("-" * 30)
        await self.simulate_concurrent_users(3, 2)
        
        # Show reaction stats
        print("\n4️⃣ **Reaction Statistics**")
        print("-" * 30)
        self.print_reaction_stats()
        
        print("\n🎉 **Demo completed successfully!**")
        print("The bot demonstrates excellent parallel processing capabilities!")

async def main():
    """Main demo function."""
    demo_bot = DemoBot()
    await demo_bot.run_demo()

if __name__ == "__main__":
    asyncio.run(main())