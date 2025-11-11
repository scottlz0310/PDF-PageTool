"""
Batch Processing Module

複数PDFファイルの一括処理機能
"""

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from PyQt6 import QtWidgets
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..pdf_operations import PDFOperations
from ..utils.logger import get_logger


class BatchOperation(Enum):
    """バッチ操作の種類"""

    MERGE_ALL = "merge_all"
    SPLIT_ALL = "split_all"
    ROTATE_ALL = "rotate_all"
    EXTRACT_PAGES = "extract_pages"
    OPTIMIZE_ALL = "optimize_all"


@dataclass
class BatchJob:
    """バッチ処理ジョブ"""

    operation: BatchOperation
    input_files: list[str]
    output_directory: str
    parameters: dict[str, Any]
    name: str = ""


class BatchProcessorThread(QThread):
    """バッチ処理を実行するスレッド"""

    # シグナル定義
    progress_updated = pyqtSignal(int, int, str)  # 現在, 総数, メッセージ
    file_processed = pyqtSignal(str, bool, str)  # ファイル, 成功, メッセージ
    job_completed = pyqtSignal(bool, str)  # 成功, メッセージ

    def __init__(self, job: BatchJob, log_level: str = "INFO"):
        super().__init__()
        self.job = job
        self.pdf_ops = PDFOperations(log_level)
        self.logger = get_logger("BatchProcessor", log_level)
        self.should_stop = False

    def stop(self) -> None:
        """処理を停止"""
        self.should_stop = True

    def run(self) -> None:
        """バッチ処理実行"""
        try:
            total_files = len(self.job.input_files)
            self.logger.info(f"Starting batch job: {self.job.operation.value} on {total_files} files")

            success_count = 0

            for i, file_path in enumerate(self.job.input_files):
                if self.should_stop:
                    self.job_completed.emit(False, "処理が中断されました")
                    return

                self.progress_updated.emit(i, total_files, f"処理中: {Path(file_path).name}")

                try:
                    success = self._process_file(file_path)
                    if success:
                        success_count += 1
                        self.file_processed.emit(file_path, True, "完了")
                    else:
                        self.file_processed.emit(file_path, False, "失敗")

                except Exception as e:
                    self.logger.error(f"Error processing {file_path}: {e}")
                    self.file_processed.emit(file_path, False, str(e))

            # 完了
            self.progress_updated.emit(total_files, total_files, "完了")
            success_rate = (success_count / total_files) * 100 if total_files > 0 else 0
            message = f"処理完了: {success_count}/{total_files} ファイル ({success_rate:.1f}%)"
            self.job_completed.emit(success_count > 0, message)

        except Exception as e:
            self.logger.error(f"Batch job failed: {e}")
            self.job_completed.emit(False, f"バッチ処理エラー: {e}")

    def _process_file(self, file_path: str) -> bool:
        """単一ファイルの処理"""
        try:
            if self.job.operation == BatchOperation.MERGE_ALL:
                return self._merge_file(file_path)
            elif self.job.operation == BatchOperation.SPLIT_ALL:
                return self._split_file(file_path)
            elif self.job.operation == BatchOperation.ROTATE_ALL:
                return self._rotate_file(file_path)
            elif self.job.operation == BatchOperation.EXTRACT_PAGES:
                return self._extract_pages(file_path)
            elif self.job.operation == BatchOperation.OPTIMIZE_ALL:
                return self._optimize_file(file_path)
            else:
                return False

        except Exception as e:
            self.logger.error(f"Error in _process_file for {file_path}: {e}")
            return False

    def _merge_file(self, file_path: str) -> bool:
        """ファイル結合処理（他のファイルと結合）"""
        # 簡単な実装：各ファイルを個別に出力ディレクトリにコピー
        # 実際の結合は別途実装
        try:
            output_path = os.path.join(self.job.output_directory, f"merged_{Path(file_path).stem}.pdf")

            # PDFを読み込んで再保存（基本的な処理）
            pages = self.pdf_ops.load_pdf(file_path)
            if pages:
                self.pdf_ops.merge_pages(pages, output_path)
                return True
            return False

        except Exception as e:
            self.logger.error(f"Merge failed for {file_path}: {e}")
            return False

    def _split_file(self, file_path: str) -> bool:
        """ファイル分割処理"""
        try:
            pages = self.pdf_ops.load_pdf(file_path)
            if not pages:
                return False

            base_name = Path(file_path).stem
            success_count = 0

            for i, page in enumerate(pages):
                output_path = os.path.join(self.job.output_directory, f"{base_name}_page_{i + 1}.pdf")

                try:
                    self.pdf_ops.merge_pages([page], output_path)
                    success_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to save page {i + 1}: {e}")

            return success_count == len(pages)

        except Exception as e:
            self.logger.error(f"Split failed for {file_path}: {e}")
            return False

    def _rotate_file(self, file_path: str) -> bool:
        """ファイル回転処理"""
        try:
            angle = self.job.parameters.get("rotation_angle", 90)
            pages = self.pdf_ops.load_pdf(file_path)

            if not pages:
                return False

            # 全ページを回転
            for page in pages:
                page.rotation = (page.rotation + angle) % 360

            output_path = os.path.join(self.job.output_directory, f"rotated_{Path(file_path).name}")

            self.pdf_ops.merge_pages(pages, output_path)
            return True

        except Exception as e:
            self.logger.error(f"Rotation failed for {file_path}: {e}")
            return False

    def _extract_pages(self, file_path: str) -> bool:
        """ページ抽出処理"""
        try:
            start_page = self.job.parameters.get("start_page", 1) - 1
            end_page = self.job.parameters.get("end_page", -1)

            pages = self.pdf_ops.load_pdf(file_path)
            if not pages:
                return False

            if end_page == -1:
                end_page = len(pages)

            extracted_pages = pages[start_page:end_page]

            output_path = os.path.join(self.job.output_directory, f"extracted_{Path(file_path).name}")

            self.pdf_ops.merge_pages(extracted_pages, output_path)
            return True

        except Exception as e:
            self.logger.error(f"Extraction failed for {file_path}: {e}")
            return False

    def _optimize_file(self, file_path: str) -> bool:
        """ファイル最適化処理"""
        try:
            # 基本的な最適化：読み込んで再保存
            pages = self.pdf_ops.load_pdf(file_path)
            if not pages:
                return False

            output_path = os.path.join(self.job.output_directory, f"optimized_{Path(file_path).name}")

            self.pdf_ops.merge_pages(pages, output_path)
            return True

        except Exception as e:
            self.logger.error(f"Optimization failed for {file_path}: {e}")
            return False


class BatchProcessorDialog(QDialog):
    """バッチ処理ダイアログ"""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.logger = get_logger("BatchProcessorDialog")
        self.processor_thread: BatchProcessorThread | None = None
        self.current_job: BatchJob | None = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """UI設定"""
        self.setWindowTitle("バッチ処理")
        self.setModal(True)
        self.resize(600, 500)

        layout = QVBoxLayout(self)

        # タブウィジェット
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # 設定タブ
        self._setup_config_tab()

        # 進行状況タブ
        self._setup_progress_tab()

        # ボタンエリア
        button_layout = QHBoxLayout()

        self.start_button = QPushButton("開始")
        self.start_button.clicked.connect(self._start_processing)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("停止")
        self.stop_button.clicked.connect(self._stop_processing)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        button_layout.addStretch()

        self.close_button = QPushButton("閉じる")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def _setup_config_tab(self) -> None:
        """設定タブ"""
        tab = QWidget()
        self.tab_widget.addTab(tab, "設定")

        layout = QVBoxLayout(tab)

        # ファイル選択
        file_group = QGroupBox("入力ファイル")
        file_layout = QVBoxLayout(file_group)

        file_button_layout = QHBoxLayout()
        self.add_files_button = QPushButton("ファイル追加...")
        self.add_files_button.clicked.connect(self._add_files)
        file_button_layout.addWidget(self.add_files_button)

        self.clear_files_button = QPushButton("クリア")
        self.clear_files_button.clicked.connect(self._clear_files)
        file_button_layout.addWidget(self.clear_files_button)

        file_button_layout.addStretch()
        file_layout.addLayout(file_button_layout)

        self.file_list = QListWidget()
        self.file_list.setMaximumHeight(150)
        file_layout.addWidget(self.file_list)

        layout.addWidget(file_group)

        # 操作選択
        operation_group = QGroupBox("操作")
        operation_layout = QVBoxLayout(operation_group)

        self.merge_radio = QCheckBox("すべて結合")
        operation_layout.addWidget(self.merge_radio)

        self.split_radio = QCheckBox("ページ分割")
        operation_layout.addWidget(self.split_radio)

        rotation_layout = QHBoxLayout()
        self.rotate_radio = QCheckBox("回転")
        rotation_layout.addWidget(self.rotate_radio)
        self.rotation_angle = QSpinBox()
        self.rotation_angle.setRange(-360, 360)
        self.rotation_angle.setValue(90)
        self.rotation_angle.setSuffix("°")
        rotation_layout.addWidget(self.rotation_angle)
        rotation_layout.addStretch()
        operation_layout.addLayout(rotation_layout)

        extract_layout = QHBoxLayout()
        self.extract_radio = QCheckBox("ページ抽出")
        extract_layout.addWidget(self.extract_radio)
        extract_layout.addWidget(QLabel("開始:"))
        self.start_page = QSpinBox()
        self.start_page.setRange(1, 9999)
        self.start_page.setValue(1)
        extract_layout.addWidget(self.start_page)
        extract_layout.addWidget(QLabel("終了:"))
        self.end_page = QSpinBox()
        self.end_page.setRange(1, 9999)
        self.end_page.setValue(10)
        extract_layout.addWidget(self.end_page)
        extract_layout.addStretch()
        operation_layout.addLayout(extract_layout)

        self.optimize_radio = QCheckBox("最適化")
        operation_layout.addWidget(self.optimize_radio)

        layout.addWidget(operation_group)

        # 出力設定
        output_group = QGroupBox("出力")
        output_layout = QVBoxLayout(output_group)

        output_dir_layout = QHBoxLayout()
        output_dir_layout.addWidget(QLabel("出力ディレクトリ:"))
        self.output_dir_edit = QtWidgets.QLineEdit()
        output_dir_layout.addWidget(self.output_dir_edit)

        browse_output_button = QPushButton("参照...")
        browse_output_button.clicked.connect(self._browse_output_directory)
        output_dir_layout.addWidget(browse_output_button)
        output_layout.addLayout(output_dir_layout)

        layout.addWidget(output_group)

        layout.addStretch()

    def _setup_progress_tab(self) -> None:
        """進行状況タブ"""
        tab = QWidget()
        self.tab_widget.addTab(tab, "進行状況")

        layout = QVBoxLayout(tab)

        # プログレスバー
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("待機中...")
        layout.addWidget(self.progress_label)

        # ログ出力
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

    def _add_files(self) -> None:
        """ファイル追加"""
        files, _ = QFileDialog.getOpenFileNames(self, "PDFファイルを選択", "", "PDF files (*.pdf)")
        for file_path in files:
            self.file_list.addItem(file_path)

    def _clear_files(self) -> None:
        """ファイルリストクリア"""
        self.file_list.clear()

    def _browse_output_directory(self) -> None:
        """出力ディレクトリ選択"""
        directory = QFileDialog.getExistingDirectory(self, "出力ディレクトリを選択", self.output_dir_edit.text())
        if directory:
            self.output_dir_edit.setText(directory)

    def _start_processing(self) -> None:
        """処理開始"""
        try:
            # 入力チェック
            if self.file_list.count() == 0:
                QtWidgets.QMessageBox.warning(self, "エラー", "入力ファイルが選択されていません")
                return

            if not self.output_dir_edit.text():
                QtWidgets.QMessageBox.warning(self, "エラー", "出力ディレクトリが選択されていません")
                return

            # 操作選択チェック
            operation = self._get_selected_operation()
            if not operation:
                QtWidgets.QMessageBox.warning(self, "エラー", "操作が選択されていません")
                return

            # ファイルリスト取得
            input_files = []
            for i in range(self.file_list.count()):
                item = self.file_list.item(i)
                if item:
                    input_files.append(item.text())

            # パラメータ準備
            parameters = {}
            if operation == BatchOperation.ROTATE_ALL:
                parameters["rotation_angle"] = self.rotation_angle.value()
            elif operation == BatchOperation.EXTRACT_PAGES:
                parameters["start_page"] = self.start_page.value()
                parameters["end_page"] = self.end_page.value()

            # ジョブ作成
            self.current_job = BatchJob(
                operation=operation,
                input_files=input_files,
                output_directory=self.output_dir_edit.text(),
                parameters=parameters,
                name=f"{operation.value}_{len(input_files)}files",
            )

            # UI状態変更
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.tab_widget.setCurrentIndex(1)  # 進行状況タブに切り替え

            # ログクリア
            self.log_text.clear()
            self.log_text.append(f"バッチ処理開始: {operation.value}")
            self.log_text.append(f"対象ファイル数: {len(input_files)}")
            self.log_text.append(f"出力ディレクトリ: {self.output_dir_edit.text()}")
            self.log_text.append("-" * 50)

            # スレッド開始
            self.processor_thread = BatchProcessorThread(self.current_job)
            self.processor_thread.progress_updated.connect(self._on_progress_updated)
            self.processor_thread.file_processed.connect(self._on_file_processed)
            self.processor_thread.job_completed.connect(self._on_job_completed)
            self.processor_thread.start()

        except Exception as e:
            self.logger.error(f"Failed to start processing: {e}")
            QtWidgets.QMessageBox.critical(self, "エラー", f"処理開始に失敗しました: {e}")

    def _stop_processing(self) -> None:
        """処理停止"""
        if self.processor_thread and self.processor_thread.isRunning():
            self.processor_thread.stop()
            self.log_text.append("停止要求を送信しました...")

    def _get_selected_operation(self) -> BatchOperation | None:
        """選択された操作を取得"""
        if self.merge_radio.isChecked():
            return BatchOperation.MERGE_ALL
        elif self.split_radio.isChecked():
            return BatchOperation.SPLIT_ALL
        elif self.rotate_radio.isChecked():
            return BatchOperation.ROTATE_ALL
        elif self.extract_radio.isChecked():
            return BatchOperation.EXTRACT_PAGES
        elif self.optimize_radio.isChecked():
            return BatchOperation.OPTIMIZE_ALL
        return None

    def _on_progress_updated(self, current: int, total: int, message: str) -> None:
        """進行状況更新"""
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(current)
        self.progress_label.setText(f"{current}/{total} - {message}")

    def _on_file_processed(self, file_path: str, success: bool, message: str) -> None:
        """ファイル処理完了"""
        file_name = Path(file_path).name
        status = "✅" if success else "❌"
        self.log_text.append(f"{status} {file_name}: {message}")

    def _on_job_completed(self, success: bool, message: str) -> None:
        """ジョブ完了"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        status = "✅ 完了" if success else "❌ 失敗"
        self.log_text.append("-" * 50)
        self.log_text.append(f"{status}: {message}")

        if success:
            QtWidgets.QMessageBox.information(self, "完了", message)
        else:
            QtWidgets.QMessageBox.warning(self, "失敗", message)
