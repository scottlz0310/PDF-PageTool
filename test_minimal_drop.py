#!/usr/bin/env python3
"""
最小限のドラッグ&ドロップテスト - 他の要因を排除
"""

import sys
from pathlib import Path

# プロジェクトのパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

class MinimalDropWindow(QMainWindow):
    """最小限のドラッグ&ドロップテストウィンドウ"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("最小限ドラッグ&ドロップテスト")
        self.setGeometry(200, 200, 500, 300)
        
        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        self.label = QLabel("PDFファイルをドラッグ&ドロップしてください")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                padding: 30px;
                font-size: 14px;
                background-color: #f5f5f5;
            }
        """)
        layout.addWidget(self.label)
        
        # ドロップ受け入れを有効化（メインウィンドウレベルのみ）
        self.setAcceptDrops(True)
        
        # 子ウィジェットではドロップを無効化
        central_widget.setAcceptDrops(False)
        self.label.setAcceptDrops(False)
        
        print(f"Main window acceptDrops: {self.acceptDrops()}")
        print(f"Central widget acceptDrops: {central_widget.acceptDrops()}")
        print(f"Label acceptDrops: {self.label.acceptDrops()}")
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """ドラッグエンター時の処理"""
        print("=== dragEnterEvent called ===")
        
        try:
            mime_data = event.mimeData()
            if mime_data is None:
                print("ERROR: mimeData is None!")
                event.ignore()
                return
            
            print(f"mimeData: {mime_data}")
            print(f"Has URLs: {mime_data.hasUrls()}")
            print(f"Formats: {mime_data.formats()}")
            
            if mime_data.hasUrls():
                urls = mime_data.urls()
                print(f"Number of URLs: {len(urls)}")
                
                pdf_count = 0
                for i, url in enumerate(urls):
                    print(f"URL {i}: {url.toString()}")
                    if url.isLocalFile():
                        file_path = url.toLocalFile()
                        print(f"  Local path: {file_path}")
                        if file_path.lower().endswith('.pdf'):
                            pdf_count += 1
                
                if pdf_count > 0:
                    print(f"ACCEPTING drop of {pdf_count} PDF files")
                    event.acceptProposedAction()
                    self.label.setText(f"✅ {pdf_count}個のPDFファイルをドロップできます")
                    self.label.setStyleSheet("""
                        QLabel {
                            border: 2px dashed #4CAF50;
                            padding: 30px;
                            font-size: 14px;
                            background-color: #E8F5E8;
                            color: #2E7D32;
                        }
                    """)
                else:
                    print("REJECTING: No PDF files")
                    event.ignore()
                    self.label.setText("❌ PDFファイルではありません")
                    self.label.setStyleSheet("""
                        QLabel {
                            border: 2px dashed #f44336;
                            padding: 30px;
                            font-size: 14px;
                            background-color: #FFEBEE;
                            color: #C62828;
                        }
                    """)
            else:
                print("REJECTING: No URLs in mimeData")
                event.ignore()
                
        except Exception as e:
            print(f"Exception in dragEnterEvent: {e}")
            event.ignore()
    
    def dragLeaveEvent(self, event):
        """ドラッグリーブ時の処理"""
        print("dragLeaveEvent called")
        self.label.setText("PDFファイルをドラッグ&ドロップしてください")
        self.label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                padding: 30px;
                font-size: 14px;
                background-color: #f5f5f5;
            }
        """)
    
    def dropEvent(self, event: QDropEvent):
        """ドロップ時の処理"""
        print("=== dropEvent called ===")
        
        try:
            mime_data = event.mimeData()
            if mime_data is None:
                print("ERROR: mimeData is None in dropEvent!")
                event.ignore()
                return
            
            pdf_files = []
            for url in mime_data.urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if file_path.lower().endswith('.pdf'):
                        pdf_files.append(file_path)
            
            if pdf_files:
                print(f"SUCCESS: Dropped {len(pdf_files)} PDF files:")
                for pdf_file in pdf_files:
                    print(f"  - {pdf_file}")
                
                event.acceptProposedAction()
                self.label.setText(f"🎉 成功！{len(pdf_files)}個のPDFファイルをドロップしました")
                self.label.setStyleSheet("""
                    QLabel {
                        border: 2px solid #4CAF50;
                        padding: 30px;
                        font-size: 14px;
                        background-color: #C8E6C9;
                        color: #1B5E20;
                    }
                """)
            else:
                print("ERROR: No valid PDF files in dropEvent")
                event.ignore()
                
        except Exception as e:
            print(f"Exception in dropEvent: {e}")
            event.ignore()

def main():
    app = QApplication(sys.argv)
    
    print("=== 最小限ドラッグ&ドロップテスト開始 ===")
    
    window = MinimalDropWindow()
    window.show()
    
    print("テストウィンドウが表示されました")
    print("PDFファイルをドラッグ&ドロップしてテストしてください")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
