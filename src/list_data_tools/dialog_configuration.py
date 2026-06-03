#!/usr/bin/python3

import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


class DialogConfiguration(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration")
        self.resize(509, 186)
        self.setWindowIcon(QIcon(os.path.join("icons", "if_tools_1054957.png")))

        self.sort_index = None  # será definido via set_sort_type

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Path do programa
        h1 = QHBoxLayout()
        label1 = QLabel("Path of listfiles program:")
        self.lineEdit_listfiles_path = QLineEdit()
        self.lineEdit_listfiles_path.setReadOnly(True)
        h1.addWidget(label1)
        h1.addWidget(self.lineEdit_listfiles_path)
        layout.addLayout(h1)

        # Sort Type
        h2 = QHBoxLayout()
        label2 = QLabel("Result sort type:")
        self.comboBox_sort_type = QComboBox()
        self.comboBox_sort_type.addItem("Ascending lexicographical order")
        self.comboBox_sort_type.addItem("Ascending length; Ascending alphabetical")
        h2.addWidget(label2)
        h2.addWidget(self.comboBox_sort_type)
        layout.addLayout(h2)

        # Spacer
        layout.addStretch()

        # Botão OK
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.pushButton_conf_ok = QPushButton("OK")
        self.pushButton_conf_ok.setMinimumWidth(100)
        btn_layout.addWidget(self.pushButton_conf_ok)
        layout.addLayout(btn_layout)

        # Conexão
        self.pushButton_conf_ok.clicked.connect(self.on_pushButton_conf_ok_clicked)

    def set_lineedit_listfiles_path(self, path: str):
        self.lineEdit_listfiles_path.setText(path)

    def set_sort_type(self, sort_type):
        """sort_type deve ser uma lista ou objeto mutável com [index]"""
        self.sort_index = sort_type
        self.comboBox_sort_type.setCurrentIndex(sort_type[0])

    def on_pushButton_conf_ok_clicked(self):
        if self.sort_index is not None:
            self.sort_index[0] = self.comboBox_sort_type.currentIndex()
        self.accept()
