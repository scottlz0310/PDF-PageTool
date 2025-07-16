"""
PDF Operations Module

PDFファイルの読み込み、ページ抽出、結合、回転などの基本操作を提供します。
"""

import os
from pathlib import Path
from typing import List, Tuple
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
from PIL import Image
import tempfile

from ..utils.logger import get_logger


class PDFPageInfo:
    """PDFページの情報を保持するクラス"""
    
    def __init__(self, source_file: str, page_number: int, rotation: int = 0):
        """
        PDFページ情報を初期化
        
        Args:
            source_file: ソースPDFファイルのパス
            page_number: ページ番号（0始まり）
            rotation: 回転角度（0, 90, 180, 270）
        """
        self.source_file = source_file
        self.page_number = page_number
        self.rotation = rotation
        self.thumbnail_path: str | None = None
    
    def __str__(self):
        return f"Page {self.page_number + 1} from {Path(self.source_file).name}"


class PDFOperations:
    """PDF操作の主要クラス"""
    
    def __init__(self, log_level: str = "INFO"):
        """
        PDF操作クラスを初期化
        
        Args:
            log_level: ログレベル
        """
        self.logger = get_logger("PDFOperations", log_level)
        self.temp_dir = None
        self._create_temp_dir()
    
    def _create_temp_dir(self):
        """一時ディレクトリを作成"""
        try:
            self.temp_dir = tempfile.mkdtemp(prefix="pdf_pagetool_")
            self.logger.debug(f"Created temporary directory: {self.temp_dir}")
        except Exception as e:
            self.logger.error(f"Failed to create temporary directory: {e}")
            raise
    
    def load_pdf(self, file_path: str) -> List[PDFPageInfo]:
        """
        PDFファイルを読み込み、ページ情報のリストを返す
        
        Args:
            file_path: PDFファイルのパス
            
        Returns:
            PDFPageInfoのリスト
        """
        try:
            self.logger.info(f"Loading PDF file: {file_path}")
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"PDF file not found: {file_path}")
            
            # PyPDF2でページ数を取得
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                page_count = len(reader.pages)
            
            self.logger.info(f"PDF has {page_count} pages")
            
            # 各ページの情報を作成
            pages = []
            for i in range(page_count):
                page_info = PDFPageInfo(file_path, i)
                pages.append(page_info)
            
            return pages
            
        except Exception as e:
            self.logger.error(f"Failed to load PDF: {e}")
            raise
    
    def generate_thumbnail(self, page_info: PDFPageInfo, size: Tuple[int, int] = (150, 200)) -> str:
        """
        PDFページのサムネイルを生成
        
        Args:
            page_info: PDFページ情報
            size: サムネイルサイズ (width, height)
            
        Returns:
            サムネイル画像ファイルのパス
        """
        try:
            self.logger.debug(f"Generating thumbnail for {page_info}")
            
            # サムネイルが既に生成済みの場合はそのパスを返す
            if page_info.thumbnail_path and os.path.exists(page_info.thumbnail_path):
                return page_info.thumbnail_path
            
            # pdf2imageを使用してページを画像に変換
            images = convert_from_path(
                page_info.source_file,
                first_page=page_info.page_number + 1,
                last_page=page_info.page_number + 1,
                dpi=100
            )
            
            if not images:
                raise ValueError("Failed to convert PDF page to image")
            
            image = images[0]
            
            # 回転を適用
            if page_info.rotation != 0:
                image = image.rotate(-page_info.rotation, expand=True)
            
            # サムネイルサイズにリサイズ
            image.thumbnail(size, Image.Resampling.LANCZOS)
            
            # 一時ファイルに保存
            thumbnail_filename = f"thumb_{Path(page_info.source_file).stem}_p{page_info.page_number + 1}.png"
            if self.temp_dir is None:
                raise RuntimeError("Temporary directory not initialized")
            thumbnail_path = os.path.join(self.temp_dir, thumbnail_filename)
            image.save(thumbnail_path, "PNG")
            
            page_info.thumbnail_path = thumbnail_path
            self.logger.debug(f"Thumbnail saved: {thumbnail_path}")
            
            return thumbnail_path
            
        except Exception as e:
            self.logger.error(f"Failed to generate thumbnail: {e}")
            raise
    
    def rotate_page(self, page_info: PDFPageInfo, angle: int):
        """
        ページの回転角度を設定
        
        Args:
            page_info: PDFページ情報
            angle: 回転角度（90の倍数）
        """
        if angle not in [0, 90, 180, 270]:
            raise ValueError("Rotation angle must be 0, 90, 180, or 270 degrees")
        
        page_info.rotation = angle
        # サムネイルを再生成するためにパスをクリア
        page_info.thumbnail_path = None
        
        self.logger.debug(f"Page rotation set to {angle} degrees for {page_info}")
    
    def merge_pages(self, pages: List[PDFPageInfo], output_path: str):
        """
        指定されたページを結合してPDFファイルを作成
        
        Args:
            pages: 結合するページのリスト
            output_path: 出力PDFファイルのパス
        """
        try:
            self.logger.info(f"Merging {len(pages)} pages to {output_path}")
            
            writer = PdfWriter()
            
            for page_info in pages:
                self.logger.debug(f"Adding {page_info}")
                
                # ソースPDFを読み込み
                with open(page_info.source_file, 'rb') as file:
                    reader = PdfReader(file)
                    page = reader.pages[page_info.page_number]
                    
                    # 回転を適用
                    if page_info.rotation != 0:
                        page.rotate(page_info.rotation)
                    
                    writer.add_page(page)
            
            # 出力ファイルに書き込み
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            self.logger.info(f"Successfully merged PDF: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to merge PDF: {e}")
            raise
    
    def cleanup(self):
        """一時ファイルをクリーンアップ"""
        try:
            if self.temp_dir and os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
                self.logger.debug(f"Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            self.logger.warning(f"Failed to cleanup temporary directory: {e}")


# モジュールテスト用
if __name__ == "__main__":
    # テスト用コード
    pdf_ops = PDFOperations(log_level="DEBUG")
    print("PDF Operations module initialized successfully")
