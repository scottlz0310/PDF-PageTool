#!/usr/bin/env python3

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt


class ThumbnailSizeDialog(QtWidgets.QDialog):
    """サムネイルサイズ設定ダイアログ"""

    def __init__(self, current_size: int = 160, parent=None):
        super().__init__(parent)
        self.current_size = current_size
        self.new_size = current_size
        self.setup_ui()

    def setup_ui(self):
        """UIを設定"""
        self.setWindowTitle("サムネイルサイズ設定")
        self.setFixedSize(400, 200)
        self.setModal(True)

        layout = QtWidgets.QVBoxLayout(self)

        # 説明ラベル
        description_label = QtWidgets.QLabel("サムネイルのサイズを設定してください（50-300ピクセル）")
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description_label)

        # サイズ設定エリア
        size_layout = QtWidgets.QHBoxLayout()

        # 現在のサイズ表示
        current_label = QtWidgets.QLabel(f"現在のサイズ: {self.current_size}px")
        size_layout.addWidget(current_label)

        size_layout.addStretch()
        layout.addLayout(size_layout)

        # スライダーとスピンボックス
        slider_layout = QtWidgets.QHBoxLayout()

        # サイズ調整スライダー
        self.size_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setMinimum(50)
        self.size_slider.setMaximum(300)
        self.size_slider.setValue(self.current_size)
        self.size_slider.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
        self.size_slider.setTickInterval(50)

        # サイズ値表示・入力
        self.size_spinbox = QtWidgets.QSpinBox()
        self.size_spinbox.setMinimum(50)
        self.size_spinbox.setMaximum(300)
        self.size_spinbox.setValue(self.current_size)
        self.size_spinbox.setSuffix("px")

        slider_layout.addWidget(QtWidgets.QLabel("小"))
        slider_layout.addWidget(self.size_slider)
        slider_layout.addWidget(QtWidgets.QLabel("大"))
        slider_layout.addWidget(self.size_spinbox)

        layout.addLayout(slider_layout)

        # プレビューラベル
        self.preview_label = QtWidgets.QLabel(f"プレビューサイズ: {self.current_size}px")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("QLabel { border: 1px solid gray; margin: 10px; padding: 5px; }")
        layout.addWidget(self.preview_label)

        # ボタン
        button_layout = QtWidgets.QHBoxLayout()

        # リセットボタン
        reset_button = QtWidgets.QPushButton("デフォルト（160px）")
        reset_button.clicked.connect(self.reset_to_default)
        button_layout.addWidget(reset_button)

        button_layout.addStretch()

        # OK/Cancelボタン
        self.button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok |
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        button_layout.addWidget(self.button_box)

        layout.addLayout(button_layout)

        # シグナル接続
        self.size_slider.valueChanged.connect(self.update_size)
        self.size_spinbox.valueChanged.connect(self.update_size_from_spinbox)

    def update_size(self, value: int):
        """スライダー値の変更を反映"""
        self.new_size = value
        self.size_spinbox.blockSignals(True)
        self.size_spinbox.setValue(value)
        self.size_spinbox.blockSignals(False)
        self.update_preview()

    def update_size_from_spinbox(self, value: int):
        """スピンボックス値の変更を反映"""
        self.new_size = value
        self.size_slider.blockSignals(True)
        self.size_slider.setValue(value)
        self.size_slider.blockSignals(False)
        self.update_preview()

    def update_preview(self):
        """プレビュー表示を更新"""
        self.preview_label.setText(f"プレビューサイズ: {self.new_size}px")

    def reset_to_default(self):
        """デフォルト値にリセット"""
        self.size_slider.setValue(160)

    def get_size(self) -> int:
        """設定されたサイズを取得"""
        return self.new_size
