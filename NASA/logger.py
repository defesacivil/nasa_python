import logging
from datetime import datetime

class Logger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def info(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [INFO] {message}")
        
    def error(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [ERROR] {message}")
        
    def debug(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [DEBUG] {message}")
        
    def warning(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [WARNING] {message}")

# Instância global do logger
logger = Logger()
