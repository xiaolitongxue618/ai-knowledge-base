"""
日志配置模块
"""

from loguru import logger
import sys
from pathlib import Path


def setup_logger(log_file: str = "./logs/app.log", log_level: str = "INFO"):
    """
    配置日志系统

    Args:
        log_file: 日志文件路径
        log_level: 日志级别
    """
    # 移除默认处理器
    logger.remove()

    # 控制台输出
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True
    )

    # 文件输出
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger.add(
        log_file,
        rotation="500 MB",
        retention="10 days",
        level="DEBUG",
        encoding="utf-8"
    )

    logger.info(f"日志系统初始化完成，级别: {log_level}")


# 导出 logger 实例
__all__ = ["logger", "setup_logger"]
