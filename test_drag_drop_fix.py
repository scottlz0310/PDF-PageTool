#!/usr/bin/env python3
"""
PDF-PageTool ドラッグ&ドロップ機能テスト

修正1: ファイルドロップ機能の改善テスト
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.logger import get_logger

def test_drag_drop_fix():
    """ドラッグ&ドロップ修正のテスト"""
    logger = get_logger("DragDropTest", "DEBUG")
    logger.info("=== ドラッグ&ドロップ修正テスト開始 ===")
    
    try:
        # PyQt6アプリケーションの初期化
        from PyQt6.QtWidgets import QApplication
        app = QApplication(sys.argv)
        
        # メインウィンドウの作成
        from src.ui.main_window import MainWindow
        window = MainWindow()
        
        # ウィンドウを表示
        window.show()
        logger.info("アプリケーションが起動しました")
        logger.info("ファイルドロップ機能をテストしてください：")
        logger.info("1. エクスプローラーからPDFファイルをドラッグ")
        logger.info("2. アプリケーションウィンドウにドロップ")
        logger.info("3. ファイルが正常に読み込まれるかを確認")
        
        # イベントループ開始
        return app.exec()
        
    except Exception as e:
        logger.error(f"テスト中にエラーが発生: {e}")
        return 1

if __name__ == "__main__":
    exit_code = test_drag_drop_fix()
    sys.exit(exit_code)
