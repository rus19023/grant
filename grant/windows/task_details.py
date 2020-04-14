""" Detail View for a plan """

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QLabel, QLineEdit, QTextEdit, QGroupBox
from PyQt5.QtWidgets import QDataWidgetMapper
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QInputDialog
from grant.research import ResearchResult
from .base_screens import DetailScreen
from .result_dialog import ResultDialog


class TaskDetails(DetailScreen):
    """ Displays all current Research Plans """
    plan_changed = pyqtSignal()

    def __init__(self, model):
        super(TaskDetails, self).__init__(model)

        #from PyQt5.QtWidgets import QComboBox
        #from PyQt5.QtCore import QStringListModel
        # self.status_model = QStringListModel(
        #     ["active", "completed", "abandoned"])
        # self.status = QComboBox()
        # self.status.setModel(self.status_model)
        # self.mapper.addMapping(self.status, 2, b"currentText")

        form_layout = QFormLayout()
        self.source = QLineEdit()
        form_layout.addRow(QLabel("Source:"), self.source)

        self.description = QTextEdit()
        form_layout.addRow(QLabel("Description:"), self.description)

        result_box = QHBoxLayout()
        self.result = QLineEdit()
        self.result.setReadOnly(True)
        self.more_action = QAction(QIcon(":/icons/more.ico"), "more")
        self.more_action.triggered.connect(self.show_result_dialog)
        self.result.addAction(self.more_action, self.result.TrailingPosition)
        result_box.addWidget(self.result)

        self.result_nil = QPushButton("Nil")
        self.result_nil.pressed.connect(lambda: self.record_result(False))
        result_box.addWidget(self.result_nil)
        self.result_success = QPushButton("Success")
        self.result_success.pressed.connect(lambda: self.record_result(True))
        result_box.addWidget(self.result_success)

        form_layout.addRow(QLabel("Results:"), result_box)

        form_group = QGroupBox("Task")
        form_group.setLayout(form_layout)

        layout = QVBoxLayout()
        layout.addWidget(form_group)

        self.setLayout(layout)

        self.mapper = QDataWidgetMapper()
        self.mapper.setModel(self.data_model)
        self.mapper.addMapping(self.source, 0)
        self.mapper.addMapping(self.description, 1)
        self.mapper.addMapping(self.result, 2)
        self.mapper.toFirst()
        self.mapper.currentIndexChanged.connect(self.item_selected)

    def item_selected(self, index: int):
        """ Triggered when the selected item changes """
        task = self.data_model.index(
            index, 0, self.mapper.rootIndex()).internalPointer().data
        self.result.setVisible(task.result is not None)
        self.result_nil.setVisible(task.result is None)
        self.result_success.setVisible(task.result is None)

    def record_result(self, success: bool):
        """ Records a result """
        task = self.data_model.index(
            self.mapper.currentIndex(), 0, self.mapper.rootIndex()).internalPointer().data

        summary, ok_pressed = QInputDialog.getText(self,
                                                   "Summary", "Enter a summary of your findings")
        if ok_pressed:
            task.result = ResearchResult(success)
            task.result.summary = summary

        self.mapper.setCurrentIndex(self.mapper.currentIndex())

    def show_result_dialog(self):
        """ Opens the result dialog """
        index = self.data_model.index(
            self.mapper.currentIndex(), 0, self.mapper.rootIndex())
        task = index.internalPointer().data

        dialog = ResultDialog(task.result)
        if dialog.exec():
            self.data_model.update_result(index, dialog.result)
