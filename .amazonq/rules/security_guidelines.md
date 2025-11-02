# PDF-PageTool セキュリティガイドライン

## ファイル処理セキュリティ

### PDFファイル検証
```python
import magic
from pathlib import Path

class SecurePDFValidator:
    def __init__(self):
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.allowed_extensions = {'.pdf'}

    def validate_pdf_file(self, file_path: str) -> bool:
        """PDFファイルの安全性を検証"""
        try:
            path = Path(file_path)

            # ファイル存在確認
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            # ファイルサイズ制限
            if path.stat().st_size > self.max_file_size:
                raise ValueError(f"File too large: {path.stat().st_size} bytes")

            # 拡張子確認
            if path.suffix.lower() not in self.allowed_extensions:
                raise ValueError(f"Invalid file extension: {path.suffix}")

            # MIMEタイプ確認
            mime_type = magic.from_file(str(path), mime=True)
            if mime_type != 'application/pdf':
                raise ValueError(f"Invalid MIME type: {mime_type}")

            # PDFファイル構造の基本検証
            self._validate_pdf_structure(file_path)

            return True

        except Exception as e:
            self.logger.error(f"PDF validation failed: {e}")
            return False

    def _validate_pdf_structure(self, file_path: str):
        """PDFファイル構造の基本検証"""
        try:
            with open(file_path, 'rb') as file:
                # PDFヘッダー確認
                header = file.read(8)
                if not header.startswith(b'%PDF-'):
                    raise ValueError("Invalid PDF header")

                # PyPDF2での読み込みテスト
                reader = PdfReader(file_path)
                if len(reader.pages) == 0:
                    raise ValueError("PDF has no pages")

        except Exception as e:
            raise ValueError(f"PDF structure validation failed: {e}")
```

### パストラバーサル対策
```python
import os
from pathlib import Path

class SecurePathHandler:
    def __init__(self, base_directory: str):
        self.base_directory = Path(base_directory).resolve()

    def validate_path(self, file_path: str) -> str:
        """パストラバーサル攻撃を防ぐパス検証"""
        try:
            # パスを正規化
            normalized_path = Path(file_path).resolve()

            # ベースディレクトリ外へのアクセスを防ぐ
            if not str(normalized_path).startswith(str(self.base_directory)):
                raise ValueError(f"Path outside base directory: {normalized_path}")

            # 危険な文字列をチェック
            dangerous_patterns = ['..', '~', '$']
            for pattern in dangerous_patterns:
                if pattern in str(normalized_path):
                    raise ValueError(f"Dangerous pattern in path: {pattern}")

            return str(normalized_path)

        except Exception as e:
            self.logger.error(f"Path validation failed: {e}")
            raise
```

## 一時ファイルセキュリティ

### 安全な一時ファイル管理
```python
import tempfile
import os
import stat
from pathlib import Path

class SecureTempFileManager:
    def __init__(self):
        self.temp_dir = None
        self.created_files = set()
        self._create_secure_temp_dir()

    def _create_secure_temp_dir(self):
        """セキュアな一時ディレクトリを作成"""
        try:
            # セキュアな一時ディレクトリ作成
            self.temp_dir = tempfile.mkdtemp(
                prefix="pdf_pagetool_secure_",
                suffix="_temp"
            )

            # ディレクトリの権限を制限（所有者のみアクセス可能）
            os.chmod(self.temp_dir, stat.S_IRWXU)  # 700

            self.logger.info(f"Secure temp directory created: {self.temp_dir}")

        except Exception as e:
            self.logger.error(f"Failed to create secure temp directory: {e}")
            raise

    def create_temp_file(self, suffix: str = ".tmp") -> str:
        """セキュアな一時ファイルを作成"""
        try:
            fd, temp_path = tempfile.mkstemp(
                suffix=suffix,
                dir=self.temp_dir
            )

            # ファイルの権限を制限（所有者のみ読み書き可能）
            os.chmod(temp_path, stat.S_IRUSR | stat.S_IWUSR)  # 600

            # ファイルディスクリプタを閉じる
            os.close(fd)

            self.created_files.add(temp_path)
            return temp_path

        except Exception as e:
            self.logger.error(f"Failed to create secure temp file: {e}")
            raise

    def secure_cleanup(self):
        """セキュアなクリーンアップ"""
        try:
            # 作成したファイルを安全に削除
            for file_path in self.created_files.copy():
                if os.path.exists(file_path):
                    # ファイル内容を上書きしてから削除
                    self._secure_delete_file(file_path)
                    self.created_files.remove(file_path)

            # 一時ディレクトリを削除
            if self.temp_dir and os.path.exists(self.temp_dir):
                os.rmdir(self.temp_dir)

        except Exception as e:
            self.logger.error(f"Secure cleanup failed: {e}")

    def _secure_delete_file(self, file_path: str):
        """ファイルを安全に削除（内容を上書き）"""
        try:
            file_size = os.path.getsize(file_path)

            # ファイル内容をランダムデータで上書き
            with open(file_path, 'r+b') as file:
                file.write(os.urandom(file_size))
                file.flush()
                os.fsync(file.fileno())

            # ファイルを削除
            os.remove(file_path)

        except Exception as e:
            self.logger.warning(f"Secure file deletion failed: {e}")
            # 通常の削除を試行
            try:
                os.remove(file_path)
            except:
                pass
```

## 入力検証とサニタイゼーション

### ユーザー入力の検証
```python
import re
from typing import Any, Dict

class InputValidator:
    def __init__(self):
        self.filename_pattern = re.compile(r'^[a-zA-Z0-9._-]+$')
        self.max_filename_length = 255

    def validate_filename(self, filename: str) -> str:
        """ファイル名の検証とサニタイゼーション"""
        if not filename:
            raise ValueError("Filename cannot be empty")

        if len(filename) > self.max_filename_length:
            raise ValueError(f"Filename too long: {len(filename)} characters")

        # 危険な文字を除去
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)

        # 予約語チェック（Windows）
        reserved_names = {
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        }

        name_without_ext = sanitized.split('.')[0].upper()
        if name_without_ext in reserved_names:
            sanitized = f"file_{sanitized}"

        return sanitized

    def validate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """設定値の検証"""
        validated = {}

        # 数値設定の検証
        if 'thumbnail_size' in settings:
            size = settings['thumbnail_size']
            if not isinstance(size, int) or size < 50 or size > 500:
                raise ValueError(f"Invalid thumbnail size: {size}")
            validated['thumbnail_size'] = size

        # 文字列設定の検証
        if 'theme' in settings:
            theme = settings['theme']
            allowed_themes = {'light', 'dark', 'blue', 'green'}
            if theme not in allowed_themes:
                raise ValueError(f"Invalid theme: {theme}")
            validated['theme'] = theme

        return validated
```

## ログセキュリティ

### セキュアなログ出力
```python
import re
from typing import Any

class SecureLogger:
    def __init__(self, base_logger):
        self.base_logger = base_logger
        self.sensitive_patterns = [
            r'password[=:]\s*\S+',
            r'token[=:]\s*\S+',
            r'key[=:]\s*\S+',
            r'secret[=:]\s*\S+',
        ]

    def _sanitize_message(self, message: str) -> str:
        """ログメッセージから機密情報を除去"""
        sanitized = message

        # 機密情報パターンをマスク
        for pattern in self.sensitive_patterns:
            sanitized = re.sub(pattern, lambda m: m.group().split('=')[0] + '=***',
                             sanitized, flags=re.IGNORECASE)

        # ファイルパスの個人情報を部分的にマスク
        sanitized = re.sub(r'/Users/([^/]+)/', r'/Users/***//', sanitized)
        sanitized = re.sub(r'C:\\Users\\([^\\]+)\\', r'C:\\Users\\***\\', sanitized)

        return sanitized

    def info(self, message: str):
        sanitized = self._sanitize_message(message)
        self.base_logger.info(sanitized)

    def error(self, message: str):
        sanitized = self._sanitize_message(message)
        self.base_logger.error(sanitized)

    def debug(self, message: str):
        sanitized = self._sanitize_message(message)
        self.base_logger.debug(sanitized)
```

## 設定ファイルセキュリティ

### 設定ファイルの暗号化
```python
import json
import base64
from cryptography.fernet import Fernet
from pathlib import Path

class SecureSettingsManager:
    def __init__(self, settings_file: str):
        self.settings_file = Path(settings_file)
        self.key_file = self.settings_file.with_suffix('.key')
        self.cipher = self._get_or_create_cipher()

    def _get_or_create_cipher(self) -> Fernet:
        """暗号化キーを取得または作成"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            # キーファイルの権限を制限
            with open(self.key_file, 'wb') as f:
                f.write(key)
            os.chmod(self.key_file, stat.S_IRUSR | stat.S_IWUSR)  # 600

        return Fernet(key)

    def save_settings(self, settings: Dict[str, Any]):
        """設定を暗号化して保存"""
        try:
            # 設定をJSONに変換
            json_data = json.dumps(settings, ensure_ascii=False)

            # 暗号化
            encrypted_data = self.cipher.encrypt(json_data.encode('utf-8'))

            # Base64エンコードして保存
            with open(self.settings_file, 'wb') as f:
                f.write(base64.b64encode(encrypted_data))

            # ファイル権限を制限
            os.chmod(self.settings_file, stat.S_IRUSR | stat.S_IWUSR)  # 600

        except Exception as e:
            self.logger.error(f"Failed to save encrypted settings: {e}")
            raise

    def load_settings(self) -> Dict[str, Any]:
        """暗号化された設定を読み込み"""
        try:
            if not self.settings_file.exists():
                return {}

            # Base64デコード
            with open(self.settings_file, 'rb') as f:
                encrypted_data = base64.b64decode(f.read())

            # 復号化
            decrypted_data = self.cipher.decrypt(encrypted_data)

            # JSONパース
            return json.loads(decrypted_data.decode('utf-8'))

        except Exception as e:
            self.logger.error(f"Failed to load encrypted settings: {e}")
            return {}
```

## エラーハンドリングセキュリティ

### セキュアなエラー処理
```python
class SecureErrorHandler:
    def __init__(self, logger):
        self.logger = logger

    def handle_file_error(self, error: Exception, file_path: str = None):
        """ファイル関連エラーの安全な処理"""
        # 内部ログには詳細情報を記録
        if file_path:
            self.logger.error(f"File operation failed: {error} (Path: {file_path})")
        else:
            self.logger.error(f"File operation failed: {error}")

        # ユーザーには一般的なメッセージを表示
        if isinstance(error, FileNotFoundError):
            return "指定されたファイルが見つかりません。"
        elif isinstance(error, PermissionError):
            return "ファイルにアクセスする権限がありません。"
        elif isinstance(error, OSError):
            return "ファイル操作中にエラーが発生しました。"
        else:
            return "予期しないエラーが発生しました。"

    def handle_pdf_error(self, error: Exception):
        """PDF処理エラーの安全な処理"""
        self.logger.error(f"PDF processing failed: {error}")

        # 攻撃者に有用な情報を与えない一般的なメッセージ
        return "PDFファイルの処理中にエラーが発生しました。ファイルが破損している可能性があります。"
```

## セキュリティ監査

### セキュリティチェックリスト
```python
class SecurityAuditor:
    def __init__(self):
        self.security_checks = [
            self._check_file_permissions,
            self._check_temp_directory_security,
            self._check_log_file_permissions,
            self._check_settings_encryption,
        ]

    def run_security_audit(self) -> Dict[str, bool]:
        """セキュリティ監査を実行"""
        results = {}

        for check in self.security_checks:
            try:
                check_name = check.__name__
                results[check_name] = check()
            except Exception as e:
                self.logger.error(f"Security check failed: {check.__name__}: {e}")
                results[check.__name__] = False

        return results

    def _check_file_permissions(self) -> bool:
        """ファイル権限をチェック"""
        # 重要なファイルの権限確認
        critical_files = [
            self.settings_file,
            self.key_file,
            self.log_file
        ]

        for file_path in critical_files:
            if file_path.exists():
                file_stat = file_path.stat()
                # 所有者以外に読み取り権限がないことを確認
                if file_stat.st_mode & (stat.S_IRGRP | stat.S_IROTH):
                    return False

        return True
```
