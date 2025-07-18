#!/usr/bin/env python3
"""
ファイル読み込み機能の基本テスト
"""

import sys
import os
from pathlib import Path

# プロジェクトのパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.utils.logger import get_logger

def test_file_loading():
    """ファイル読み込み機能の基本テスト"""
    app = QApplication(sys.argv)
    
    logger = get_logger("FileLoadingTest", "INFO")
    logger.info("=== ファイル読み込み機能テスト開始 ===")
    
    # メインウィンドウを作成
    main_window = MainWindow(log_level="DEBUG")
    main_window.show()
    
    # テスト用PDFファイルのパスをチェック
    test_pdf_files = [
        "idea/TEST_PDF1.pdf",
        "idea/TEST_PDF2.pdf",
        "test_output.pdf"
    ]
    
    existing_files = []
    for pdf_file in test_pdf_files:
        full_path = Path(pdf_file)
        if full_path.exists():
            existing_files.append(str(full_path.absolute()))
            logger.info(f"テストファイル確認: {full_path}")
        else:
            logger.warning(f"テストファイル未発見: {full_path}")
    
    if existing_files:
        logger.info(f"見つかったファイル: {len(existing_files)}個")
        # ファイル読み込みテスト
        try:
            main_window.load_pdf_files(existing_files)
            logger.info("ファイル読み込み処理を開始しました")
        except Exception as e:
            logger.error(f"ファイル読み込みエラー: {e}")
    else:
        logger.info("テスト用PDFファイルが見つかりません")
        logger.info("ドラッグ&ドロップでファイルを追加してテストしてください")
    
    logger.info("ウィンドウが表示されました。ドラッグ&ドロップをテストしてください")
    logger.info("テスト終了時はウィンドウを閉じてください")
    
    # アプリケーションを実行
    sys.exit(app.exec())

if __name__ == "__main__":
    test_file_loading()
