#!/usr/bin/env python3
"""
Test script for Parallel Reactions Telegram Bot

This script tests the parallel processing capabilities of the bot
by simulating multiple concurrent interactions.
"""

import asyncio
import logging
import os
import random
import time
from typing import List, Dict
from datetime import datetime

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class BotTester:
    """Test class for the Parallel Reactions Bot."""
    
    def __init__(self):
        self.test_results: List[Dict] = []
        self.concurrent_tasks: List[asyncio.Task] = []
        
    async def test_parallel_processing(self, num_tasks: int = 10) -> Dict:
        """Test parallel processing with multiple concurrent tasks."""
        logger.info(f"Starting parallel processing test with {num_tasks} tasks...")
        
        start_time = time.time()
        
        # Create multiple concurrent tasks
        tasks = []
        for i in range(num_tasks):
            task = asyncio.create_task(self._simulate_bot_task(i))
            tasks.append(task)
        
        # Wait for all tasks to complete
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            # Analyze results
            success_count = sum(1 for result in results if not isinstance(result, Exception))
            error_count = len(results) - success_count
            total_time = end_time - start_time
            
            test_result = {
                'test_name': 'Parallel Processing',
                'total_tasks': num_tasks,
                'successful_tasks': success_count,
                'failed_tasks': error_count,
                'total_time': total_time,
                'average_time_per_task': total_time / num_tasks,
                'success_rate': (success_count / num_tasks) * 100,
                'timestamp': datetime.now().isoformat()
            }
            
            self.test_results.append(test_result)
            
            logger.info(f"Parallel processing test completed:")
            logger.info(f"  - Success rate: {test_result['success_rate']:.2f}%")
            logger.info(f"  - Total time: {total_time:.2f}s")
            logger.info(f"  - Average time per task: {test_result['average_time_per_task']:.2f}s")
            
            return test_result
            
        except Exception as e:
            logger.error(f"Error in parallel processing test: {e}")
            return {'error': str(e)}
    
    async def _simulate_bot_task(self, task_id: int) -> str:
        """Simulate a bot task with random processing time."""
        try:
            # Simulate random processing time (0.5 to 2 seconds)
            delay = random.uniform(0.5, 2.0)
            await asyncio.sleep(delay)
            
            # Simulate some work
            result = f"Task {task_id} completed in {delay:.2f}s"
            logger.info(f"Completed task {task_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            raise
    
    async def test_reaction_processing(self, num_messages: int = 20) -> Dict:
        """Test reaction processing with multiple messages."""
        logger.info(f"Starting reaction processing test with {num_messages} messages...")
        
        start_time = time.time()
        
        # Simulate different types of messages
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
            "Great work",
            "Awesome job",
            "LOL that's hilarious",
            "OMG that's incredible",
            "I'm crying tears of joy",
            "I'm furious about this",
            "Congratulations!",
            "Random message",
            "Another test",
            "Final message",
            "End of test"
        ]
        
        # Process messages in parallel
        tasks = []
        for i, message in enumerate(test_messages[:num_messages]):
            task = asyncio.create_task(self._simulate_reaction_processing(message, i))
            tasks.append(task)
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            # Count successful reactions
            successful_reactions = 0
            reaction_types = {}
            
            for result in results:
                if not isinstance(result, Exception) and isinstance(result, dict):
                    successful_reactions += 1
                    reaction_type = result.get('reaction_type', 'unknown')
                    reaction_types[reaction_type] = reaction_types.get(reaction_type, 0) + 1
            
            total_time = end_time - start_time
            
            test_result = {
                'test_name': 'Reaction Processing',
                'total_messages': num_messages,
                'successful_reactions': successful_reactions,
                'failed_reactions': num_messages - successful_reactions,
                'total_time': total_time,
                'average_time_per_message': total_time / num_messages,
                'success_rate': (successful_reactions / num_messages) * 100,
                'reaction_types': reaction_types,
                'timestamp': datetime.now().isoformat()
            }
            
            self.test_results.append(test_result)
            
            logger.info(f"Reaction processing test completed:")
            logger.info(f"  - Success rate: {test_result['success_rate']:.2f}%")
            logger.info(f"  - Total time: {total_time:.2f}s")
            logger.info(f"  - Reaction types: {reaction_types}")
            
            return test_result
            
        except Exception as e:
            logger.error(f"Error in reaction processing test: {e}")
            return {'error': str(e)}
    
    async def _simulate_reaction_processing(self, message: str, message_id: int) -> Dict:
        """Simulate reaction processing for a message."""
        try:
            # Simulate processing time
            delay = random.uniform(0.1, 0.8)
            await asyncio.sleep(delay)
            
            # Determine reaction type based on message content
            message_lower = message.lower()
            reaction_type = 'random'
            
            if any(word in message_lower for word in ['hello', 'hi', 'hey']):
                reaction_type = 'greeting'
            elif any(word in message_lower for word in ['good', 'great', 'awesome', 'amazing']):
                reaction_type = 'positive'
            elif any(word in message_lower for word in ['love', 'like', 'adore']):
                reaction_type = 'love'
            elif any(word in message_lower for word in ['lol', 'haha', 'funny', 'laugh']):
                reaction_type = 'funny'
            elif any(word in message_lower for word in ['wow', 'omg', 'incredible']):
                reaction_type = 'surprise'
            elif any(word in message_lower for word in ['sad', 'cry', 'tears']):
                reaction_type = 'sad'
            elif any(word in message_lower for word in ['angry', 'mad', 'furious']):
                reaction_type = 'angry'
            elif any(word in message_lower for word in ['party', 'celebrate', 'congrats']):
                reaction_type = 'celebration'
            
            return {
                'message_id': message_id,
                'message': message,
                'reaction_type': reaction_type,
                'processing_time': delay
            }
            
        except Exception as e:
            logger.error(f"Error processing message {message_id}: {e}")
            raise
    
    async def test_concurrent_users(self, num_users: int = 5, tasks_per_user: int = 3) -> Dict:
        """Test concurrent user interactions."""
        logger.info(f"Starting concurrent users test with {num_users} users, {tasks_per_user} tasks each...")
        
        start_time = time.time()
        
        # Create tasks for each user
        all_tasks = []
        for user_id in range(num_users):
            for task_id in range(tasks_per_user):
                task = asyncio.create_task(
                    self._simulate_user_interaction(user_id, task_id)
                )
                all_tasks.append(task)
        
        try:
            results = await asyncio.gather(*all_tasks, return_exceptions=True)
            end_time = time.time()
            
            # Analyze results
            successful_interactions = sum(1 for result in results if not isinstance(result, Exception))
            total_interactions = len(all_tasks)
            total_time = end_time - start_time
            
            test_result = {
                'test_name': 'Concurrent Users',
                'num_users': num_users,
                'tasks_per_user': tasks_per_user,
                'total_interactions': total_interactions,
                'successful_interactions': successful_interactions,
                'failed_interactions': total_interactions - successful_interactions,
                'total_time': total_time,
                'average_time_per_interaction': total_time / total_interactions,
                'success_rate': (successful_interactions / total_interactions) * 100,
                'timestamp': datetime.now().isoformat()
            }
            
            self.test_results.append(test_result)
            
            logger.info(f"Concurrent users test completed:")
            logger.info(f"  - Success rate: {test_result['success_rate']:.2f}%")
            logger.info(f"  - Total time: {total_time:.2f}s")
            logger.info(f"  - Interactions per second: {total_interactions / total_time:.2f}")
            
            return test_result
            
        except Exception as e:
            logger.error(f"Error in concurrent users test: {e}")
            return {'error': str(e)}
    
    async def _simulate_user_interaction(self, user_id: int, task_id: int) -> Dict:
        """Simulate a user interaction."""
        try:
            # Simulate user interaction time
            delay = random.uniform(0.2, 1.5)
            await asyncio.sleep(delay)
            
            return {
                'user_id': user_id,
                'task_id': task_id,
                'interaction_time': delay,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in user interaction {user_id}-{task_id}: {e}")
            raise
    
    def generate_test_report(self) -> str:
        """Generate a comprehensive test report."""
        if not self.test_results:
            return "No test results available."
        
        report = "🧪 **Parallel Reactions Bot Test Report**\n\n"
        report += f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Total tests run: {len(self.test_results)}\n\n"
        
        for i, result in enumerate(self.test_results, 1):
            if 'error' in result:
                report += f"**Test {i}: {result.get('test_name', 'Unknown')}** ❌\n"
                report += f"Error: {result['error']}\n\n"
            else:
                report += f"**Test {i}: {result['test_name']}** ✅\n"
                report += f"Success Rate: {result['success_rate']:.2f}%\n"
                report += f"Total Time: {result['total_time']:.2f}s\n"
                
                if 'average_time_per_task' in result:
                    report += f"Avg Time per Task: {result['average_time_per_task']:.2f}s\n"
                if 'average_time_per_message' in result:
                    report += f"Avg Time per Message: {result['average_time_per_message']:.2f}s\n"
                if 'average_time_per_interaction' in result:
                    report += f"Avg Time per Interaction: {result['average_time_per_interaction']:.2f}s\n"
                if 'reaction_types' in result:
                    report += f"Reaction Types: {result['reaction_types']}\n"
                
                report += "\n"
        
        return report
    
    async def run_all_tests(self):
        """Run all test scenarios."""
        logger.info("Starting comprehensive test suite...")
        
        # Test 1: Parallel Processing
        await self.test_parallel_processing(10)
        
        # Test 2: Reaction Processing
        await self.test_reaction_processing(15)
        
        # Test 3: Concurrent Users
        await self.test_concurrent_users(5, 4)
        
        # Generate and display report
        report = self.generate_test_report()
        logger.info("\n" + "="*50)
        logger.info("TEST REPORT")
        logger.info("="*50)
        logger.info(report)
        
        return self.test_results


async def main():
    """Main test function."""
    logger.info("Starting Parallel Reactions Bot Test Suite...")
    
    tester = BotTester()
    results = await tester.run_all_tests()
    
    logger.info("All tests completed!")
    return results


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())