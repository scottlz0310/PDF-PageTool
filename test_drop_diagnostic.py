#!/usr/bin/env python3
"""
ドラッグ&ドロップ問題診断スクリプト
"""

import sys
import os
from pathlib import Path

# プロジェクトのパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from src.utils.logger import get_logger

class TestDropWindow(QMainWindow):
    """ドラッグ&ドロップテスト用の簡単なウィンドウ"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger("TestDropWindow", "DEBUG")
        
        self.setWindowTitle("ドラッグ&ドロップテスト")
        self.setGeometry(100, 100, 600, 400)
        
        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        self.label = QLabel("PDFファイルをここにドラッグ&ドロップしてください")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                padding: 50px;
                font-size: 16px;
                background-color: #f9f9f9;
            }
        """)
        layout.addWidget(self.label)
        
        # ドロップ受け入れを有効化
        self.setAcceptDrops(True)
        self.logger.info("Test window initialized with drop support")
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """ドラッグエンター時の処理"""
        self.logger.info("=== dragEnterEvent called ===")
        
        try:
            mime_data = event.mimeData()
            if mime_data is None:
                self.logger.error("mimeData is None!")
                event.ignore()
                return
            
            self.logger.info(f"mimeData available: {mime_data}")
            self.logger.info(f"Has URLs: {mime_data.hasUrls()}")
            self.logger.info(f"Has text: {mime_data.hasText()}")
            self.logger.info(f"Formats: {mime_data.formats()}")
            
            if mime_data.hasUrls():
                urls = mime_data.urls()
                self.logger.info(f"Number of URLs: {len(urls)}")
                
                pdf_count = 0
                for i, url in enumerate(urls):
                    self.logger.info(f"URL {i}: {url.toString()}")
                    self.logger.info(f"  isLocalFile: {url.isLocalFile()}")
                    
                    if url.isLocalFile():
                        file_path = url.toLocalFile()
                        self.logger.info(f"  Local path: {file_path}")
                        self.logger.info(f"  File exists: {Path(file_path).exists()}")
                        self.logger.info(f"  Is PDF: {file_path.lower().endswith('.pdf')}")
                        
                        if file_path.lower().endswith('.pdf'):
                            pdf_count += 1
                
                if pdf_count > 0:
                    self.logger.info(f"Found {pdf_count} PDF files - ACCEPTING drop")
                    event.acceptProposedAction()
                    self.label.setText(f"PDFファイル{pdf_count}個をドロップできます！")
                    self.label.setStyleSheet("""
                        QLabel {
                            border: 2px dashed #4CAF50;
                            padding: 50px;
                            font-size: 16px;
                            background-color: #E8F5E8;
                            color: #2E7D32;
                        }
                    """)
                else:
                    self.logger.warning("No PDF files found - REJECTING drop")
                    event.ignore()
                    self.label.setText("PDFファイルではありません")
                    self.label.setStyleSheet("""
                        QLabel {
                            border: 2px dashed #f44336;
                            padding: 50px;
                            font-size: 16px;
                            background-color: #FFEBEE;
                            color: #C62828;
                        }
                    """)
            else:
                self.logger.warning("No URLs in mimeData - REJECTING drop")
                event.ignore()
                
        except Exception as e:
            self.logger.error(f"Exception in dragEnterEvent: {e}")
            event.ignore()
    
    def dragLeaveEvent(self, event):
        """ドラッグリーブ時の処理"""
        self.logger.info("dragLeaveEvent called")
        self.label.setText("PDFファイルをここにドラッグ&ドロップしてください")
        self.label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                padding: 50px;
                font-size: 16px;
                background-color: #f9f9f9;
            }
        """)
    
    def dropEvent(self, event: QDropEvent):
        """ドロップ時の処理"""
        self.logger.info("=== dropEvent called ===")
        
        try:
            mime_data = event.mimeData()
            if mime_data is None:
                self.logger.error("mimeData is None in dropEvent!")
                event.ignore()
                return
            
            pdf_files = []
            for url in mime_data.urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if file_path.lower().endswith('.pdf'):
                        pdf_files.append(file_path)
            
            if pdf_files:
                self.logger.info(f"Successfully dropped {len(pdf_files)} PDF files:")
                for pdf_file in pdf_files:
                    self.logger.info(f"  - {pdf_file}")
                
                event.acceptProposedAction()
                self.label.setText(f"成功！{len(pdf_files)}個のPDFファイルをドロップしました")
                self.label.setStyleSheet("""
                    QLabel {
                        border: 2px solid #4CAF50;
                        padding: 50px;
                        font-size: 16px;
                        background-color: #C8E6C9;
                        color: #1B5E20;
                    }
                """)
            else:
                self.logger.warning("No valid PDF files in dropEvent")
                event.ignore()
                
        except Exception as e:
            self.logger.error(f"Exception in dropEvent: {e}")
            event.ignore()

def main():
    app = QApplication(sys.argv)
    
    logger = get_logger("DropDiagnostic", "DEBUG")
    logger.info("=== ドラッグ&ドロップ診断開始 ===")
    
    window = TestDropWindow()
    window.show()
    
    logger.info("テストウィンドウが表示されました")
    logger.info("PDFファイルをウィンドウにドラッグ&ドロップしてテストしてください")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
