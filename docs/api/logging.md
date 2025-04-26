# Logging Utilities

nGPT provides logging utilities that help with debugging, tracing operations, and saving conversation history. These utilities are located in the `ngpt.utils.log` module.

## Overview

The logging utilities in nGPT provide a simple interface for creating loggers and logging messages at different levels of severity. The logging system is built on top of Python's built-in `logging` module, with some additional features specific to nGPT.

## Core Functions

### `create_logger`

```python
from ngpt.utils.log import create_logger

def create_logger(name=None, log_file=None, level=None):
```

Creates a logger instance with the specified name, file, and level.

**Parameters:**
- `name` (str, optional): The name of the logger. If None, uses a default name.
- `log_file` (str, optional): The file path to log messages to. If None, logs to console only.
- `level` (int, optional): The logging level. If None, uses INFO level.

**Returns:**
- `Logger`: A logger instance

**Example:**
```python
from ngpt.utils.log import create_logger

# Create a console logger
logger = create_logger()
logger.info("This is an info message")

# Create a file logger
file_logger = create_logger(log_file="conversation.log")
file_logger.info("This message will be logged to the file")

# Create a debug-level logger
debug_logger = create_logger(level="DEBUG")
debug_logger.debug("This debug message will be shown")
```

## Logger Class

The `Logger` class is a wrapper around Python's standard logging module with some additional features.

```python
from ngpt.utils.log import Logger

logger = Logger(name=None, log_file=None, level=None)
```

### Methods

#### `debug(message)`
Logs a message with DEBUG level.

#### `info(message)`
Logs a message with INFO level.

#### `warning(message)`
Logs a message with WARNING level.

#### `error(message)`
Logs a message with ERROR level.

#### `critical(message)`
Logs a message with CRITICAL level.

### Example

```python
from ngpt.utils.log import Logger

# Create a logger instance
logger = Logger(name="ngpt-client", log_file="client.log")

# Log messages at different levels
logger.debug("Detailed debugging information")
logger.info("General information about program execution")
logger.warning("Warning about a potential issue")
logger.error("Error that prevented an operation from completing")
logger.critical("Critical error that might cause the program to terminate")
```

## Log Levels

nGPT uses the standard Python logging levels:

| Level | Value | Description |
|-------|-------|-------------|
| DEBUG | 10 | Detailed information, typically of interest only when diagnosing problems |
| INFO | 20 | Confirmation that things are working as expected |
| WARNING | 30 | An indication that something unexpected happened, or indicative of some problem in the near future |
| ERROR | 40 | Due to a more serious problem, the software has not been able to perform some function |
| CRITICAL | 50 | A serious error, indicating that the program itself may be unable to continue running |

## Log Formatting

The default log format for nGPT includes:
- Timestamp
- Logger name
- Log level
- Message

Example of a formatted log message:
```
2023-08-15 14:30:45 - ngpt-client - INFO - Starting chat session
```

## Using Loggers with NGPTClient

The NGPTClient functions accept a logger parameter that can be used to log operations:

```python
from ngpt import NGPTClient, load_config
from ngpt.utils.log import create_logger

# Create a logger that writes to a file
logger = create_logger(log_file="chat_history.log")

# Initialize client
client = NGPTClient(**load_config())

# Use logger with chat method
response = client.chat(
    prompt="Tell me about quantum computing",
    stream=False,
    logger=logger  # Pass the logger here
)

# The prompt and response will be logged to chat_history.log
```

This is particularly useful for saving conversation history or for debugging API calls. 