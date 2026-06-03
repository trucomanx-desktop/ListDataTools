#!/usr/bin/python3

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QLineEdit, QPushButton, QLabel, QToolBar, QStatusBar,
    QAction, QMessageBox, QFileDialog, QHeaderView
)
from PyQt5.QtCore import Qt, QDir
from PyQt5.QtGui import QIcon

# Import do diálogo
from dialog_configuration import DialogConfiguration

# Constantes (ajuste conforme seu projeto)
APP_TARGET = "ListFiles"
APP_VERSION = "1.0"
APP_HOMEPAGE = "https://github.com/seuusuario/listfiles"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_TARGET} {APP_VERSION}")
        self.resize(825, 569)

        self.SORTDATATYPE = 0  # 0 = SORT_LEX, 1 = SORT_LENGTH
        self.progpath = ""
        self.progdir = ""

        self.dis_rootdir = False
        self.dis_filter = False
        self.dis_outfile = False

        self.setup_ui()
        self.create_actions()
        self.create_menus()
        self.create_toolbar()

    def setup_ui(self):
        # Central Widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # === Formulário superior ===
        form_layout = QGridLayout()
        form_layout.setColumnStretch(1, 1)

        # Root Directory
        self.label_rootdir = QLabel("Root directory:")
        self.lineEdit_rootdir = QLineEdit()
        self.pushButton_rootdir = QPushButton("...")
        self.pushButton_rootdir.setIcon(QIcon(os.path.join("icons", "folder-saved-search.png")))
        self.pushButton_rootdir.setFixedSize(30, 30)

        # Filter
        self.label_filter = QLabel("Filter filetype:")
        self.lineEdit_filter = QLineEdit()

        # Output file
        self.label_outfile = QLabel("Output file path:")
        self.lineEdit_outfile = QLineEdit()
        self.pushButton_outfile = QPushButton("...")
        self.pushButton_outfile.setIcon(QIcon(os.path.join("icons", "listfiles.png")))
        self.pushButton_outfile.setFixedSize(30, 30)

        # Adiciona ao grid
        form_layout.addWidget(self.label_rootdir, 0, 0)
        form_layout.addWidget(self.lineEdit_rootdir, 0, 1)
        form_layout.addWidget(self.pushButton_rootdir, 0, 2)

        form_layout.addWidget(self.label_filter, 1, 0)
        form_layout.addWidget(self.lineEdit_filter, 1, 1)

        form_layout.addWidget(self.label_outfile, 2, 0)
        form_layout.addWidget(self.lineEdit_outfile, 2, 1)
        form_layout.addWidget(self.pushButton_outfile, 2, 2)

        layout.addLayout(form_layout)

        # === Botões de ação ===
        btn_layout = QHBoxLayout()
        self.pushButton_search = QPushButton("Search")
        self.pushButton_search.setIcon(QIcon(os.path.join("icons", "gtk-zoom-fit.png")))
        self.pushButton_search.setIconSize(QSize(24, 24))

        self.pushButton_deleterow = QPushButton("Remove rows")
        self.pushButton_deleterow.setIcon(QIcon(os.path.join("icons", "edit-rem.png")))
        self.pushButton_deleterow.setIconSize(QSize(24, 24))

        self.pushButton_saveexit = QPushButton("Save files and Exit")
        self.pushButton_saveexit.setIcon(QIcon(os.path.join("icons", "Gnome-media-floppy.png")))
        self.pushButton_saveexit.setIconSize(QSize(32, 32))

        btn_layout.addWidget(self.pushButton_search)
        btn_layout.addWidget(self.pushButton_deleterow)
        btn_layout.addStretch()
        btn_layout.addWidget(self.pushButton_saveexit)

        layout.addLayout(btn_layout)

        # === Tabela ===
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setHorizontalHeaderLabels(["filepath"])
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tableWidget)

        # === Rodapé com número de arquivos ===
        footer = QHBoxLayout()
        footer.addWidget(QLabel("Number of files:"))
        self.label_nfiles = QLabel("0")
        self.label_nfiles.setStyleSheet("font-weight: bold;")
        footer.addWidget(self.label_nfiles)
        footer.addStretch()
        layout.addLayout(footer)

        # Conexões
        self.pushButton_search.clicked.connect(self.on_pushButton_search_clicked)
        self.pushButton_deleterow.clicked.connect(self.on_pushButton_deleterow_clicked)
        self.pushButton_rootdir.clicked.connect(self.on_pushButton_rootdir_clicked)
        self.pushButton_outfile.clicked.connect(self.on_pushButton_outfile_clicked)
        self.pushButton_saveexit.clicked.connect(self.on_pushButton_saveexit_clicked)

    def create_actions(self):
        self.actionSave_files = QAction(
            QIcon(os.path.join("icons", "Gnome-media-floppy.png")), "&Save files", self)
        self.actionSave_files.setShortcut("Ctrl+S")
        self.actionSave_files.triggered.connect(self.on_actionSave_files_triggered)

        self.actionConfiguration = QAction(
            QIcon(os.path.join("icons", "if_tools_1054957.png")), "&Configuration", self)
        self.actionConfiguration.setShortcut("Ctrl+T")
        self.actionConfiguration.triggered.connect(self.on_actionConfiguration_triggered)

        self.actionTutorial = QAction(
            QIcon(os.path.join("icons", "if_document_1055071.png")), "&Tutorial", self)
        self.actionTutorial.setShortcut("Ctrl+H")
        self.actionTutorial.triggered.connect(self.on_actionTutorial_triggered)

        self.actionAbout = QAction(
            QIcon(os.path.join("icons", "Information_icon.png")), "About this program", self)
        self.actionAbout.triggered.connect(self.on_actionAbout_triggered)

        self.actionAboutQt = QAction(
            QIcon(os.path.join("icons", "Information_icon.png")), "About QT libs", self)
        self.actionAboutQt.triggered.connect(self.on_actionAbout_QT_libs_triggered)

    def create_menus(self):
        menubar = self.menuBar()
        menu_file = menubar.addMenu("&Menu")
        menu_file.addAction(self.actionSave_files)

        menu_doc = menubar.addMenu("&Documentation")
        menu_doc.addAction(self.actionTutorial)

        menu_about = menubar.addMenu("Abo&ut")
        menu_about.addAction(self.actionAbout)
        menu_about.addAction(self.actionAboutQt)

    def create_toolbar(self):
        toolbar = QToolBar()
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.addToolBar(toolbar)

        toolbar.addAction(self.actionSave_files)
        toolbar.addAction(self.actionConfiguration)

    # ==================== Métodos Originais ====================

    def set_parameter_progpath(self, ppath):
        self.progpath = ppath

    def set_parameter_progdir(self, pdir):
        self.progdir = pdir

    def set_parameter_rootdir(self, rootdir, dis_rootdir):
        self.dis_rootdir = bool(dis_rootdir)
        self.lineEdit_rootdir.setText(rootdir)
        self.lineEdit_rootdir.setEnabled(not self.dis_rootdir)
        self.pushButton_rootdir.setEnabled(not self.dis_rootdir)

    def set_parameter_filter(self, filter_str, dis_filter):
        self.dis_filter = bool(dis_filter)
        self.lineEdit_filter.setText(filter_str)
        self.lineEdit_filter.setEnabled(not self.dis_filter)

    def set_parameter_outfile(self, outfile, dis_outfile):
        self.dis_outfile = bool(dis_outfile)
        self.lineEdit_outfile.setText(outfile)
        self.lineEdit_outfile.setEnabled(not self.dis_outfile)
        self.pushButton_outfile.setEnabled(not self.dis_outfile)

    def set_nfiles(self):
        n = self.tableWidget.rowCount()
        self.label_nfiles.setText(str(n))
        return n

    def search_files(self):
        # Aqui você deve implementar a lógica de busca usando pdsdatafunc ou outra biblioteca
        # Por enquanto, deixo como placeholder
        rootdir = self.lineEdit_rootdir.text()
        filter_ = self.lineEdit_filter.text()

        # Exemplo placeholder:
        self.tableWidget.setRowCount(0)
        # ... sua lógica de busca aqui ...

        self.set_nfiles()

    # Slots
    def on_pushButton_search_clicked(self):
        self.search_files()

    def on_pushButton_deleterow_clicked(self):
        for row in reversed(range(self.tableWidget.rowCount())):
            if self.tableWidget.item(row, 0).isSelected():
                self.tableWidget.removeRow(row)
        self.set_nfiles()

    def on_pushButton_rootdir_clicked(self):
        dir_ = QFileDialog.getExistingDirectory(self, "Select root directory",
                                                self.lineEdit_rootdir.text())
        if dir_:
            self.lineEdit_rootdir.setText(dir_)

    def on_pushButton_outfile_clicked(self):
        start = self.lineEdit_outfile.text() or os.path.join(QDir.homePath(), "listfilesdat.listfiles")
        fileName, _ = QFileDialog.getSaveFileName(
            self, "Select or define an output filename",
            start,
            "Output listfiles file (*.listfiles);;Output data file (*.dat);;All files (*)"
        )
        if fileName:
            self.lineEdit_outfile.setText(fileName)

    def on_pushButton_saveexit_clicked(self):
        self.save_in_outfile()
        if self.set_nfiles() != 0:
            QApplication.quit()

    def save_in_outfile(self):
        outfile = self.lineEdit_outfile.text()
        if not outfile:
            QMessageBox.warning(self, "Error", "Output file not defined!")
            return False

        try:
            with open(outfile, "w", encoding="utf-8") as f:
                for row in range(self.tableWidget.rowCount()):
                    item = self.tableWidget.item(row, 0)
                    if item:
                        f.write(item.text() + "\n")

            n = self.tableWidget.rowCount()
            msg = f"[OK] {n} files was written in {outfile}"
            QMessageBox.information(self, "Success", msg)
            self.statusBar().showMessage(msg, 5000)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Writing the file {outfile}\n\n{str(e)}")
            return False

    def on_actionSave_files_triggered(self):
        self.save_in_outfile()

    def on_actionConfiguration_triggered(self):
        self.statusBar().showMessage("Configuration open", 2000)
        dialog = DialogConfiguration(self)
        dialog.set_lineedit_listfiles_path(self.progpath)
        dialog.set_sort_type([self.SORTDATATYPE])  # lista mutável
        if dialog.exec_():
            self.SORTDATATYPE = dialog.sort_index[0]

    def on_actionTutorial_triggered(self):
        # Implementar abertura do PDF
        pass

    def on_actionAbout_triggered(self):
        QMessageBox.about(self, "About the program",
                          f"<center><b>{APP_TARGET}</b></center><br>"
                          f"<b>version:</b> {APP_VERSION}<br>"
                          f"<b>license:</b> GPL<br>"
                          f"<b>homepage:</b> <a href='{APP_HOMEPAGE}'>{APP_HOMEPAGE}</a><br>"
                          f"<b>author:</b> Fernando Pujaico Rivera")

    def on_actionAbout_QT_libs_triggered(self):
        QMessageBox.aboutQt(self, "Qt :: a cross-platform application framework")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
