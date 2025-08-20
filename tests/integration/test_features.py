#!/usr/bin/env python3
"""
PDF-PageTool 機能テストスクリプト

基本的な操作をプログラムで実行して機能を確認します。
"""

import os
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.pdf_operations import PDFOperations
from src.utils.logger import get_logger


def test_pdf_merge():
    """PDF結合機能のテスト"""
    logger = get_logger("PDFMergeTest", "DEBUG")
    logger.info("PDF結合機能のテストを開始します")

    try:
        # PDF操作クラスを初期化
        pdf_ops = PDFOperations("DEBUG")

        # テストファイルを読み込み
        test_files = ["idea/TEST_PDF1.pdf", "idea/TEST_PDF2.pdf"]
        all_pages = []

        for test_file in test_files:
            if os.path.exists(test_file):
                logger.info(f"読み込み中: {test_file}")
                pages = pdf_ops.load_pdf(test_file)
                logger.info(f"  ページ数: {len(pages)}")

                # 各ページのサムネイルを生成
                for page in pages:
                    thumbnail_path = pdf_ops.generate_thumbnail(page)
                    logger.info(f"  サムネイル: {thumbnail_path}")

                all_pages.extend(pages)
            else:
                logger.warning(f"ファイルが見つかりません: {test_file}")

        if not all_pages:
            logger.error("テストファイルが見つかりません")
            return False

        # 結合用のページリストを作成（交互に選択）
        merge_pages = []

        # TEST_PDF1から1,3ページ目を選択
        pdf1_pages = [p for p in all_pages if "TEST_PDF1" in p.source_file]
        if len(pdf1_pages) >= 3:
            merge_pages.extend([pdf1_pages[0], pdf1_pages[2]])  # 1ページ目と3ページ目

        # TEST_PDF2から2,4ページ目を選択
        pdf2_pages = [p for p in all_pages if "TEST_PDF2" in p.source_file]
        if len(pdf2_pages) >= 4:
            merge_pages.extend([pdf2_pages[1], pdf2_pages[3]])  # 2ページ目と4ページ目

        logger.info(f"結合するページ数: {len(merge_pages)}")
        for i, page in enumerate(merge_pages):
            logger.info(f"  {i+1}: {page}")

        # 出力ファイル名
        output_file = "test_output.pdf"

        # PDF結合を実行
        logger.info(f"PDF結合を実行: {output_file}")
        pdf_ops.merge_pages(merge_pages, output_file)

        # 結果確認
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            logger.info(f"結合完了! ファイルサイズ: {file_size} bytes")

            # 結合されたファイルの確認
            merged_pages = pdf_ops.load_pdf(output_file)
            logger.info(f"結合されたPDFのページ数: {len(merged_pages)}")

            # クリーンアップ
            pdf_ops.cleanup()

            return True
        else:
            logger.error("出力ファイルが作成されませんでした")
            return False

    except Exception as e:
        logger.error(f"テスト中にエラーが発生: {e}")
        return False


def test_page_rotation():
    """ページ回転機能のテスト"""
    logger = get_logger("PageRotationTest", "DEBUG")
    logger.info("ページ回転機能のテストを開始します")

    try:
        pdf_ops = PDFOperations("DEBUG")

        # テストファイルを読み込み
        test_file = "idea/TEST_PDF1.pdf"
        if not os.path.exists(test_file):
            logger.error(f"テストファイルが見つかりません: {test_file}")
            return False

        pages = pdf_ops.load_pdf(test_file)
        if not pages:
            logger.error("ページが読み込めませんでした")
            return False

        # 最初のページを回転
        first_page = pages[0]
        logger.info(f"元の回転角度: {first_page.rotation}")

        # 90度回転
        pdf_ops.rotate_page(first_page, 90)
        logger.info(f"90度回転後: {first_page.rotation}")

        # さらに180度回転（合計270度）
        pdf_ops.rotate_page(first_page, 180)
        logger.info(f"180度追加回転後: {first_page.rotation}")

        # 回転後のサムネイル生成
        rotated_thumbnail = pdf_ops.generate_thumbnail(first_page)
        logger.info(f"回転後サムネイル: {rotated_thumbnail}")

        # 回転されたページを含むPDFを保存
        rotated_output = "test_rotated.pdf"
        pdf_ops.merge_pages([first_page], rotated_output)

        if os.path.exists(rotated_output):
            logger.info(f"回転テスト完了: {rotated_output}")
            pdf_ops.cleanup()
            return True
        else:
            logger.error("回転されたPDFの保存に失敗")
            return False

    except Exception as e:
        logger.error(f"回転テスト中にエラー: {e}")
        return False


def main():
    """メイン関数"""
    logger = get_logger("PDFPageToolTest", "INFO")
    logger.info("PDF-PageTool 機能テストを開始します")

    # テスト実行
    tests = [
        ("PDF結合機能", test_pdf_merge),
        ("ページ回転機能", test_page_rotation),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"テスト実行: {test_name}")
        logger.info(f"{'='*50}")

        try:
            if test_func():
                logger.info(f"✅ {test_name}: 成功")
                passed += 1
            else:
                logger.error(f"❌ {test_name}: 失敗")
        except Exception as e:
            logger.error(f"❌ {test_name}: 例外発生 - {e}")

    logger.info(f"\n{'='*50}")
    logger.info(f"テスト結果: {passed}/{total} 成功")
    logger.info(f"{'='*50}")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
