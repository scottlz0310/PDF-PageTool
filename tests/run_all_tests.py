#!/usr/bin/env python3
"""
PDF-PageTool 全テスト実行スクリプト

使用方法:
    python -m tests.run_all_tests
    または
    python tests/run_all_tests.py
"""

import subprocess
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_debug_tests():
    """デバッグテストの実行"""
    print("🔍 デバッグテスト実行中...")
    try:
        debug_script = project_root / "tests" / "debug" / "debug_test.py"
        result = subprocess.run([sys.executable, str(debug_script)], capture_output=True, text=True, cwd=project_root)

        print("--- デバッグテスト結果 ---")
        print(result.stdout)
        if result.stderr:
            print("エラー出力:")
            print(result.stderr)

        return result.returncode == 0
    except Exception as e:
        print(f"❌ デバッグテスト実行エラー: {e}")
        return False


def run_unit_tests():
    """ユニットテストの実行"""
    print("\n🧪 ユニットテスト実行中...")
    tests_passed = 0
    tests_total = 0

    unit_test_dir = project_root / "tests" / "unit"
    for test_file in unit_test_dir.glob("test_*.py"):
        tests_total += 1
        try:
            print(f"  実行中: {test_file.name}")
            result = subprocess.run([sys.executable, str(test_file)], capture_output=True, text=True, cwd=project_root)

            if result.returncode == 0:
                print(f"  ✅ {test_file.name} - 成功")
                tests_passed += 1
            else:
                print(f"  ❌ {test_file.name} - 失敗")
                if result.stdout:
                    print(f"     出力: {result.stdout}")
                if result.stderr:
                    print(f"     エラー: {result.stderr}")
        except Exception as e:
            print(f"  ❌ {test_file.name} - 実行エラー: {e}")

    print(f"\nユニットテスト結果: {tests_passed}/{tests_total} 成功")
    return tests_passed == tests_total


def run_integration_tests():
    """統合テストの実行"""
    print("\n🔗 統合テスト実行中...")
    tests_passed = 0
    tests_total = 0

    integration_test_dir = project_root / "tests" / "integration"
    for test_file in integration_test_dir.glob("test_*.py"):
        tests_total += 1
        try:
            print(f"  実行中: {test_file.name}")
            result = subprocess.run([sys.executable, str(test_file)], capture_output=True, text=True, cwd=project_root)

            if result.returncode == 0:
                print(f"  ✅ {test_file.name} - 成功")
                tests_passed += 1
            else:
                print(f"  ❌ {test_file.name} - 失敗")
                if result.stdout:
                    print(f"     出力: {result.stdout}")
                if result.stderr:
                    print(f"     エラー: {result.stderr}")
        except Exception as e:
            print(f"  ❌ {test_file.name} - 実行エラー: {e}")

    print(f"\n統合テスト結果: {tests_passed}/{tests_total} 成功")
    return tests_passed == tests_total


def main():
    """メインテスト実行"""
    print("PDF-PageTool 全テスト実行")
    print("=" * 60)

    # 各テストカテゴリを実行
    debug_success = run_debug_tests()
    unit_success = run_unit_tests()
    integration_success = run_integration_tests()

    # 結果サマリー
    print("\n" + "=" * 60)
    print("📊 テスト結果サマリー")
    print(f"🔍 デバッグテスト: {'✅ 成功' if debug_success else '❌ 失敗'}")
    print(f"🧪 ユニットテスト: {'✅ 成功' if unit_success else '❌ 失敗'}")
    print(f"🔗 統合テスト: {'✅ 成功' if integration_success else '❌ 失敗'}")

    overall_success = debug_success and unit_success and integration_success

    if overall_success:
        print("\n🎉 全テスト成功！")
        return 0
    else:
        print("\n⚠️ 一部テストが失敗しました")
        return 1


if __name__ == "__main__":
    sys.exit(main())
