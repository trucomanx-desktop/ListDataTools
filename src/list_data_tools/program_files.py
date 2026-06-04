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
    "menubar_menu": "&Menu",
    "menubar_about": "Abo&ut",
    "toolbar_save": "&Save files",
    "toolbar_save_tooltip": "Save the *.listfiles file",
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
    "nfiles_label": "Number of files:",
    "nfiles_tooltip": "Number of files in the list of files",
    "deleterow_button": "Remove rows",
    "deleterow_button_tooltip": "Delete a selected file path from the list of files.",
    "saveexit_button": "Save and Exit",
    "saveexit_button_tooltip": "Save files and Exit",
    "msg_error": "Error",
    "msg_error_invalid_dir": "Diretório raiz inválido ou não existe!",
    "msg_select_root": "Select root directory",
    "msg_select_outfile": "Select or define an output filename",
    "msg_error_no_file": "Output file not defined!",
    "msg_files_written": "files was written in",
    "msg_sucess": "Success",
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
        self.create_toolbar()
        self.create_menus()


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
        

        
        footer.addWidget(QLabel(CONFIG["nfiles_label"]))
        self.label_nfiles = QLabel("0")
        self.label_nfiles.setToolTip(CONFIG["nfiles_tooltip"])
        self.label_nfiles.setStyleSheet("font-weight: bold;")
        footer.addWidget(self.label_nfiles)
        
        
        self.pushButton_deleterow = QPushButton(CONFIG["deleterow_button"])
        self.pushButton_deleterow.setToolTip(CONFIG["deleterow_button_tooltip"])
        self.pushButton_deleterow.setIcon(QIcon(resource_path("icons", "edit-rem.svg")))
        self.pushButton_deleterow.clicked.connect(self.on_pushButton_deleterow_clicked)
        self.pushButton_deleterow.setIconSize(QSize(32, 32))
        footer.addWidget(self.pushButton_deleterow)
        
        footer.addStretch()
        
        self.pushButton_saveexit = QPushButton(CONFIG["saveexit_button"])
        self.pushButton_saveexit.setToolTip(CONFIG["saveexit_button_tooltip"])
        self.pushButton_saveexit.setIcon(QIcon(resource_path("icons", "Gnome-media-floppy.png")))
        self.pushButton_saveexit.clicked.connect(self.on_pushButton_saveexit_clicked)
        self.pushButton_saveexit.setIconSize(QSize(32, 32))
        footer.addWidget(self.pushButton_saveexit)
        
        layout.addLayout(footer)


    def create_toolbar(self):
        self.toolbar = self.addToolBar("Main")
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
    
        # Save files
        self.actionSave_files = QAction(QIcon(resource_path("icons", "Gnome-media-floppy.png")), 
                                        CONFIG["toolbar_save"], 
                                        self)
        self.actionSave_files.setToolTip(CONFIG["toolbar_save_tooltip"])
        self.actionSave_files.setShortcut("Ctrl+S")
        self.actionSave_files.triggered.connect(self.on_actionSave_files_triggered)
        self.toolbar.addAction(self.actionSave_files)
        
        
        # Adicionar o espaçador
        self.toolbar_spacer = QWidget()
        self.toolbar_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.toolbar.addWidget(self.toolbar_spacer)
        
        
        # Configure
        self.configure_action = QAction(QIcon(resource_path("icons", "text-configure.svg")),
                                        CONFIG["toolbar_configure"], 
                                        self)
        self.configure_action.setToolTip(CONFIG["toolbar_configure_tooltip"])
        self.configure_action.triggered.connect(self.open_configure_editor)
        self.toolbar.addAction(self.configure_action)
        
        
        # About
        self.about_action = QAction(QIcon(resource_path("icons", "Information_icon.svg")),
                                    CONFIG["toolbar_about"], 
                                    self)
        self.about_action.setToolTip(CONFIG["toolbar_about_tooltip"])
        self.about_action.triggered.connect(self.open_about)
        self.toolbar.addAction(self.about_action)
        
        
        # Coffee
        self.coffee_action = QAction(   QIcon(resource_path("icons", "emote-love.png")),
                                        CONFIG["toolbar_coffee"], 
                                        self)
        self.coffee_action.setToolTip(CONFIG["toolbar_coffee_tooltip"])
        self.coffee_action.triggered.connect(self.on_coffee_action_click)
        self.toolbar.addAction(self.coffee_action)

        
        # Conectar ao sinal de mudança de orientação
        self.toolbar.orientationChanged.connect(self.on_update_spacer_policy)
        self.on_update_spacer_policy()


    def create_menus(self):
        menubar = self.menuBar()
        
        menu_file = menubar.addMenu(CONFIG["menubar_menu"])
        menu_file.addAction(self.actionSave_files)

        menu_about = menubar.addMenu(CONFIG["menubar_about"])
        menu_about.addAction(self.about_action)
        

    def on_update_spacer_policy(self):
        """Atualiza a política do espaçador baseado na orientação da toolbar"""
        if self.toolbar.orientation() == Qt.Horizontal:
            # Horizontal: expande na largura
            self.toolbar_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        else:
            # Vertical: expande na altura
            self.toolbar_spacer.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

    def _open_file_in_text_editor(self, filepath):
        if os.name == 'nt':  # Windows
            os.startfile(filepath)
        elif os.name == 'posix':  # Linux/macOS
            subprocess.run(['xdg-open', filepath])
            
    def open_configure_editor(self):
        self._open_file_in_text_editor(CONFIG_PATH)

    def open_about(self):
        data={
            "version": about.__version__,
            "package": about.__package__,
            "program_name": about.__program_files__,
            "author": about.__author__,
            "email": about.__email__,
            "description": about.__description__,
            "url_source": about.__url_source__,
            "url_doc": about.__url_doc__,
            "url_funding": about.__url_funding__,
            "url_bugs": about.__url_bugs__
        }
        show_about_window(data,self.icon_path)

    def on_coffee_action_click(self):
        QDesktopServices.openUrl(QUrl("https://ko-fi.com/trucomanx"))


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
            QMessageBox.warning(self, CONFIG["msg_error"], CONFIG["msg_error_invalid_dir"])
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
            QMessageBox.critical(self, CONFIG["msg_error"], f"{str(e)}")

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
        dir_ = QFileDialog.getExistingDirectory(self, CONFIG["msg_select_root"],
                                                self.lineEdit_rootdir.text())
        if dir_:
            self.lineEdit_rootdir.setText(dir_)

    def on_pushButton_outfile_clicked(self):
        start = self.lineEdit_outfile.text() or os.path.join(QDir.homePath(), "data.listfiles")
        fileName, _ = QFileDialog.getSaveFileName(
            self, 
            CONFIG["msg_select_outfile"],
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
            QMessageBox.warning(self, CONFIG["msg_error"], CONFIG["msg_error_no_file"] )
            return False

        try:
            with open(outfile, "w", encoding="utf-8") as f:
                for row in range(self.tableWidget.rowCount()):
                    item = self.tableWidget.item(row, 0)
                    if item:
                        f.write(item.text() + "\n")

            n = self.tableWidget.rowCount()
            msg = CONFIG["msg_files_written"] 
            msg = f"[OK] {n} {msg} {outfile}"
            QMessageBox.information(self, CONFIG["msg_sucess"], msg)
            self.statusBar().showMessage(msg, 5000)
            return True
        except Exception as e:
            QMessageBox.critical(self, CONFIG["msg_error"], f"{outfile}\n\n{str(e)}")
            return False

    def on_actionSave_files_triggered(self):
        self.save_in_outfile()


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
       
    extras="" 
    
    create_desktop_directory()    
    create_desktop_menu()
    create_desktop_file(os.path.join("~",".local","share","applications"), 
                        program_name=about.__program_files__,
                        extras=extras)
    
    for n in range(len(sys.argv)):
        if sys.argv[n] == "--autostart":
            create_desktop_directory(overwrite = True)
            create_desktop_menu(overwrite = True)
            create_desktop_file(os.path.join("~",".config","autostart"), 
                                overwrite=True, 
                                program_name=about.__program_files__,
                                extras=extras)
            return
        if sys.argv[n] == "--applications":
            create_desktop_directory(overwrite = True)
            create_desktop_menu(overwrite = True)
            create_desktop_file(os.path.join("~",".local","share","applications"), 
                                overwrite=True, 
                                program_name=about.__program_files__,
                                extras=extras)
            return
    
    app = QApplication(sys.argv)
    app.setApplicationName(about.__program_files__) 
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    
