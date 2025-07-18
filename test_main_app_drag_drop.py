#!/usr/bin/env python3
"""
メインアプリケーションでのドラッグ&ドロップテスト
"""

import sys
import os
from pathlib import Path

# プロジェクトのパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.utils.logger import get_logger

def test_main_app_drag_drop():
    """メインアプリケーションでのドラッグ&ドロップテスト"""
    app = QApplication(sys.argv)
    
    logger = get_logger("MainAppDragDropTest", "INFO")
    logger.info("=== メインアプリケーション ドラッグ&ドロップテスト開始 ===")
    
    # メインウィンドウを作成（INFOログレベルで確実にログが出力される）
    main_window = MainWindow(log_level="INFO")
    main_window.show()
    
    logger.info("メインアプリケーションが起動しました")
    logger.info("ドラッグ&ドロップの状態:")
    logger.info(f"  Main window acceptDrops: {main_window.acceptDrops()}")
    
    # 子ウィジェットのドロップ状態も確認
    if hasattr(main_window.ui, 'scrollAreaInputs'):
        logger.info(f"  scrollAreaInputs acceptDrops: {main_window.ui.scrollAreaInputs.acceptDrops()}")
    if hasattr(main_window.ui, 'scrollAreaWidgetInputs'):
        logger.info(f"  scrollAreaWidgetInputs acceptDrops: {main_window.ui.scrollAreaWidgetInputs.acceptDrops()}")
    
    logger.info("=== テスト手順 ===")
    logger.info("1. エクスプローラーでPDFファイルを選択")
    logger.info("2. PDFファイルをメインウィンドウにドラッグ")
    logger.info("3. dragEnterEventのログを確認")
    logger.info("4. ドロップしてdropEventのログを確認")
    logger.info("5. テスト終了時はウィンドウを閉じてください")
    
    # アプリケーションを実行
    sys.exit(app.exec())

if __name__ == "__main__":
    test_main_app_drag_drop()
