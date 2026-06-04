import os
import sys
import math
import random
import signal
import subprocess

from PyQt5.QtCore import Qt, QPoint, QPointF, QSize, QFileInfo, QDir, pyqtSignal, QUrl
from PyQt5.QtGui import (
    QIcon, QPen, QColor, QPixmap, QImage, QPainter, QDesktopServices
)
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QFormLayout, QLabel, QLineEdit, QPushButton, QSpinBox,
    QTabWidget, QSizePolicy, QSpacerItem, QStatusBar, QToolBar,
    QAction, QGraphicsView, QGraphicsScene, QApplication,
    QFileDialog, QMessageBox, QColorDialog
)

import list_data_tools.about as about
import list_data_tools.modules.configure as configure 
from list_data_tools.modules.resources import resource_path

from list_data_tools.modules.wabout    import show_about_window
from list_data_tools.desktop import create_desktop_file, create_desktop_directory, create_desktop_menu


# ---------- Path to config file ----------
CONFIG_PATH = os.path.join( os.path.expanduser("~"),
                            ".config", 
                            about.__package__, 
                            f"config_{about.__program_points__}.json" )

DEFAULT_CONTENT={   
    "toolbar_configure": "Configure",
    "toolbar_configure_tooltip": "Open the configure Json file of program GUI",
    "toolbar_about": "About",
    "toolbar_about_tooltip": "About the program",
    "toolbar_coffee": "Coffee",
    "toolbar_coffee_tooltip": "Buy me a coffee (TrucomanX)",
    "window_width": 1024,
    "window_height": 800
}

configure.verify_default_config(CONFIG_PATH,default_content=DEFAULT_CONTENT)

CONFIG=configure.load_config(CONFIG_PATH)


# ---------------------------------------------------------------------------
# Custom QGraphicsView — emite sinal ao clicar
# ---------------------------------------------------------------------------

class mygraphicsview(QGraphicsView):
    sendMousePosition = pyqtSignal(QPoint)

    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, ev):
        pos = ev.pos()
        if (pos.x() <= self.size().width()) and (pos.y() <= self.size().height()):
            if (pos.x() > 0) and (pos.y() > 0):
                self.sendMousePosition.emit(pos)
        super().mousePressEvent(ev)


# ---------------------------------------------------------------------------
# Helper para ícones
# ---------------------------------------------------------------------------

def _color_icon(color):
    """Cria um ícone 32x32 preenchido com a cor dada."""
    pix = QPixmap(32, 32)
    pix.fill(color)
    icon = QIcon()
    icon.addPixmap(pix, QIcon.Normal, QIcon.On)
    return icon


# ---------------------------------------------------------------------------
# MainWindow
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        
        self.setWindowTitle(about.__program_points__)
        self.resize(CONFIG["window_width"], CONFIG["window_height"])
        
        ## Icon
        # Get base directory for icons
        self.icon_path = resource_path("icons", "listpoints.svg")
        self.setWindowIcon(QIcon(self.icon_path)) 
        

        # --- estado interno ---
        self.NCLICKS = 0
        self.GAUSIAN_CLICKED = False
        self.RANDOM_C1_CLICKED = False
        self.RANDOM_C2_CLICKED = False

        self.pointl = []
        self.color_point  = QColor(255, 0, 0)
        self.color_corner = QColor(0, 255, 0)
        self.pen_point  = QPen(self.color_point)
        self.pen_corner = QPen(self.color_corner)
        self.pen_corner.setWidth(5)

        self.IMAGEH = 0
        self.IMAGEW = 0
        self.progpath = None
        self.progdir  = None
        self.dis_rootimage = 0
        self.dis_outfile   = 0

        self.scene = None  # criado em load_imagefile

        self._setup_ui()
        self._setup_menubar()
        self._setup_toolbar()
        self._setup_statusbar()
        self._connect_signals()

        # inicializa cena vazia e limpa pontos
        self.load_imagefile("")
        self.clear_points()

        # ícones de cor nos botões
        self.pushButton_point_color.setIcon(_color_icon(self.color_point))
        self.pushButton_corner_color.setIcon(_color_icon(self.color_corner))

        self.mainToolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

    # -----------------------------------------------------------------------
    # Construção da UI
    # -----------------------------------------------------------------------

    def _setup_ui(self):

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.verticalLayout_3 = QVBoxLayout(self.centralWidget)
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setContentsMargins(11, 11, 11, 11)

        # --- grid superior: imagem de fundo + ficheiro de saída ---
        self.gridLayout = QGridLayout()
        self.verticalLayout_3.addLayout(self.gridLayout)

        self.label_9 = QLabel("Background image:")
        self.gridLayout.addWidget(self.label_9, 0, 0)

        self.lineEdit_imagefile = QLineEdit()
        self.lineEdit_imagefile.setEnabled(False)
        self.gridLayout.addWidget(self.lineEdit_imagefile, 0, 1)

        self.pushButton_imagefile = QPushButton()
        self.pushButton_imagefile.setIcon(QIcon(resource_path("icons", "folder-saved-search.svg")))
        self.gridLayout.addWidget(self.pushButton_imagefile, 0, 2)

        self.label_10 = QLabel("Output file:")
        self.gridLayout.addWidget(self.label_10, 1, 0)

        self.lineEdit_outfile = QLineEdit()
        self.gridLayout.addWidget(self.lineEdit_outfile, 1, 1)

        self.pushButton_outfile = QPushButton()
        self.pushButton_outfile.setIcon(QIcon(resource_path("icons", "if_compose_1055085.svg")))
        self.gridLayout.addWidget(self.pushButton_outfile, 1, 2)

        # --- meio: graphicsView + tabWidget ---
        self.horizontalLayout_2 = QHBoxLayout()
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.graphicsView = mygraphicsview()
        self.graphicsView.setMouseTracking(False)
        self.horizontalLayout_2.addWidget(self.graphicsView)

        self.tabWidget = QTabWidget()
        self.tabWidget.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.tabWidget.setCurrentIndex(0)
        self.horizontalLayout_2.addWidget(self.tabWidget)

        self._setup_tab_gaussian()
        self._setup_tab_random()

        # --- barra inferior: cores, contagem, guardar/sair ---
        self.horizontalLayout_4 = QHBoxLayout()
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)

        self.pushButton_point_color = QPushButton("Point color")
        self.horizontalLayout_4.addWidget(self.pushButton_point_color)

        self.pushButton_corner_color = QPushButton("Corner color")
        self.horizontalLayout_4.addWidget(self.pushButton_corner_color)

        self.label = QLabel("Total points:")
        self.horizontalLayout_4.addWidget(self.label)

        self.label_npoints = QLabel("0")
        self.horizontalLayout_4.addWidget(self.label_npoints)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.pushButton_saveexit = QPushButton("Save points and Exit")
        self.pushButton_saveexit.setIcon(QIcon(resource_path("icons", "Gnome-media-floppy.png")))
        self.pushButton_saveexit.setIconSize(QSize(48, 48))
        self.horizontalLayout_4.addWidget(self.pushButton_saveexit)

    def _setup_tab_gaussian(self):
        self.tab = QWidget()
        self.tabWidget.addTab(self.tab, "Gaussian")

        self.verticalLayout_2 = QVBoxLayout(self.tab)

        self.formLayout_2 = QFormLayout()
        self.verticalLayout_2.addLayout(self.formLayout_2)

        self.label_4 = QLabel("Number of points:")
        self.spinBox_gaussian_npoints = QSpinBox()
        self.spinBox_gaussian_npoints.setMinimum(1)
        self.spinBox_gaussian_npoints.setMaximum(100000)
        self.spinBox_gaussian_npoints.setValue(200)
        self.formLayout_2.addRow(self.label_4, self.spinBox_gaussian_npoints)

        self.label_5 = QLabel("Radius in pixels:")
        self.spinBox_gaussian_radius = QSpinBox()
        self.spinBox_gaussian_radius.setMinimum(1)
        self.spinBox_gaussian_radius.setMaximum(100000)
        self.spinBox_gaussian_radius.setValue(16)
        self.formLayout_2.addRow(self.label_5, self.spinBox_gaussian_radius)

        self.pushButton_select_gaussian = QPushButton("Select points")
        self.verticalLayout_2.addWidget(self.pushButton_select_gaussian)

    def _setup_tab_random(self):
        self.tab_2 = QWidget()
        self.tabWidget.addTab(self.tab_2, "Random")

        self.verticalLayout_4 = QVBoxLayout(self.tab_2)

        self.formLayout = QFormLayout()
        self.verticalLayout_4.addLayout(self.formLayout)

        sp_exp = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.label_2 = QLabel("Number of points:")
        self.spinBox_random_npoints = QSpinBox()
        self.spinBox_random_npoints.setMinimum(1)
        self.spinBox_random_npoints.setMaximum(100000)
        self.spinBox_random_npoints.setValue(200)
        self.formLayout.addRow(self.label_2, self.spinBox_random_npoints)

        self.pushButton_random_c1 = QPushButton("Select corner 1")
        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.pushButton_random_c1)

        self.label_3 = QLabel("Corner 1 - Line:")
        self.label_3.setSizePolicy(sp_exp)
        self.spinBox_random_c1_line = QSpinBox()
        self.spinBox_random_c1_line.setMaximum(100000)
        self.formLayout.addRow(self.label_3, self.spinBox_random_c1_line)

        self.label_6 = QLabel("Corner 1 - Column:")
        self.label_6.setSizePolicy(sp_exp)
        self.label_6.setLayoutDirection(Qt.RightToLeft)
        self.spinBox_random_c1_column = QSpinBox()
        self.spinBox_random_c1_column.setMaximum(100000)
        self.formLayout.addRow(self.label_6, self.spinBox_random_c1_column)

        self.pushButton_random_c2 = QPushButton("Select corner 2")
        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.pushButton_random_c2)

        self.label_7 = QLabel("Corner 2 - Line:")
        self.spinBox_random_c2_line = QSpinBox()
        self.spinBox_random_c2_line.setMaximum(100000)
        self.formLayout.addRow(self.label_7, self.spinBox_random_c2_line)

        self.label_8 = QLabel("Corner 2 - Column:")
        self.spinBox_random_c2_column = QSpinBox()
        self.spinBox_random_c2_column.setMaximum(100000)
        self.formLayout.addRow(self.label_8, self.spinBox_random_c2_column)

        self.pushButton_select_random = QPushButton("Select points")
        self.verticalLayout_4.addWidget(self.pushButton_select_random)

    def _setup_menubar(self):
        self.menuBar = self.menuBar()
        self.menuBar.setGeometry(0, 0, 790, 25)

        self.actionSave_points = QAction(QIcon(resource_path("icons", "Gnome-media-floppy.png")), "&Save points", self)
        self.actionSave_points.setToolTip("Save the points in the output file")
        self.actionSave_points.setShortcut("Ctrl+S")

        self.actionLoad_points = QAction(QIcon(resource_path("icons", "edit-add.svg")), "&Load points", self)
        self.actionLoad_points.setToolTip("Load the points from the output file")
        self.actionLoad_points.setShortcut("Ctrl+L")

        self.actionRemove_points = QAction(QIcon(resource_path("icons", "edit-rem.svg")), "&Remove points", self)
        self.actionRemove_points.setToolTip("Remove all points")
        self.actionRemove_points.setStatusTip("")
        self.actionRemove_points.setShortcut("Ctrl+R")

        self.actionScreenshot = QAction(QIcon(resource_path("icons", "if_polaroids_1055003.svg")), "S&creenshot", self)
        self.actionScreenshot.setToolTip("Take a screenshot and save the image")
        self.actionScreenshot.setShortcut("Ctrl+T")

        self.actionTutorial = QAction(QIcon(resource_path("icons", "if_document_1055071.svg")), "&Tutorial", self)
        self.actionTutorial.setToolTip("Launch a simple tutorial")
        self.actionTutorial.setShortcut("Ctrl+H")

        self.actionAbout = QAction(QIcon(resource_path("icons", "Information_icon.svg")), "&About this program", self)
        self.actionAbout_QT_libs = QAction(QIcon(resource_path("icons", "Information_icon.svg")), "About &QT libs", self)

        self.menuMenu = self.menuBar.addMenu("&Menu")
        self.menuMenu.addAction(self.actionSave_points)
        self.menuMenu.addAction(self.actionLoad_points)
        self.menuMenu.addAction(self.actionRemove_points)
        self.menuMenu.addAction(self.actionScreenshot)

        self.menuDocumentation = self.menuBar.addMenu("Doc&umentation")
        self.menuDocumentation.addAction(self.actionTutorial)

        self.menuAbout = self.menuBar.addMenu("A&bout")
        self.menuAbout.addAction(self.actionAbout)
        self.menuAbout.addAction(self.actionAbout_QT_libs)

    def _setup_toolbar(self):
        self.mainToolBar = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, self.mainToolBar)
        self.mainToolBar.addAction(self.actionLoad_points)
        self.mainToolBar.addAction(self.actionRemove_points)
        self.mainToolBar.addAction(self.actionSave_points)
        self.mainToolBar.addAction(self.actionScreenshot)

    def _setup_statusbar(self):
        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)

    def _connect_signals(self):
        self.graphicsView.sendMousePosition.connect(self.my_mouse_event)

        self.pushButton_imagefile.clicked.connect(self.on_pushButton_imagefile_clicked)
        self.pushButton_outfile.clicked.connect(self.on_pushButton_outfile_clicked)
        self.pushButton_select_gaussian.clicked.connect(self.on_pushButton_select_gaussian_clicked)
        self.pushButton_select_random.clicked.connect(self.on_pushButton_select_random_clicked)
        self.pushButton_random_c1.clicked.connect(self.on_pushButton_random_c1_clicked)
        self.pushButton_random_c2.clicked.connect(self.on_pushButton_random_c2_clicked)
        self.pushButton_saveexit.clicked.connect(self.on_pushButton_saveexit_clicked)
        self.pushButton_point_color.clicked.connect(self.on_pushButton_point_color_clicked)
        self.pushButton_corner_color.clicked.connect(self.on_pushButton_corner_color_clicked)

        self.actionRemove_points.triggered.connect(self.on_actionRemove_points_triggered)
        self.actionScreenshot.triggered.connect(self.on_actionScreenshot_triggered)
        self.actionLoad_points.triggered.connect(self.on_actionLoad_points_triggered)
        self.actionSave_points.triggered.connect(self.on_actionSave_points_triggered)
        self.actionTutorial.triggered.connect(self.on_actionTutorial_triggered)
        self.actionAbout.triggered.connect(self.on_actionAbout_triggered)
        self.actionAbout_QT_libs.triggered.connect(self.on_actionAbout_QT_libs_triggered)

    # -----------------------------------------------------------------------
    # Métodos públicos (interface C++)
    # -----------------------------------------------------------------------

    def set_parameter_rootimage(self, rootimage, dis_rootimage):
        if self.load_imagefile(rootimage):
            self.dis_rootimage = dis_rootimage
            self.lineEdit_imagefile.setText(rootimage)
            if dis_rootimage == 0:   # PDS_OK == 0
                self.pushButton_imagefile.setDisabled(True)
            else:
                self.pushButton_imagefile.setDisabled(False)

    def set_parameter_outfile(self, outfile, dis_outfile):
        self.dis_outfile = dis_outfile
        self.lineEdit_outfile.setText(outfile)
        if dis_outfile == 0:         # PDS_OK == 0
            self.pushButton_outfile.setDisabled(True)
            self.lineEdit_outfile.setDisabled(True)
        else:
            self.pushButton_outfile.setDisabled(False)
            self.lineEdit_outfile.setDisabled(False)

    def set_parameter_progpath(self, ppath):
        self.progpath = ppath

    def set_parameter_progdir(self, pdir):
        self.progdir = pdir

    # -----------------------------------------------------------------------
    # Lógica principal
    # -----------------------------------------------------------------------

    def rand_norm(self):
        """Número aleatório uniforme em [0, 1)."""
        return random.random()

    def rand_gnorm(self):
        """Número aleatório com distribuição gaussiana (média 0, sigma 1)."""
        return math.sqrt(-2.0 * math.log(max(self.rand_norm(), 1e-300))) * \
               math.cos(2 * math.pi * self.rand_norm())

    def load_imagefile(self, imagefile):
        if self.scene is not None:
            del self.scene

        self.scene = QGraphicsScene(self)
        self.graphicsView.setScene(self.scene)

        pixmap = QPixmap()
        if imagefile and pixmap.load(imagefile):
            self.scene.addPixmap(pixmap)
            self.IMAGEH = pixmap.height()
            self.IMAGEW = pixmap.width()
            self.scene.setSceneRect(0, 0, self.IMAGEW, self.IMAGEH)

            # inicializa cantos do random só se ambos forem zero
            if (self.spinBox_random_c2_line.value() == 0 and
                    self.spinBox_random_c1_line.value() == 0):
                self.spinBox_random_c2_line.setValue(self.IMAGEH - 1)
            if (self.spinBox_random_c2_column.value() == 0 and
                    self.spinBox_random_c1_column.value() == 0):
                self.spinBox_random_c2_column.setValue(self.IMAGEW - 1)

            self.spinBox_random_c1_line.setMaximum(self.IMAGEH - 1)
            self.spinBox_random_c1_column.setMaximum(self.IMAGEW - 1)
            self.spinBox_random_c2_line.setMaximum(self.IMAGEH - 1)
            self.spinBox_random_c2_column.setMaximum(self.IMAGEW - 1)
            return True
        else:
            self.IMAGEH = 0
            self.IMAGEW = 0
            return False

    def clear_points(self):
        self.pointl.clear()
        self.label_npoints.setText("0")

    def plot_point(self, pos, pencil):
        self.scene.addEllipse(pos.x(), pos.y(), 3, 3, pencil)
        return True

    def remap_point(self, pos):
        pf = self.graphicsView.mapToScene(pos)
        return QPoint(int(pf.x()), int(pf.y()))

    def save_in_outfile(self):
        outfile = self.lineEdit_outfile.text()
        if len(outfile) == 0:
            msg = "First you need select the output file."
            QMessageBox.critical(self, "[ERROR]", msg)
            self.statusBar.showMessage(msg, 5000)
            return False

        try:
            with open(outfile, "w") as fd:
                for p in self.pointl:
                    fd.write("%d\t%d\n" % (p.y(), p.x()))

            msg = "[OK] Wrote %d points in the file %s" % (len(self.pointl), outfile)
            QMessageBox.information(self, "Saved", msg)
            self.statusBar.showMessage(msg, 5000)
            return True
        except OSError:
            msg = "Error writing the file %s" % outfile
            QMessageBox.critical(self, "[ERROR]", msg)
            self.statusBar.showMessage(msg, 5000)
            return False

    def load_points(self, string):
        if len(self.lineEdit_imagefile.text()) == 0:
            QMessageBox.critical(self, "[ERROR]", "First need be selected the imagefile.")
            return False

        inputfile = string
        if len(inputfile) == 0:
            if len(self.lineEdit_outfile.text()) != 0:
                origem = QFileInfo(self.lineEdit_outfile.text()).path()
            else:
                origem = QDir.currentPath()

            inputfile = QFileDialog.getOpenFileName(
                self, "Open points file", origem,
                "listpoints file (*.listpoints);;Data file (*.dat);;All files (*.*)"
            )[0]

        if len(inputfile) == 0:
            QMessageBox.critical(self, "[ERROR]", "No input file selected.")
            return False

        self.statusBar.showMessage("Loading the file: " + inputfile, 4000)

        try:
            with open(inputfile, "r") as f:
                content = f.read()
        except OSError:
            QMessageBox.critical(self, "[ERROR]", "Error reading the file %s" % inputfile)
            return False

        tokens = content.split()
        N = len(tokens)

        if N < 2:
            QMessageBox.critical(self, "[ERROR]",
                "They were found %d elements in the input file (Minimum 2)." % N)
            return False

        if N % 2 != 0:
            N -= 1

        for i in range(0, N, 2):
            p = QPoint(int(tokens[i + 1]), int(tokens[i]))   # x=column, y=line
            if p.x() < 0 or p.y() < 0 or p.x() >= self.IMAGEW or p.y() >= self.IMAGEH:
                QMessageBox.critical(self, "[ERROR]",
                    "The point (%d,%d) cannot be added." % (p.y(), p.x()))
            else:
                self.pointl.append(p)
                self.label_npoints.setText(str(len(self.pointl)))
                self.plot_point(p, self.pen_point)

        return True

    # -----------------------------------------------------------------------
    # Slots — botões
    # -----------------------------------------------------------------------

    def on_pushButton_imagefile_clicked(self):
        if len(self.lineEdit_imagefile.text()) != 0:
            origem = self.lineEdit_imagefile.text()
        else:
            origem = QDir.homePath()

        imagefile = QFileDialog.getOpenFileName(
            self, "Open Image File", origem,
            "Images (*.png *.bmp *.jpg)"
        )[0]

        if self.load_imagefile(imagefile):
            self.lineEdit_imagefile.setText(imagefile)
        else:
            self.lineEdit_imagefile.setText("")

    def on_pushButton_outfile_clicked(self):
        if len(self.lineEdit_outfile.text()) != 0:
            origem = QFileInfo(self.lineEdit_outfile.text()).path() + \
                     QDir.separator() + "listpointsdat.listpoints"
        else:
            origem = QDir.homePath() + QDir.separator() + "listpointsdat.listpoints"

        fileName = QFileDialog.getSaveFileName(
            self, "Select or define an output filename", origem,
            "Output listpoints file (*.listpoints);;Output data file (*.dat);;All files (*.*)"
        )[0]
        self.lineEdit_outfile.setText(fileName)

    def on_pushButton_select_gaussian_clicked(self):
        self.NCLICKS = 0
        self.GAUSIAN_CLICKED = True
        self.statusBar.showMessage("Select the central point", 3000)

    def on_pushButton_select_random_clicked(self):
        N  = self.spinBox_random_npoints.value()
        p1 = QPoint(self.spinBox_random_c1_column.value(),
                    self.spinBox_random_c1_line.value())
        p2 = QPoint(self.spinBox_random_c2_column.value(),
                    self.spinBox_random_c2_line.value())

        for _ in range(N):
            while True:
                px = int(self.rand_norm() * (p2.x() - p1.x()) + p1.x())
                py = int(self.rand_norm() * (p2.y() - p1.y()) + p1.y())
                if 0 <= px < self.IMAGEW and 0 <= py < self.IMAGEH:
                    break
            p = QPoint(px, py)
            self.pointl.append(p)
            self.label_npoints.setText(str(len(self.pointl)))
            self.plot_point(p, self.pen_point)

        self.plot_point(p1, self.pen_corner)
        self.plot_point(p2, self.pen_corner)
        self.statusBar.showMessage("Points selected", 3000)

    def on_pushButton_random_c1_clicked(self):
        self.NCLICKS = 0
        self.RANDOM_C1_CLICKED = True
        self.statusBar.showMessage("Select a corner point 1", 3000)

    def on_pushButton_random_c2_clicked(self):
        self.NCLICKS = 0
        self.RANDOM_C2_CLICKED = True
        self.statusBar.showMessage("Select a corner point 2", 3000)

    def on_pushButton_saveexit_clicked(self):
        if self.save_in_outfile():
            QApplication.quit()

    def on_pushButton_point_color_clicked(self):
        color = QColorDialog.getColor(self.color_point, self)
        if color.isValid():
            self.color_point = color
            self.pen_point   = QPen(self.color_point)
            self.pushButton_point_color.setIcon(_color_icon(self.color_point))

    def on_pushButton_corner_color_clicked(self):
        color = QColorDialog.getColor(self.color_corner, self)
        if color.isValid():
            self.color_corner = color
            self.pen_corner   = QPen(self.color_corner)
            self.pen_corner.setWidth(5)
            self.pushButton_corner_color.setIcon(_color_icon(self.color_corner))

    # -----------------------------------------------------------------------
    # Slots — actions
    # -----------------------------------------------------------------------

    def on_actionRemove_points_triggered(self):
        self.statusBar.showMessage(
            "%d points removed" % len(self.pointl), 3000)
        self.clear_points()
        self.load_imagefile(self.lineEdit_imagefile.text())

    def on_actionScreenshot_triggered(self):
        if len(self.lineEdit_outfile.text()) != 0:
            origem = QFileInfo(self.lineEdit_outfile.text()).path() + \
                     QDir.separator() + "screenshot.bmp"
        else:
            origem = QDir.homePath() + QDir.separator() + "screenshot.bmp"

        fileName = QFileDialog.getSaveFileName(
            self, "Define an output [PNG,BMP,JPG] filename", origem,
            "Output image file (*.png *.bmp *.jpg)"
        )[0]

        if not fileName:
            return

        self.scene.clearSelection()
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        image = QImage(self.scene.sceneRect().size().toSize(),
                       QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        self.scene.render(painter)
        painter.end()

        if image.save(fileName, None, 100):
            self.statusBar.showMessage("Wrote the image file: " + fileName, 10000)
        else:
            self.statusBar.showMessage("ERROR:: Could not write the image file: " + fileName, 10000)

    def on_actionLoad_points_triggered(self):
        self.load_points("")

    def on_actionSave_points_triggered(self):
        self.save_in_outfile()

    def on_actionTutorial_triggered(self):
        from PyQt5.QtCore import QUrl
        from PyQt5.QtGui import QDesktopServices
        if self.progdir:
            path = os.path.join(self.progdir, "..", "share", "doc",
                                "listpoints", "listpoints.pdf")
            QDesktopServices.openUrl(QUrl(path, QUrl.TolerantMode))

    def on_actionAbout_triggered(self):
        QMessageBox.about(
            self, "About the program",
            "<center><b>ListPoints</b></center><br>"
            "<b>license:</b> GPL<br>"
            "<b>author:</b> Fernando Pujaico Rivera<br>"
            "<b>email:</b> fernando.pujaico.rivera@gmail.com<br>"
        )

    def on_actionAbout_QT_libs_triggered(self):
        QMessageBox.aboutQt(self, "Qt :: a cross-platform application framework")

    # -----------------------------------------------------------------------
    # Slot — evento de rato
    # -----------------------------------------------------------------------

    def my_mouse_event(self, pos):
        self.NCLICKS += 1
        p0 = self.remap_point(pos)

        self.statusBar.showMessage(
            "Line: %d\tColumn: %d" % (p0.y(), p0.x()), 3000)

        def _inside(p):
            return 0 <= p.x() < self.IMAGEW and 0 <= p.y() < self.IMAGEH

        # --- Gaussian ---
        if self.GAUSIAN_CLICKED and self.NCLICKS > 0:
            if _inside(p0):
                self.NCLICKS = 0
                self.GAUSIAN_CLICKED = False

                N      = self.spinBox_gaussian_npoints.value()
                radius = self.spinBox_gaussian_radius.value()

                for _ in range(N):
                    while True:
                        px = int(self.rand_gnorm() * radius + p0.x())
                        py = int(self.rand_gnorm() * radius + p0.y())
                        if 0 <= px < self.IMAGEW and 0 <= py < self.IMAGEH:
                            break
                    p = QPoint(px, py)
                    self.pointl.append(p)
                    self.label_npoints.setText(str(len(self.pointl)))
                    self.plot_point(p, self.pen_point)

                self.plot_point(p0, self.pen_corner)
                self.statusBar.showMessage("Gaussian clicked done", 3000)
            else:
                QMessageBox.warning(self, "Warning",
                    "You need select the point inside the image.")

        # --- Random corner 1 ---
        if self.RANDOM_C1_CLICKED and self.NCLICKS > 0:
            if _inside(p0):
                self.NCLICKS = 0
                self.RANDOM_C1_CLICKED = False
                self.spinBox_random_c1_column.setValue(p0.x())
                self.spinBox_random_c1_line.setValue(p0.y())
                self.statusBar.showMessage("Corner 1 selected", 3000)
            else:
                QMessageBox.warning(self, "Warning",
                    "You need select the point inside the image.")

        # --- Random corner 2 ---
        if self.RANDOM_C2_CLICKED and self.NCLICKS > 0:
            if _inside(p0):
                self.NCLICKS = 0
                self.RANDOM_C2_CLICKED = False
                self.spinBox_random_c2_column.setValue(p0.x())
                self.spinBox_random_c2_line.setValue(p0.y())
                self.statusBar.showMessage("Corner 2 selected", 3000)
            else:
                QMessageBox.warning(self, "Warning",
                    "You need select the point inside the image.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    app = QApplication(sys.argv)

    # Suporte a argumentos de linha de comando idêntico ao main.cpp
    import argparse
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--rootimage",     default="")
    parser.add_argument("--outfile",       default=os.path.join(os.path.expanduser("~"),
                                                                  "listpointsdat.listpoints"))
    parser.add_argument("--dis-rootimage", action="store_true")
    parser.add_argument("--en-rootimage",  action="store_true")
    parser.add_argument("--dis-outfile",   action="store_true")
    parser.add_argument("--en-outfile",    action="store_true")
    args, _ = parser.parse_known_args()

    dis_rootimage = 1   # PDS_WRONG
    dis_outfile   = 1

    if args.rootimage:
        dis_rootimage = 0   # PDS_OK
    if args.dis_rootimage:
        dis_rootimage = 0
    if args.en_rootimage:
        dis_rootimage = 1

    if args.dis_outfile:
        dis_outfile = 0
    if args.en_outfile:
        dis_outfile = 1

    window = MainWindow()
    window.set_parameter_progpath(os.path.abspath(sys.argv[0]))
    window.set_parameter_progdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    window.set_parameter_rootimage(args.rootimage, dis_rootimage)
    window.set_parameter_outfile(args.outfile, dis_outfile)

    if args.rootimage:
        window.load_points(args.outfile)

    window.show()
    sys.exit(app.exec_())
    
    
if __name__ == "__main__":
    main()
    
