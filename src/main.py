#!/usr/bin/env python3
"""
PDF-PageTool Main Application

PDFページの抽出・結合ツールのメインエントリーポイントです。
コマンドライン引数からPDFファイルを受け取り、GUIアプリケーションを起動します。
"""

import argparse
import os
import sys
from pathlib import Path

from src.pdf_operations import PDFOperations
from src.utils.logger import get_logger

# プロジェクトルートのパスを取得
project_root = Path(__file__).parent.parent


def parse_arguments() -> argparse.Namespace:
    """コマンドライン引数を解析"""
    parser = argparse.ArgumentParser(
        description="PDF-PageTool: PDFページ抽出・結合ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  main.py file1.pdf file2.pdf
  main.py --log-level DEBUG file.pdf
  main.py --version
        """,
    )

    parser.add_argument("files", nargs="*", help="処理するPDFファイル（複数指定可能）")

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "VERBOSE", "INFO", "WARNING", "ERROR"],
        default="WARNING",
        help="ログレベルを設定（デフォルト: WARNING - 警告以上のみ表示）",
    )

    parser.add_argument("--version", action="version", version="PDF-PageTool 0.1.0")

    parser.add_argument("--test-mode", action="store_true", help="テストモードで起動（GUI無し）")

    return parser.parse_args()


def validate_pdf_files(file_paths: list[str]) -> list[str]:
    """PDFファイルの存在確認と検証"""
    valid_files: list[str] = []

    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"エラー: ファイルが見つかりません: {file_path}", file=sys.stderr)
            continue

        if not file_path.lower().endswith(".pdf"):
            print(f"警告: PDFファイルではありません: {file_path}", file=sys.stderr)
            continue

        valid_files.append(file_path)

    return valid_files


def test_mode(pdf_files: list[str], log_level: str) -> bool:
    """テストモード：基本機能のテスト"""
    logger = get_logger("TestMode", log_level)
    logger.info("テストモードで起動しました")

    if not pdf_files:
        logger.info("テスト用サンプルファイルが必要です")
        return False

    try:
        # PDF操作のテスト
        pdf_ops = PDFOperations(log_level)

        for pdf_file in pdf_files:
            logger.info(f"PDFファイルをテスト中: {pdf_file}")
            pages = pdf_ops.load_pdf(pdf_file)
            logger.info(f"  ページ数: {len(pages)}")

            # 最初のページのサムネイル生成テスト
            if pages:
                thumbnail_path = pdf_ops.generate_thumbnail(pages[0])
                logger.info(f"  サムネイル生成成功: {thumbnail_path}")

        pdf_ops.cleanup()
        logger.info("テスト完了")

    except Exception as e:
        logger.error(f"テスト中にエラーが発生しました: {e}")
        return False

    return True


def main() -> int:
    """メイン関数"""
    args = parse_arguments()

    # ログレベルを環境変数として設定
    os.environ["LOG_LEVEL"] = args.log_level

    logger = get_logger("PDF-PageTool", args.log_level)
    logger.info("PDF-PageTool を起動しています...")

    # PDFファイルの検証
    valid_files = validate_pdf_files(args.files)

    # ファイルがない場合でも引数なし起動を許可
    if not valid_files and not args.test_mode:
        logger.info("引数なしで起動しました。後でファイルを追加できます。")

    # テストモードの場合
    if args.test_mode:
        if not valid_files:
            logger.error("テストモードにはPDFファイルが必要です")
            return 1
        logger.info("テストモードで実行中...")
        success = test_mode(valid_files, args.log_level)
        return 0 if success else 1

    # 通常モード：GUIアプリケーションを起動
    try:
        logger.info("GUIアプリケーションを初期化中...")

        # PyQt6アプリケーションを初期化
        from PyQt6.QtGui import QIcon
        from PyQt6.QtWidgets import QApplication

        from src.ui import create_main_window

        app = QApplication(sys.argv)
        app.setApplicationName("PDF-PageTool")
        app.setApplicationVersion("0.1.0")

        # アプリケーションアイコンを設定
        icon_path = project_root / "asset" / "pdf-tool.ico"
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
            logger.debug(f"Application icon set: {icon_path}")
        else:
            logger.warning(f"Icon file not found: {icon_path}")

        # メインウィンドウを作成・表示
        main_window = create_main_window(valid_files, args.log_level)
        main_window.show()

        logger.info("GUIアプリケーションを起動しました")

        # イベントループを開始
        exit_code: int = app.exec()
        return exit_code

    except KeyboardInterrupt:
        logger.info("ユーザーによって中断されました")
        return 0
    except Exception as e:
        logger.error(f"予期しないエラーが発生しました: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
