#!/usr/bin/python3

import os
import sys
import glob
import signal
import subprocess

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,  
    QLineEdit, QPushButton, QLabel, QToolBar, QStatusBar, QGridLayout, 
    QAction, QMessageBox, QFileDialog, QHeaderView, QWidget, QSizePolicy
)
from PyQt5.QtCore import Qt, QDir, QSize, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices


# Import do diálogo
from list_data_tools.dialog_configuration import DialogConfiguration


import list_data_tools.about as about
import list_data_tools.modules.configure as configure 
from list_data_tools.modules.resources import resource_path

from list_data_tools.modules.wabout    import show_about_window
from list_data_tools.desktop import create_desktop_file, create_desktop_directory, create_desktop_menu

# ---------- Path to config file ----------
CONFIG_PATH = os.path.join( os.path.expanduser("~"),
                            ".config", 
                            about.__package__, 
                            "config.json" )

DEFAULT_CONTENT={   
    "toolbar_configure": "Configure",
    "toolbar_configure_tooltip": "Open the configure Json file of program GUI",
    "toolbar_about": "About",
    "toolbar_about_tooltip": "About the program",
    "toolbar_coffee": "Coffee",
    "toolbar_coffee_tooltip": "Buy me a coffee (TrucomanX)",
    "window_width": 1024,
    "window_height": 800,
    "input_label":"Root directory:",
    "input_lineedit_placeholder": "/path/to/input/directory",
    "input_lineedit_tooltip": "Directory where the files will be searched",
    "input_button": "Select Input",
    "input_button_tooltip": "Select a directory where the files will be searched",
    "filter_label": "Filter filetype:",
    "filter_lineedit": "*.jpg",
    "filter_lineedit_placeholder": "*.png",
    "filter_lineedit_tooltip": "The extension file to be searched",
    "output_label": "Output file path:",
    "output_lineedit_placeholder": "/path/to/output/filename.listfiles",
    "output_lineedit_tooltip": "File where the files will be stored",
    "output_button": "Select Output",
    "output_button_tooltip": "Select the file where the files will be stored",
    "search_button": "Search",
    "search_button_tooltip": "Start the search for files.",
}

configure.verify_default_config(CONFIG_PATH,default_content=DEFAULT_CONTENT)

CONFIG=configure.load_config(CONFIG_PATH)

# ---------------------------------------



# Constantes (ajuste conforme seu projeto)
APP_TARGET = "ListFiles"
APP_VERSION = "1.0"
APP_HOMEPAGE = "https://github.com/seuusuario/listfiles"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(about.__program_files__)
        self.resize(CONFIG["window_width"], CONFIG["window_height"])
        
        ## Icon
        # Get base directory for icons
        self.icon_path = resource_path("icons", "logo.png")
        self.setWindowIcon(QIcon(self.icon_path)) 

        self.SORTDATATYPE = 0  # 0 = SORT_LEX, 1 = SORT_LENGTH
        self.progpath = os.path.realpath(sys.argv[0])
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
        self.label_rootdir = QLabel(CONFIG["input_label"])
        self.lineEdit_rootdir = QLineEdit()
        self.lineEdit_rootdir.setPlaceholderText(CONFIG["input_lineedit_placeholder"])
        self.lineEdit_rootdir.setToolTip(CONFIG["input_lineedit_tooltip"])
        self.pushButton_rootdir = QPushButton(CONFIG["input_button"])
        self.pushButton_rootdir.setIcon(QIcon(resource_path("icons", "folder-saved-search.svg")))
        self.pushButton_rootdir.setToolTip(CONFIG["input_button_tooltip"])
        self.pushButton_rootdir.clicked.connect(self.on_pushButton_rootdir_clicked)

        # Filter
        self.label_filter = QLabel(CONFIG["filter_label"])
        self.lineEdit_filter = QLineEdit(CONFIG["filter_lineedit"])
        self.lineEdit_filter.setPlaceholderText(CONFIG["filter_lineedit_placeholder"])
        self.lineEdit_filter.setToolTip(CONFIG["filter_lineedit_tooltip"])


        # Output file
        self.label_outfile = QLabel(CONFIG["output_label"])
        self.lineEdit_outfile = QLineEdit()
        self.lineEdit_outfile.setPlaceholderText(CONFIG["output_lineedit_placeholder"])
        self.lineEdit_outfile.setToolTip(CONFIG["output_lineedit_tooltip"])
        self.pushButton_outfile = QPushButton(CONFIG["output_button"])
        self.pushButton_outfile.setIcon(QIcon(resource_path("icons", "listfiles.svg")))
        self.pushButton_outfile.setToolTip(CONFIG["output_button_tooltip"])
        self.pushButton_outfile.clicked.connect(self.on_pushButton_outfile_clicked)

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


        # Search
        self.pushButton_search = QPushButton(CONFIG["search_button"])
        self.pushButton_search.setToolTip(CONFIG["search_button_tooltip"])
        self.pushButton_search.setIcon(QIcon(resource_path("icons", "gtk-zoom-fit.svg")))
        self.pushButton_search.setIconSize(QSize(32, 32))
        self.pushButton_search.clicked.connect(self.on_pushButton_search_clicked)
        layout.addWidget(self.pushButton_search)


        # === Tabela ===
        self.tableWidget = QTableWidget()

        self.tableWidget.setColumnCount(1)
        self.tableWidget.setHorizontalHeaderLabels(["filepath"])

        self.tableWidget.setSortingEnabled(True)

        self.tableWidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)

        self.tableWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.tableWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        

        layout.addWidget(self.tableWidget)


        # === Rodapé com número de arquivos ===
        footer = QHBoxLayout()
        
        footer.addWidget(QLabel("Number of files:"))
        self.label_nfiles = QLabel("0")
        self.label_nfiles.setStyleSheet("font-weight: bold;")
        footer.addWidget(self.label_nfiles)
        
        
        self.pushButton_deleterow = QPushButton("Remove rows")
        self.pushButton_deleterow.setIcon(QIcon(resource_path("icons", "edit-rem.png")))
        self.pushButton_deleterow.clicked.connect(self.on_pushButton_deleterow_clicked)
        self.pushButton_deleterow.setIconSize(QSize(32, 32))
        footer.addWidget(self.pushButton_deleterow)
        
        footer.addStretch()
        
        self.pushButton_saveexit = QPushButton("Save files and Exit")
        self.pushButton_saveexit.setIcon(QIcon(resource_path("icons", "Gnome-media-floppy.png")))
        self.pushButton_saveexit.clicked.connect(self.on_pushButton_saveexit_clicked)
        self.pushButton_saveexit.setIconSize(QSize(32, 32))
        footer.addWidget(self.pushButton_saveexit)
        
        layout.addLayout(footer)

        # Conexões



    def create_actions(self):
        self.actionSave_files = QAction(
            QIcon(resource_path("icons", "Gnome-media-floppy.png")), "&Save files", self)
        self.actionSave_files.setShortcut("Ctrl+S")
        self.actionSave_files.triggered.connect(self.on_actionSave_files_triggered)

        self.actionConfiguration = QAction(
            QIcon(resource_path("icons", "if_tools_1054957.png")), "&Configuration", self)
        self.actionConfiguration.setShortcut("Ctrl+T")
        self.actionConfiguration.triggered.connect(self.on_actionConfiguration_triggered)

        self.actionAbout = QAction(
            QIcon(resource_path("icons", "Information_icon.png")), "About this program", self)
        self.actionAbout.triggered.connect(self.on_actionAbout_triggered)

    def create_menus(self):
        menubar = self.menuBar()
        menu_file = menubar.addMenu("&Menu")
        menu_file.addAction(self.actionSave_files)

        menu_about = menubar.addMenu("Abo&ut")
        menu_about.addAction(self.actionAbout)


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
        """Busca recursiva de arquivos conforme o filtro"""
        rootdir = self.lineEdit_rootdir.text().strip()
        filter_pattern = self.lineEdit_filter.text().strip()

        if not rootdir or not os.path.isdir(rootdir):
            QMessageBox.warning(self, "Erro", "Diretório raiz inválido ou não existe!")
            return

        if not filter_pattern:
            filter_pattern = "*.*"

        if not filter_pattern.startswith("*"):
            filter_pattern = f"*{filter_pattern}"

        # Limpa a tabela e desativa ordenação temporariamente
        self.tableWidget.setSortingEnabled(False)  # Evita problemas durante preenchimento
        self.tableWidget.setRowCount(0)

        files_found = []

        try:
            search_pattern = os.path.join(rootdir, "**", filter_pattern)
            files_found = glob.glob(search_pattern, recursive=True)
            files_found = [f for f in files_found if os.path.isfile(f)]

            # Ordenação inicial conforme configuração do programa
            if self.SORTDATATYPE == 0:  # SORT_LEX
                files_found.sort(key=lambda x: x.lower())
            elif self.SORTDATATYPE == 1:  # SORT_LENGTH
                files_found.sort(key=lambda x: (len(os.path.basename(x)), os.path.basename(x).lower()))

            # Preenche a tabela
            self.tableWidget.setRowCount(len(files_found))

            for i, filepath in enumerate(files_found):
                item = QTableWidgetItem(filepath)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.tableWidget.setItem(i, 0, item)
            self.tableWidget.resizeColumnToContents(0)

        except Exception as e:
            QMessageBox.critical(self, "Erro na busca", f"Ocorreu um erro:\n{str(e)}")

        finally:
            self.tableWidget.setSortingEnabled(True)  # Reativa ordenação

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

    def on_actionAbout_triggered(self):
        QMessageBox.about(self, "About the program",
                          f"<center><b>{APP_TARGET}</b></center><br>"
                          f"<b>version:</b> {APP_VERSION}<br>"
                          f"<b>license:</b> GPL<br>"
                          f"<b>homepage:</b> <a href='{APP_HOMEPAGE}'>{APP_HOMEPAGE}</a><br>"
                          f"<b>author:</b> Fernando Pujaico Rivera")



def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    
