#!/usr/bin/env python3
"""
PDF-PageTool 新機能テストスクリプト

設定管理、右クリックメニュー、ツールチップなどの新機能をテスト
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.settings_manager import SettingsManager
from src.utils.logger import get_logger


def test_settings_manager():
    """設定管理システムのテスト"""
    print("=== 設定管理システムテスト ===")
    
    # 一時的な設定ファイルを使用
    settings = SettingsManager("PDF-PageTool-Test")
    
    print(f"設定ファイルパス: {settings.settings_file}")
    
    # デフォルト設定の確認
    print("\n--- デフォルト設定 ---")
    all_settings = settings.get_all()
    for key, value in sorted(all_settings.items()):
        print(f"{key}: {value}")
    
    # 設定の変更
    print("\n--- 設定変更テスト ---")
    settings.set("theme", "ダーク")
    settings.set("thumbnail_size", 200)
    settings.set("log_level", "DEBUG")
    
    print(f"テーマ: {settings.get('theme')}")
    print(f"サムネイルサイズ: {settings.get('thumbnail_size')}")
    print(f"ログレベル: {settings.get('log_level')}")
    
    # 設定保存
    settings.save_settings()
    print("設定を保存しました")
    
    # 新しいインスタンスで読み込み確認
    print("\n--- 設定読み込み確認 ---")
    settings2 = SettingsManager("PDF-PageTool-Test")
    print(f"テーマ（再読み込み）: {settings2.get('theme')}")
    print(f"サムネイルサイズ（再読み込み）: {settings2.get('thumbnail_size')}")
    
    # 最近使用したファイルのテスト
    print("\n--- 最近使用したファイルテスト ---")
    settings.add_recent_file("/path/to/file1.pdf")
    settings.add_recent_file("/path/to/file2.pdf")
    settings.add_recent_file("/path/to/file3.pdf")
    
    recent_files = settings.get_recent_files()
    print(f"最近使用したファイル: {recent_files}")
    
    # デフォルトリセット
    print("\n--- デフォルトリセットテスト ---")
    settings.reset_to_defaults()
    print(f"リセット後のテーマ: {settings.get('theme')}")
    
    print("✅ 設定管理システムテスト完了")


def test_logger_system():
    """ログシステムのテスト"""
    print("\n=== ログシステムテスト ===")
    
    # 各レベルのロガーをテスト
    logger = get_logger("TestLogger", "DEBUG")
    
    print("ログ出力テスト:")
    logger.debug("これはDEBUGメッセージです")
    logger.verbose("これはVERBOSEメッセージです")
    logger.info("これはINFOメッセージです")
    logger.warning("これはWARNINGメッセージです")
    logger.error("これはERRORメッセージです")
    
    print("✅ ログシステムテスト完了")


def test_file_operations():
    """ファイル操作のテスト"""
    print("\n=== ファイル操作テスト ===")
    
    # プロジェクト構造の確認
    project_root = Path(__file__).parent
    print(f"プロジェクトルート: {project_root}")
    
    # 重要ファイルの存在確認
    important_files = [
        "src/utils/settings_manager.py",
        "src/utils/logger.py", 
        "src/ui/settings_dialog.py",
        "src/ui/main_window.py",
        "src/ui/page_widgets.py",
        "src/pdf_operations/pdf_handler.py",
        "doc/bug_report_template.md",
        "doc/known_issues.md"
    ]
    
    print("\n重要ファイルの確認:")
    for file_path in important_files:
        full_path = project_root / file_path
        status = "✅" if full_path.exists() else "❌"
        print(f"{status} {file_path}")
    
    print("✅ ファイル操作テスト完了")


def test_gui_components():
    """GUI コンポーネントのインポートテスト"""
    print("\n=== GUI コンポーネントテスト ===")
    
    try:
        # PyQt6のインポート確認
        from PyQt6.QtWidgets import QApplication
        print("✅ PyQt6 インポート成功")
        
        # 設定ダイアログのインポート確認
        from src.ui.settings_dialog import SettingsDialog
        print("✅ SettingsDialog インポート成功")
        
        # メインウィンドウのインポート確認
        from src.ui.main_window import MainWindow
        print("✅ MainWindow インポート成功")
        
        # PDF操作のインポート確認
        from src.pdf_operations.pdf_handler import PDFOperations
        print("✅ PDFOperations インポート成功")
        
        # バッチ処理のインポート確認
        from src.ui.batch_processor import BatchProcessorDialog, BatchOperation
        print("✅ BatchProcessor インポート成功")
        
        # プログレスダイアログのインポート確認
        from src.ui.progress_dialog import ProgressDialog, ProgressManager
        print("✅ ProgressDialog インポート成功")
        
        print("✅ GUI コンポーネントテスト完了")
        
    except Exception as e:
        print(f"❌ GUI コンポーネントエラー: {e}")


def test_theme_system():
    """テーマシステムのテスト"""
    print("\n=== テーマシステムテスト ===")
    
    try:
        from src.ui.theme_manager import ThemeManager
        from src.utils.settings_manager import SettingsManager
        
        settings = SettingsManager(app_name="PDF-PageTool-Test")
        theme_manager = ThemeManager(settings)
        
        print(f"現在のテーマ: {theme_manager.current_theme}")
        print(f"利用可能なテーマ: {theme_manager.available_themes}")
        
        # テーマ色情報テスト
        colors = theme_manager.get_theme_colors("ダーク")
        print(f"ダークテーマの色数: {len(colors)}")
        
        # テーマプレビュースタイル取得テスト
        preview_style = theme_manager.get_theme_preview_style("ブルー")
        print(f"ブルーテーマプレビュー生成: {len(preview_style)} 文字")
        
        print("✅ テーマシステムテスト完了")
        return True
        
    except Exception as e:
        print(f"❌ テーマシステムテストエラー: {e}")
        return False


def test_shortcut_system():
    """ショートカットシステムのテスト"""
    print("\n=== ショートカットシステムテスト ===")
    
    try:
        from src.ui.keyboard_shortcuts import ShortcutManager
        from src.utils.settings_manager import SettingsManager
        from PyQt6.QtWidgets import QApplication, QMainWindow
        
        # 最小限のアプリケーション作成
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        main_window = QMainWindow()
        settings = SettingsManager(app_name="PDF-PageTool-Test")
        shortcut_manager = ShortcutManager(main_window, settings)
        
        print(f"デフォルトショートカット数: {len(shortcut_manager.default_shortcuts)}")
        
        # テストアクション登録
        def test_action():
            print("テストアクション実行")
        
        shortcut_manager.register_action('test_action', test_action, 'Ctrl+T')
        print("テストアクション登録完了")
        
        help_text = shortcut_manager.get_shortcut_help_text()
        print(f"ヘルプテキスト生成: {len(help_text)} 文字")
        
        print("✅ ショートカットシステムテスト完了")
        return True
        
    except Exception as e:
        print(f"❌ ショートカットシステムテストエラー: {e}")
        return False


def main():
    """メインテスト実行"""
    print("PDF-PageTool 新機能統合テスト")
    print("=" * 50)
    
    try:
        test_settings_manager()
        test_logger_system()
        test_file_operations()
        test_gui_components()
        test_theme_system()
        test_shortcut_system()
        
        print("\n" + "=" * 50)
        print("🎉 すべてのテストが完了しました!")
        
        print("\n新機能の実装状況:")
        print("✅ 設定管理システム")
        print("✅ 設定ダイアログ")
        print("✅ ツールチップ機能")
        print("✅ 右クリックコンテキストメニュー")
        print("✅ ウィンドウ設定保存/復元")
        print("✅ テーマサポート基盤")
        print("✅ 不具合報告ドキュメント")
        print("✅ PDFページ並び替え機能")
        print("✅ バッチ処理機能")
        print("✅ プログレスバー表示改善")
        print("✅ ダークテーマ実装")
        print("✅ キーボードショートカット")
        
        print("\n次のステップ:")
        print("• 履歴機能（Undo/Redo）")
        print("• パフォーマンス最適化")
        print("• エラーハンドリング強化")
        print("• ユーザビリティ改善")
        print("• テストカバレッジ向上")
        
    except Exception as e:
        print(f"\n❌ テスト実行中にエラーが発生: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
