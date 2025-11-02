"""
Progress Dialog Module

進行状況表示とキャンセル機能付きダイアログ
"""

from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from ..utils.logger import get_logger


class ProgressDialog(QDialog):
    """進行状況ダイアログ"""

    # シグナル定義
    cancelled = pyqtSignal()

    def __init__(self, title: str = "処理中...", parent=None):
        super().__init__(parent)
        self.logger = get_logger("ProgressDialog")
        self.is_cancelled = False
        self.can_cancel = True
        self.auto_close = True

        self._setup_ui(title)

    def _setup_ui(self, title: str):
        """UI設定"""
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(400, 200)

        # ウィンドウを閉じるボタンを無効化
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)

        layout = QVBoxLayout(self)

        # メインメッセージ
        self.main_label = QLabel("処理を開始しています...")
        self.main_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.main_label)

        # プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # 詳細メッセージ
        self.detail_label = QLabel("")
        self.detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detail_label.setStyleSheet("color: #666666; font-size: 11px;")
        layout.addWidget(self.detail_label)

        # 時間表示
        self.time_label = QLabel("")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("color: #888888; font-size: 10px;")
        layout.addWidget(self.time_label)

        # ログ表示（通常は非表示）
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(100)
        self.log_text.setVisible(False)
        layout.addWidget(self.log_text)

        # ボタンエリア
        button_layout = QHBoxLayout()

        self.show_log_button = QPushButton("ログ表示")
        self.show_log_button.clicked.connect(self._toggle_log_display)
        button_layout.addWidget(self.show_log_button)

        button_layout.addStretch()

        self.cancel_button = QPushButton("キャンセル")
        self.cancel_button.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        # タイマー設定
        self.start_time = QtCore.QTime.currentTime()
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_time)
        self.timer.start(1000)  # 1秒間隔

    def set_range(self, minimum: int, maximum: int):
        """プログレスバーの範囲を設定"""
        self.progress_bar.setRange(minimum, maximum)

    def set_value(self, value: int):
        """プログレスバーの値を設定"""
        self.progress_bar.setValue(value)

        # 完了時の自動クローズ
        if self.auto_close and value >= self.progress_bar.maximum():
            QTimer.singleShot(1500, self.accept)  # 1.5秒後に自動で閉じる

    def set_main_text(self, text: str):
        """メインメッセージを設定"""
        self.main_label.setText(text)

    def set_detail_text(self, text: str):
        """詳細メッセージを設定"""
        self.detail_label.setText(text)

    def add_log(self, message: str):
        """ログメッセージを追加"""
        self.log_text.append(message)
        # 最新のメッセージまでスクロール
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)

    def set_cancelable(self, cancelable: bool):
        """キャンセル可能かどうかを設定"""
        self.can_cancel = cancelable
        self.cancel_button.setEnabled(cancelable)

    def set_auto_close(self, auto_close: bool):
        """自動クローズを設定"""
        self.auto_close = auto_close

    def is_canceled(self) -> bool:
        """キャンセルされているかどうかを確認"""
        return self.is_cancelled

    def _toggle_log_display(self):
        """ログ表示の切り替え"""
        if self.log_text.isVisible():
            self.log_text.setVisible(False)
            self.show_log_button.setText("ログ表示")
            self.resize(400, 200)
        else:
            self.log_text.setVisible(True)
            self.show_log_button.setText("ログ非表示")
            self.resize(400, 350)

    def _on_cancel(self):
        """キャンセルボタンクリック"""
        if self.can_cancel:
            self.is_cancelled = True
            self.cancelled.emit()
            self.cancel_button.setText("キャンセル中...")
            self.cancel_button.setEnabled(False)

    def _update_time(self):
        """経過時間更新"""
        elapsed = self.start_time.msecsTo(QtCore.QTime.currentTime())
        seconds = elapsed // 1000
        minutes = seconds // 60
        seconds = seconds % 60

        if minutes > 0:
            time_text = f"経過時間: {minutes}分{seconds}秒"
        else:
            time_text = f"経過時間: {seconds}秒"

        self.time_label.setText(time_text)

    def closeEvent(self, event):
        """ウィンドウクローズ時の処理"""
        # キャンセル可能な場合のみクローズを許可
        if self.can_cancel and not self.is_cancelled:
            self._on_cancel()

        if self.is_cancelled or self.progress_bar.value() >= self.progress_bar.maximum():
            self.timer.stop()
            event.accept()
        else:
            event.ignore()


class ProgressManager:
    """プログレス管理クラス"""

    def __init__(self, parent=None):
        self.parent = parent
        self.dialog: ProgressDialog | None = None
        self.logger = get_logger("ProgressManager")

    def start_progress(
        self, title: str = "処理中...", cancelable: bool = True, auto_close: bool = True
    ) -> ProgressDialog:
        """プログレス表示開始"""
        if self.dialog:
            self.end_progress()

        self.dialog = ProgressDialog(title, self.parent)
        self.dialog.set_cancelable(cancelable)
        self.dialog.set_auto_close(auto_close)

        return self.dialog

    def show_progress(self):
        """プログレスダイアログを表示"""
        if self.dialog:
            self.dialog.show()

    def update_progress(self, value: int, main_text: str = "", detail_text: str = ""):
        """プログレス更新"""
        if self.dialog:
            self.dialog.set_value(value)
            if main_text:
                self.dialog.set_main_text(main_text)
            if detail_text:
                self.dialog.set_detail_text(detail_text)

    def set_range(self, minimum: int, maximum: int):
        """プログレス範囲設定"""
        if self.dialog:
            self.dialog.set_range(minimum, maximum)

    def add_log(self, message: str):
        """ログ追加"""
        if self.dialog:
            self.dialog.add_log(message)

    def is_cancelled(self) -> bool:
        """キャンセル状態確認"""
        return self.dialog.is_cancelled if self.dialog else False

    def end_progress(self):
        """プログレス表示終了"""
        if self.dialog:
            self.dialog.close()
            self.dialog = None

    def __enter__(self):
        """コンテキストマネージャー対応"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー終了時"""
        self.end_progress()


# 使用例とテスト関数
def test_progress_dialog():
    """プログレスダイアログのテスト"""
    import sys
    import time

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # プログレスマネージャーを使用
    with ProgressManager() as pm:
        _dialog = pm.start_progress("テスト処理", cancelable=True)
        pm.set_range(0, 100)
        pm.show_progress()

        # 模擬処理
        for i in range(101):
            if pm.is_cancelled():
                print("処理がキャンセルされました")
                break

            pm.update_progress(i, f"処理中... {i}%", f"ステップ {i}/100")
            pm.add_log(f"ステップ {i} 完了")

            app.processEvents()  # UIの更新
            time.sleep(0.1)  # 実際の処理時間をシミュレート

        if not pm.is_cancelled():
            pm.update_progress(100, "完了!", "すべての処理が完了しました")

    sys.exit(app.exec())


if __name__ == "__main__":
    test_progress_dialog()
