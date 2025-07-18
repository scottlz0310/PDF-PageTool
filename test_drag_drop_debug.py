#!/usr/bin/env python3
"""
ドラッグ&ドロップ詳細デバッグテスト
"""

import sys
import os
from pathlib import Path

# プロジェクトのパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from src.ui.main_window import MainWindow
from src.utils.logger import get_logger

def test_drag_drop_debug():
    """ドラッグ&ドロップの詳細デバッグテスト"""
    app = QApplication(sys.argv)
    
    logger = get_logger("DragDropDebugTest", "DEBUG")
    logger.info("=== ドラッグ&ドロップ詳細デバッグテスト開始 ===")
    
    # メインウィンドウを作成（強制的にDEBUGログレベル）
    main_window = MainWindow(log_level="DEBUG")
    main_window.show()
    
    # ウィンドウのドロップ設定を再確認
    logger.info(f"Main window accepts drops: {main_window.acceptDrops()}")
    
    # 定期的にドラッグ&ドロップの状態をチェック
    def check_status():
        logger.debug("ドラッグ&ドロップ待機中...")
        
    timer = QTimer()
    timer.timeout.connect(check_status)
    timer.start(5000)  # 5秒ごと
    
    logger.info("=== テスト手順 ===")
    logger.info("1. エクスプローラーでPDFファイルを選択")
    logger.info("2. PDFファイルをこのウィンドウにドラッグ")
    logger.info("3. ドロップしてください")
    logger.info("4. デバッグログでイベントを確認")
    logger.info("5. テスト終了時はウィンドウを閉じてください")
    
    # アプリケーションを実行
    sys.exit(app.exec())

if __name__ == "__main__":
    test_drag_drop_debug()
