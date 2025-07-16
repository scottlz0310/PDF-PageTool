"""
PDF-PageTool Logger Module

高機能なロガーシステムを提供し、Debug、Verbose、Default(Silent)レベルでの
ログ出力をサポートします。
"""

import logging
import colorlog
import os
from datetime import datetime
from pathlib import Path


class PDFPageToolLogger:
    """PDF-PageTool専用ロガークラス"""
    
    def __init__(self, name: str = "PDF-PageTool", log_level: str = "WARNING"):
        """
        ロガーを初期化します
        
        Args:
            name: ロガー名
            log_level: ログレベル ("DEBUG", "VERBOSE", "INFO", "WARNING", "ERROR")
                      デフォルトはWARNING（警告以上のみ表示）
        """
        self.logger = logging.getLogger(name)
        self.log_level = log_level.upper()
        self._setup_logger()
        
    def _setup_logger(self):
        """ロガーの設定を行います"""
        # 既存のハンドラーをクリア
        self.logger.handlers.clear()
        
        # ログレベルの設定
        if self.log_level == "VERBOSE":
            level = logging.DEBUG
        elif self.log_level == "DEBUG":
            level = logging.DEBUG
        elif self.log_level == "INFO":
            level = logging.INFO
        elif self.log_level == "WARNING":
            level = logging.WARNING
        elif self.log_level == "ERROR":
            level = logging.ERROR
        else:
            level = logging.INFO
            
        self.logger.setLevel(level)
        
        # コンソールハンドラーの設定（カラーログ対応）
        console_handler = colorlog.StreamHandler()
        console_format = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # ファイルハンドラーの設定（デバッグモード時のみ）
        if self.log_level in ["DEBUG", "VERBOSE"]:
            log_dir = Path(__file__).parent.parent.parent / "debug"
            log_dir.mkdir(exist_ok=True)
            
            log_file = log_dir / f"pdf_pagetool_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """デバッグメッセージをログ出力"""
        self.logger.debug(message)
    
    def verbose(self, message: str):
        """詳細メッセージをログ出力（DEBUGレベルとして扱う）"""
        self.logger.debug(f"[VERBOSE] {message}")
    
    def info(self, message: str):
        """情報メッセージをログ出力"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """警告メッセージをログ出力"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """エラーメッセージをログ出力"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """重大なエラーメッセージをログ出力"""
        self.logger.critical(message)


def get_logger(name: str = "PDF-PageTool", log_level: str | None = None) -> PDFPageToolLogger:
    """
    ロガーインスタンスを取得します
    
    Args:
        name: ロガー名
        log_level: ログレベル（環境変数LOG_LEVELが優先、デフォルトはWARNING）
    
    Returns:
        PDFPageToolLoggerインスタンス
    """
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "WARNING")  # デフォルトをWARNINGに変更
    
    return PDFPageToolLogger(name, log_level)


# モジュールレベルでの使用例
if __name__ == "__main__":
    # テスト用
    logger = get_logger(log_level="DEBUG")
    
    logger.info("PDF-PageTool Logger initialized")
    logger.debug("This is a debug message")
    logger.verbose("This is a verbose message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
