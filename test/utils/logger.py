import logging

logger = logging.getLogger("MyPlayerLogger")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Format
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
)
console_handler.setFormatter(formatter)

# Avoid duplicate handlers
if not logger.handlers:
    logger.addHandler(console_handler)
