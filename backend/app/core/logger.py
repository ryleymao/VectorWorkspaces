import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName', 
                          'levelname', 'levelno', 'lineno', 'module', 'msecs', 
                          'message', 'pathname', 'process', 'processName', 'relativeCreated',
                          'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info']:
                log_data[key] = value
        
        return json.dumps(log_data)


def setup_logger(name: str = "enterprise_ai", level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    logger.handlers = []
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))
    formatter = JSONFormatter()
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger


logger = setup_logger("enterprise_ai", "INFO")
