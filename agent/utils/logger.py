import os
import sys
from datetime import datetime

try:
    from loguru import logger as _logger

    def setup_logger(log_dir="debug/custom", console_level="INFO"):
        """设置 loguru logger

        Args:
            log_dir: 日志文件目录
            console_level: 控制台输出等级 (DEBUG, INFO, WARNING, ERROR)
        """
        os.makedirs(log_dir, exist_ok=True)
        _logger.remove()

        _logger.add(
            sys.stderr,
            format="[<level>{level}</level>] <level>{message}</level>",
            colorize=True,
            level=console_level,
        )
        _logger.add(
            f"{log_dir}/{{time:YYYY-MM-DD}}.log",
            rotation="00:00",  # midnight
            retention="2 weeks",
            compression="zip",
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
            encoding="utf-8",
            enqueue=True,
            backtrace=True,  # 包含完整的异常回溯信息
            diagnose=True,  # 包含变量值信息
        )
        return _logger

    def change_console_level(level="DEBUG"):
        """动态修改控制台日志等级"""
        setup_logger(console_level=level)
        _logger.info(f"控制台日志等级已更改为: {level}")

    logger = setup_logger()
except ImportError:
    import logging
    import sys
    import os
    
    # 配置logging模块，使其接口与loguru尽可能一致
    class LoggerAdapter(logging.LoggerAdapter):
        def exception(self, msg, *args, **kwargs):
            self.error(msg + "\n" + kwargs.get('exc_info', True), exc_info=True)
        
        def debug(self, msg, *args, **kwargs):
            self.log(logging.DEBUG, msg, *args, **kwargs)
    
    # 设置日志格式
    logger = logging.getLogger('M9A')
    logger.setLevel(logging.INFO)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('[%(levelname)s] %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器
    log_dir = "debug/custom"
    os.makedirs(log_dir, exist_ok=True)
    file_handler = logging.FileHandler(f"{log_dir}/{datetime.now().strftime('%Y-%m-%d')}.log")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
                                     datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # 创建适配器使接口更兼容
    logger = LoggerAdapter(logger, {})
