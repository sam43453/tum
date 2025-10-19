#!/usr/bin/env python3
"""
Test runner for Parallel Reactions Telegram Bot
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from test_parallel_bot import BotTester
from bot_config import TEST_CONFIG

def setup_test_logging():
    """Setup logging for tests."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('test_results.log')
        ]
    )

def print_test_banner():
    """Print test banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║              Parallel Reactions Bot Test Suite               ║
    ║                                                              ║
    ║  🧪 Test Scenarios:                                          ║
    ║  • Parallel Processing Test                                  ║
    ║  • Reaction Processing Test                                  ║
    ║  • Concurrent Users Test                                     ║
    ║                                                              ║
    ║  📊 Metrics:                                                 ║
    ║  • Success Rate                                              ║
    ║  • Processing Time                                           ║
    ║  • Concurrent Performance                                    ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

async def run_individual_tests():
    """Run individual test scenarios."""
    tester = BotTester()
    
    print("🧪 Running individual test scenarios...\n")
    
    # Test 1: Parallel Processing
    print("1️⃣ Testing Parallel Processing...")
    result1 = await tester.test_parallel_processing(TEST_CONFIG['parallel_tasks'])
    print(f"   Result: {result1.get('success_rate', 0):.2f}% success rate\n")
    
    # Test 2: Reaction Processing
    print("2️⃣ Testing Reaction Processing...")
    result2 = await tester.test_reaction_processing(TEST_CONFIG['reaction_messages'])
    print(f"   Result: {result2.get('success_rate', 0):.2f}% success rate\n")
    
    # Test 3: Concurrent Users
    print("3️⃣ Testing Concurrent Users...")
    result3 = await tester.test_concurrent_users(
        TEST_CONFIG['concurrent_users'], 
        TEST_CONFIG['tasks_per_user']
    )
    print(f"   Result: {result3.get('success_rate', 0):.2f}% success rate\n")
    
    return tester.test_results

async def run_comprehensive_test():
    """Run comprehensive test suite."""
    tester = BotTester()
    
    print("🚀 Running comprehensive test suite...\n")
    results = await tester.run_all_tests()
    
    return results

def print_test_summary(results):
    """Print test summary."""
    if not results:
        print("❌ No test results available")
        return
    
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    total_tests = len(results)
    successful_tests = sum(1 for result in results if 'error' not in result)
    failed_tests = total_tests - successful_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Success Rate: {(successful_tests/total_tests)*100:.2f}%")
    
    print("\n📈 Performance Metrics:")
    for i, result in enumerate(results, 1):
        if 'error' not in result:
            print(f"  Test {i} ({result.get('test_name', 'Unknown')}):")
            print(f"    - Success Rate: {result.get('success_rate', 0):.2f}%")
            print(f"    - Total Time: {result.get('total_time', 0):.2f}s")
            if 'average_time_per_task' in result:
                print(f"    - Avg Time per Task: {result['average_time_per_task']:.2f}s")
            if 'average_time_per_message' in result:
                print(f"    - Avg Time per Message: {result['average_time_per_message']:.2f}s")
            if 'average_time_per_interaction' in result:
                print(f"    - Avg Time per Interaction: {result['average_time_per_interaction']:.2f}s")
        else:
            print(f"  Test {i}: ❌ {result['error']}")
    
    print("\n" + "="*60)

async def main():
    """Main test function."""
    print_test_banner()
    setup_test_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Run comprehensive test suite
        results = await run_comprehensive_test()
        
        # Print summary
        print_test_summary(results)
        
        # Check if all tests passed
        failed_tests = sum(1 for result in results if 'error' in result)
        if failed_tests == 0:
            print("🎉 All tests passed successfully!")
            return 0
        else:
            print(f"⚠️  {failed_tests} test(s) failed")
            return 1
            
    except Exception as e:
        print(f"❌ Test suite failed with error: {e}")
        logger.error(f"Test suite failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)