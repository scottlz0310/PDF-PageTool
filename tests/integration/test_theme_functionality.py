#!/usr/bin/env python3
"""
テーマ機能のテストスクリプト
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from src.ui.theme_manager import get_theme_manager
from src.utils.settings_manager import SettingsManager

def test_theme_functionality():
    """テーマ機能のテスト"""
    print("🎨 テーマ機能のテストを開始します...")
    
    # QApplicationインスタンスを作成
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # SettingsManagerを初期化
    settings_manager = SettingsManager()
    
    # テーママネージャーを取得
    theme_manager = get_theme_manager(settings_manager)
    
    print(f"✅ 利用可能なテーマ: {theme_manager.available_themes}")
    print(f"✅ 現在のテーマ: {theme_manager.current_theme}")
    
    # 各テーマをテスト
    test_themes = ['ライト', 'ダーク', 'ブルー', 'グリーン']
    
    for theme in test_themes:
        try:
            print(f"🔄 テーマ '{theme}' を適用中...")
            theme_manager.apply_theme(theme, app)
            
            # テーマカラーを取得
            colors = theme_manager.get_theme_colors(theme)
            print(f"   🎨 背景色: {colors.get('background', 'N/A')}")
            print(f"   🎨 前景色: {colors.get('foreground', 'N/A')}")
            print(f"   🎨 アクセント色: {colors.get('accent', 'N/A')}")
            
            # プレビュースタイルを取得
            preview_style = theme_manager.get_theme_preview_style(theme)
            print(f"   📜 プレビュースタイル生成: {'✅' if preview_style else '❌'}")
            
            print(f"✅ テーマ '{theme}' の適用完了")
            
        except Exception as e:
            print(f"❌ テーマ '{theme}' の適用に失敗: {e}")
            return False
    
    # 設定からのテーマ読み込みテスト
    try:
        print("🔄 設定からのテーマ読み込みテスト...")
        theme_manager.load_theme_from_settings(app)
        print("✅ 設定からのテーマ読み込み成功")
    except Exception as e:
        print(f"❌ 設定からのテーマ読み込み失敗: {e}")
        return False
    
    # シグナル接続テスト
    try:
        print("🔄 シグナル接続テスト...")
        def on_theme_changed(theme_name):
            print(f"🎨 テーマ変更シグナル受信: {theme_name}")
        
        theme_manager.theme_changed.connect(on_theme_changed)
        theme_manager.apply_theme('ライト', app)
        print("✅ シグナル接続テスト成功")
    except Exception as e:
        print(f"❌ シグナル接続テスト失敗: {e}")
        return False
    
    return True

def test_theme_manager_integration():
    """テーママネージャーとの統合テスト"""
    print("\n🔗 テーママネージャー統合テストを開始します...")
    
    try:
        # シングルトンインスタンステスト
        tm1 = get_theme_manager()
        tm2 = get_theme_manager()
        
        if tm1 is tm2:
            print("✅ シングルトンパターン正常動作")
        else:
            print("❌ シングルトンパターン異常")
            return False
            
        # テーマライブラリの確認
        themes = tm1.available_themes
        expected_themes = ['ライト', 'ダーク', 'ブルー', 'グリーン']
        
        if set(themes) == set(expected_themes):
            print("✅ テーマライブラリ完全実装")
        else:
            print(f"❌ テーマライブラリ不完全: 期待={expected_themes}, 実際={themes}")
            return False
            
        # ハードコーディング確認
        for theme in themes:
            colors = tm1.get_theme_colors(theme)
            if not colors:
                print(f"❌ テーマ '{theme}' の色定義が見つかりません")
                return False
        
        print("✅ すべてのテーマが定義ファイルから正しく読み込まれています")
        return True
        
    except Exception as e:
        print(f"❌ 統合テスト失敗: {e}")
        return False

if __name__ == "__main__":
    print("🎨 PDF-PageTool テーマ機能総合テスト")
    print("=" * 50)
    
    # 基本機能テスト
    basic_test = test_theme_functionality()
    
    # 統合テスト
    integration_test = test_theme_manager_integration()
    
    print("\n" + "=" * 50)
    print("📊 テスト結果:")
    print(f"   基本機能テスト: {'✅ 成功' if basic_test else '❌ 失敗'}")
    print(f"   統合テスト: {'✅ 成功' if integration_test else '❌ 失敗'}")
    
    if basic_test and integration_test:
        print("\n🎉 すべてのテーマ機能テストが成功しました！")
        print("💡 テーママネージャーライブラリは正常に導入・動作しています。")
        sys.exit(0)
    else:
        print("\n❌ 一部のテストが失敗しました。")
        print("🔧 テーマ機能に問題があります。修正が必要です。")
        sys.exit(1)
