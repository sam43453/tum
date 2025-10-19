# Parallel Reactions Telegram Bot

A high-performance Telegram bot that demonstrates parallel processing capabilities using Python's asyncio library. This bot can handle multiple concurrent reactions and user interactions simultaneously.

## 🚀 Features

- **Concurrent Message Processing**: Handle multiple messages simultaneously
- **Parallel Reaction Handling**: Process multiple reactions in parallel
- **Real-time Task Monitoring**: Track active tasks and performance metrics
- **Async/Await Implementation**: Modern Python async programming
- **Comprehensive Testing**: Full test suite with performance metrics

## 📋 Commands

- `/start` - Show welcome message and bot information
- `/parallel` - Start parallel processing demonstration
- `/reactions` - Show reaction statistics
- `/status` - Check bot status and active tasks
- `/stop` - Stop all active tasks for the user

## 🛠️ Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variable**:
   ```bash
   export TELEGRAM_BOT_TOKEN="your_bot_token_here"
   ```

3. **Run the Bot**:
   ```bash
   python run_bot.py
   ```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python run_tests.py
```

Or run individual tests:

```bash
python test_parallel_bot.py
```

## 📊 Test Scenarios

### 1. Parallel Processing Test
- Tests concurrent task execution
- Measures success rate and processing time
- Simulates multiple parallel operations

### 2. Reaction Processing Test
- Tests reaction handling for different message types
- Measures response time and accuracy
- Simulates real-world message processing

### 3. Concurrent Users Test
- Tests multiple users interacting simultaneously
- Measures system performance under load
- Simulates realistic usage patterns

## 🔧 Configuration

Edit `bot_config.py` to customize:

- **Bot Settings**: Token, logging, timeouts
- **Reaction Settings**: Emojis, trigger words
- **Test Settings**: Test parameters and limits

## 📈 Performance Metrics

The bot tracks and reports:

- **Success Rate**: Percentage of successful operations
- **Processing Time**: Time taken for each operation
- **Concurrent Performance**: Performance under load
- **Reaction Accuracy**: Correctness of reaction matching

## 🏗️ Architecture

```
parallel_reactions_bot.py    # Main bot implementation
├── ParallelReactionsBot     # Main bot class
├── async handlers          # Async message handlers
├── parallel processing     # Concurrent task management
└── reaction system         # Smart reaction matching

test_parallel_bot.py        # Test suite
├── BotTester              # Test framework
├── parallel tests         # Concurrent testing
├── performance metrics    # Benchmarking
└── comprehensive reports  # Detailed results

bot_config.py              # Configuration
├── bot settings          # Bot parameters
├── reaction config       # Reaction settings
└── test config          # Test parameters
```

## 🚀 Usage Examples

### Starting the Bot
```bash
# Set your bot token
export TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"

# Run the bot
python run_bot.py
```

### Running Tests
```bash
# Run all tests
python run_tests.py

# Run specific test
python -c "
import asyncio
from test_parallel_bot import BotTester

async def test():
    tester = BotTester()
    await tester.test_parallel_processing(5)
    print(tester.generate_test_report())

asyncio.run(test())
"
```

## 📝 Logs

- **Bot Logs**: `bot.log` - Bot operation logs
- **Test Logs**: `test_results.log` - Test execution logs
- **Console Output**: Real-time status and error messages

## 🔍 Troubleshooting

### Common Issues

1. **Token Not Found**:
   ```
   Error: TELEGRAM_BOT_TOKEN environment variable is required
   ```
   Solution: Set the environment variable with your bot token

2. **Import Errors**:
   ```
   ModuleNotFoundError: No module named 'telegram'
   ```
   Solution: Install dependencies with `pip install -r requirements.txt`

3. **Test Failures**:
   ```
   Test failed: Connection timeout
   ```
   Solution: Check network connectivity and bot token validity

### Debug Mode

Enable debug logging by modifying `bot_config.py`:
```python
LOGGING_CONFIG = {
    'level': 'DEBUG',  # Change from 'INFO' to 'DEBUG'
    # ... other settings
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error details
3. Create an issue with detailed information
4. Include test results and configuration

---

**Happy Botting! 🤖✨**