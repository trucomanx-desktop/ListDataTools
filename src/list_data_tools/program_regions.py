"""
listregions — PyQt5 port
Converte o GUI + lógica completa de C++/Qt para Python/PyQt5.
Uso:
    python mainwindow.py [--rootimage <img>] [--outfile <file>]
                        [--dis-rootimage] [--en-rootimage]
                        [--dis-outfile]   [--en-outfile]
"""

import os
import sys
import signal
import argparse
import subprocess


from PyQt5.QtCore import Qt, QSize, QRectF, pyqtSignal, QUrl, QPoint
from PyQt5.QtGui import QColor, QFont, QIcon, QPen, QPixmap, QPainter, QImage, QDesktopServices
from PyQt5.QtWidgets import (
    QAction, QApplication, QCheckBox, QColorDialog, QFileDialog, QFormLayout, QGraphicsEllipseItem,
    QGraphicsRectItem, QGraphicsScene, QGraphicsView, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMenu, QMenuBar, QMessageBox, QPushButton, QSizePolicy, QSpacerItem, QSpinBox, QStatusBar,
    QTabWidget, QToolBar, QVBoxLayout, QWidget,
)

# ---------------------------------------------------------------------------
# Re-import QtGui.QMouseEvent (it's in QtGui, not a standalone module)
# ---------------------------------------------------------------------------
from PyQt5.QtGui import QMouseEvent  # noqa: F811 — correct location


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
    "toolbar_remove": "Remove regions",
    "toolbar_remove_tooltip": "Remove all regions",
    "toolbar_save": "Save regions",
    "toolbar_save_tooltip": "Save the regions in the output file",
    "toolbar_screenshot": "Screenshot",
    "toolbar_screenshot_tooltip": "Take a screenshot and save the image",
    "toolbar_load": "Load regions",
    "toolbar_load_tooltip": "Load the regions from the output file",
    "toolbar_configure": "Configure",
    "toolbar_configure_tooltip": "Open the configure Json file of program GUI",
    "toolbar_about": "About",
    "toolbar_about_tooltip": "About the program",
    "toolbar_coffee": "Coffee",
    "toolbar_coffee_tooltip": "Buy me a coffee (TrucomanX)",
    "window_width": 1024,
    "window_height": 800,
    "msg_error": "Error",
    "msg_saved": "Saved",
    "msg_warning": "Warning",
    "msg_need_select_output": "First you need select the output file.",
    "msg_wrote_regions": "[OK] Wrote regions in the file:",
    "msg_error_writing": "Error writing the file:",
    "msg_need_select_image": "First you need select the iamge file.",
    "msg_open_regions_file": "Open regions file",
    "msg_loading_file": "Loading the file:",
    "msg_few_elements": "Few elements were found in the input file (minimum 4). Current:",
    "msg_region_not_added_start": "The region cannot be added because it starts at",
    "msg_region_not_added_end": "The region cannot be added because it end at",
    "msg_not_open_file": "Cannot open file:",
    "msg_line": "Line:",
    "msg_column": "Column:",
    "msg_one_by_one": "One by one clicked done",
    "msg_you_need_select_point": "You need select the point so that the entire region will be inside the image.",
    "msg_corner1_selected": "Corner 1 selected",
    "msg_corner2_selected": "Corner 2 selected",
    "msg_need_select_inside": "You need select the point inside the image.",
    "msg_open_image_file": "Open Image File",
    "msg_select_output_file": "Select or define an output filename",
    "msg_select_central_point": "Select the central point",
    "msg_corner1_outside": "The corner 1 is outside the image.",
    "msg_corner2_outside": "The corner 2 is outside the image.",
    "msg_region_selected": "Regions selected",
    "msg_select_corner1": "Select a corner point 1",
    "msg_select_corner2": "Select a corner point 2",
    "msg_regions_removed": "Regions removed:",
    "msg_define_image": "Define an output image file",
    "msg_wrote_image": "Wrote the image file:",
    "msg_image_not_was_wrote": "It was not wrote the image file:",
    "menubar_menu": "&Menu",
    "menubar_about": "A&bout",
    "background_label": "Background image:",
    "background_lineedit_tooltip": "The background image file",
    "background_button": "Select image",
    "background_button_tooltip": "Select the image that will be used as background",
    "output_label": "Output file:",
    "output_lineedit_tooltip": "The ouput file path with the regions",
    "output_button": "Select output",
    "output_button_tooltip": "Select the output file where the regions will be saved",
    "region_mode_label": "Region mode:",
    "region_mode_checkbox": "Use center (instead of corner)",
    "region_mode_checkbox_tooltip": "Define the output format of regions defined by center or northwest corner",
    "tab_one_by_one": "One by one",
    "tab_grid": "Grid",
    "one_by_one_lines_by_regions": "Lines by region:",
    "one_by_one_lines_by_regions_tooltip": "Number of lines in each region",
    "one_by_one_columns_by_regions": "Columns by region:",
    "one_by_one_columns_by_regions_tooltip": "Number of columns in each region",
    "one_by_one_select_points": "Select regions",
    "one_by_one_select_points_tooltip": "Select the region",
    "grid_vertical_regions_label": "Vertical regions:",
    "grid_vertical_regions_tooltip": "<html><head/><body><p>Number of vertical regions</p></body></html>",
    "grid_horizontal_regions_label": "Horizontal regions:",
    "grid_horizontal_regions_tooltip": "<html><head/><body><p>Number of horizontal regions</p></body></html>",
    "grid_select_corner1_button": "Select corner 1",
    "grid_select_corner1_button_tooltip": "Select the corner 1 inside image",
    "grid_select_corner2_button": "Select corner 2",
    "grid_select_corner2_button_tooltip": "Select the corner 2 inside image",
    "grid_corner1_line_label": "Corner 1 - Line:",
    "grid_corner2_line_label": "Corner 2 - Line:",
    "grid_corner1_column_label": "Corner 1 - Column:",
    "grid_corner2_column_label": "Corner 2 - Column:",
    "grid_corner1_line_spin_tooltip": "<html><head/><body><p>Line of corner 1 in grid</p></body></html>",
    "grid_corner2_line_spin_tooltip": "<html><head/><body><p>Line of corner 2 in grid</p></body></html>",
    "grid_corner1_column_spin_tooltip": "<html><head/><body><p>Column of corner 1 in grid</p></body></html>",
    "grid_corner2_column_spin_tooltip": "<html><head/><body><p>Column of corner 2 in grid</p></body></html>",
    "grid_number_lines_label": "Lines by region:",
    "grid_number_columns_label": "Columns by region:",
    "grid_select_regions": "Select regions",
    "grid_select_regions_tooltip": "Select regions in grid format",
    "region_color_button": "Region color",
    "region_color_button_tooltip": "Select the color of region",
    "corner_color_button": "Corner color",
    "corner_color_button_tooltip": "Select the color of corner",
    "total_regions_label": "Total regions:",
    "save_exit_button":"Save regions and Exit",
    "save_exit_button_tooltip":"Save the regions and later close the program",
}

configure.verify_default_config(CONFIG_PATH,default_content=DEFAULT_CONTENT)

CONFIG=configure.load_config(CONFIG_PATH)

# ---------------------------------------




def _solid_icon(color, size=32):
    """Create a solid-colour square icon (used for color buttons)."""
    pm = QPixmap(size, size)
    pm.fill(color)
    ico = QIcon()
    ico.addPixmap(pm, QIcon.Normal, QIcon.On)
    return ico


# ---------------------------------------------------------------------------
# RegionRect — mirrors Pds::RegionRect
# ---------------------------------------------------------------------------
class RegionRect:
    def __init__(self, l0=0, c0=0, nlin=0, ncol=0):
        self._l0   = l0
        self._c0   = c0
        self._nlin = abs(nlin)
        self._ncol = abs(ncol)

    def l0(self):   return self._l0
    def c0(self):   return self._c0
    def nlin(self): return self._nlin
    def ncol(self): return self._ncol

    def __repr__(self):
        return f"RegionRect(l0={self._l0}, c0={self._c0}, nlin={self._nlin}, ncol={self._ncol})"


# ---------------------------------------------------------------------------
# MyGraphicsView — emits mouse-press position (mirrors mygraphicsview)
# ---------------------------------------------------------------------------
class MyGraphicsView(QGraphicsView):
    sendMousePosition = pyqtSignal(object)   # QPoint

    def mousePressEvent(self, ev: QMouseEvent):
        pos = ev.pos()
        if 0 < pos.x() <= self.size().width() and 0 < pos.y() <= self.size().height():
            self.sendMousePosition.emit(pos)
        super().mousePressEvent(ev)


# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # ── state vars (mirrors C++ public members) ──────────────────────
        self.NCLICKS            = 0
        self.ONE_BY_ONE_CLICKED = False
        self.GRID_C1_CLICKED    = False
        self.GRID_C2_CLICKED    = False

        self.pointl_p0 = []          # list of RegionRect

        self.color_point  = QColor(255,   0, 0)
        self.color_corner = QColor(  0, 255, 0)
        self.pen_point    = QPen(self.color_point)
        self.pen_corner   = QPen(self.color_corner)
        self.pen_corner.setWidth(5)

        self.IMAGEH = 0
        self.IMAGEW = 0

        self.progpath = ""
        self.progdir  = ""

        self.dis_rootimage = False   # False = not disabled (enabled)
        self.dis_outfile   = False

        self._scene = None

        # ── build UI ─────────────────────────────────────────────────────
        self.setWindowTitle(about.__program_regions__)
        self.resize(CONFIG["window_width"], CONFIG["window_height"])
        
        ## Icon
        # Get base directory for icons
        self.icon_path = resource_path("icons", "listregions.svg")
        self.setWindowIcon(QIcon(self.icon_path)) 

        #self.setObjectName("MainWindow")

        self._setup_actions()
        
        self._setup_toolbar()
        
        self._setup_menubar()

        self._setup_central_widget()
        self._setup_statusbar()

        # ── post-UI init ─────────────────────────────────────────────────
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        # colour-square icons on the colour buttons
        self.pushButton_point_color.setIcon(_solid_icon(self.color_point))
        self.pushButton_corner_color.setIcon(_solid_icon(self.color_corner))

        self._load_imagefile("")
        self._clear_regions()



        # connect mouse signal
        self.graphicsView.sendMousePosition.connect(self._my_mouse_event)

        # connect spinBox changes → recalculate nlin/ncol
        self.spinBox_grid_nvregions.valueChanged.connect(lambda v: self._calcular_nlin_ncol())
        self.spinBox_grid_nhregions.valueChanged.connect(lambda v: self._calcular_nlin_ncol())
        self.spinBox_grid_c1_line.valueChanged.connect(lambda v: self._calcular_nlin_ncol())
        self.spinBox_grid_c1_column.valueChanged.connect(lambda v: self._calcular_nlin_ncol())
        self.spinBox_grid_c2_line.valueChanged.connect(lambda v: self._calcular_nlin_ncol())
        self.spinBox_grid_c2_column.valueChanged.connect(lambda v: self._calcular_nlin_ncol())

    # ================================================================
    # Public setters (called from main() like C++ set_parameter_*)
    # ================================================================

    def set_parameter_progpath(self, ppath):
        self.progpath = ppath

    def set_parameter_progdir(self, pdir):
        self.progdir = pdir

    def set_parameter_rootimage(self, rootimage, dis_rootimage):
        if self._load_imagefile(rootimage):
            self.dis_rootimage = dis_rootimage
            self.lineEdit_imagefile.setText(rootimage)
            self.pushButton_imagefile.setDisabled(dis_rootimage)

    def set_parameter_outfile(self, outfile, dis_outfile):
        self.dis_outfile = dis_outfile
        self.lineEdit_outfile.setText(outfile)
        self.pushButton_outfile.setDisabled(dis_outfile)
        self.lineEdit_outfile.setDisabled(dis_outfile)

    # ================================================================
    # Core logic helpers
    # ================================================================

    def _calcular_nlin_ncol(self, nlin_out=None, ncol_out=None):
        NV = self.spinBox_grid_nvregions.value()
        NH = self.spinBox_grid_nhregions.value()
        c1x = self.spinBox_grid_c1_column.value()
        c1y = self.spinBox_grid_c1_line.value()
        c2x = self.spinBox_grid_c2_column.value()
        c2y = self.spinBox_grid_c2_line.value()

        NLIN = abs((1 + c2y - c1y) // NV)
        NCOL = abs((1 + c2x - c1x) // NH)

        self.label_grid_nlin.setText(str(NLIN))
        self.label_grid_ncol.setText(str(NCOL))
        return NLIN, NCOL

    def _load_imagefile(self, imagefile):
        if self._scene is not None:
            self._scene.deleteLater()

        self._scene = QGraphicsScene(self)
        self.graphicsView.setScene(self._scene)

        pm = QPixmap()
        if imagefile and pm.load(imagefile):
            self._scene.addPixmap(pm)
            self.IMAGEH = pm.height()
            self.IMAGEW = pm.width()
            self._scene.setSceneRect(0, 0, self.IMAGEW, self.IMAGEH)

            # initialise grid corners to full image when both are 0
            if (self.spinBox_grid_c2_line.value() == 0 and
                    self.spinBox_grid_c1_line.value() == 0):
                self.spinBox_grid_c2_line.setValue(self.IMAGEH - 1)
            if (self.spinBox_grid_c2_column.value() == 0 and
                    self.spinBox_grid_c1_column.value() == 0):
                self.spinBox_grid_c2_column.setValue(self.IMAGEW - 1)

            self.spinBox_grid_c1_line.setMaximum(self.IMAGEH - 1)
            self.spinBox_grid_c1_column.setMaximum(self.IMAGEW - 1)
            self.spinBox_grid_c2_line.setMaximum(self.IMAGEH - 1)
            self.spinBox_grid_c2_column.setMaximum(self.IMAGEW - 1)
            return True
        else:
            self.IMAGEH = 0
            self.IMAGEW = 0
            return False

    def _clear_regions(self):
        self.pointl_p0.clear()
        self.label_nregions.setText("0")

    def _plot_regionrect(self, rr: RegionRect, pen: QPen):
        self._scene.addRect(rr.c0(), rr.l0(), rr.ncol(), rr.nlin(), pen)

    def _plot_point(self, pos, pen: QPen):
        self._scene.addEllipse(pos.x(), pos.y(), 3, 3, pen)

    def _remap_point(self, pos):
        pf = self.graphicsView.mapToScene(pos)
        return pf.toPoint()


    def _save_in_outfile(self):
        outfile = self.lineEdit_outfile.text()
        if not outfile:
            msg = CONFIG["msg_need_select_output"]
            QMessageBox.critical(self, CONFIG["msg_error"], msg)
            self.statusBar.showMessage(msg, 5000)
            return False

        try:
            with open(outfile, "w") as fd:
                for rr in self.pointl_p0:
                    if self.checkBox_corner_center.isChecked():
                        cl = rr.l0() + rr.nlin() // 2
                        cc = rr.c0() + rr.ncol() // 2
                        fd.write(f"{cl}\t{cc}\t{rr.nlin()}\t{rr.ncol()}\n")
                    else:
                        fd.write(f"{rr.l0()}\t{rr.c0()}\t{rr.nlin()}\t{rr.ncol()}\n")
            msg = CONFIG["msg_wrote_regions"] + f" {len(self.pointl_p0)}\n{outfile}"
            QMessageBox.information(self, CONFIG["msg_saved"], msg)
            self.statusBar.showMessage(msg, 5000)
            return True
        except Exception as e:
            
            msg = CONFIG["msg_error_writing"] + f" {outfile}\n{e}"
            QMessageBox.critical(self, CONFIG["msg_error"], msg)
            self.statusBar.showMessage(msg, 5000)
            return False


    def _load_regions(self, filepath=""):
        if not self.lineEdit_imagefile.text():
            QMessageBox.critical(self, CONFIG["msg_error"], CONFIG["msg_need_select_image"])
            return False

        if not filepath:
            start = (os.path.dirname(self.lineEdit_outfile.text())
                     if self.lineEdit_outfile.text() else os.getcwd())
            filepath, _ = QFileDialog.getOpenFileName(
                self, CONFIG["msg_open_regions_file"], 
                start,
                "Data listregions file (*.listregions);;Data file (*.dat);;All files (*.*)"
            )

        if not filepath:
            QMessageBox.critical(self, CONFIG["msg_error"], CONFIG["msg_need_select_image"])
            return False

        self.statusBar.showMessage(CONFIG["msg_loading_file"] + f" {filepath}", 4000)

        try:
            with open(filepath, "r") as f:
                content = f.read()
        except Exception as e:
            
            QMessageBox.critical(self, CONFIG["msg_error"], CONFIG["msg_not_open_file"]+ f" {e}")
            return False

        tokens = content.split()
        N = len(tokens)


        if N < 4:
            QMessageBox.critical(self, CONFIG["msg_error"],
                CONFIG["msg_few_elements"] + f" {N}")
            return False

        N = (N // 4) * 4

        for i in range(0, N, 4):
            l0   = int(tokens[i])
            c0   = int(tokens[i + 1])
            nlin = int(tokens[i + 2])
            ncol = int(tokens[i + 3])

            if self.checkBox_corner_center.isChecked():
                l0 = l0 - nlin // 2
                c0 = c0 - ncol // 2

            if c0 < 0 or l0 < 0 or c0 >= self.IMAGEW or l0 >= self.IMAGEH:
                QMessageBox.critical(self, CONFIG["msg_error"],
                    CONFIG["msg_region_not_added_start"] + f" ({l0},{c0})")
                continue

            if ((c0 + ncol - 1) < 0 or (l0 + nlin - 1) < 0 or
                    (c0 + ncol - 1) >= self.IMAGEW or (l0 + nlin - 1) >= self.IMAGEH):
                QMessageBox.critical(self, CONFIG["msg_error"],
                    CONFIG["msg_region_not_added_end"] + f" ({l0+nlin},{c0+ncol})")
                continue

            rr = RegionRect(l0, c0, nlin, ncol)
            self.pointl_p0.append(rr)
            self.label_nregions.setText(str(len(self.pointl_p0)))
            self._plot_regionrect(rr, self.pen_point)

        return True

    # ================================================================
    # Slot: mouse click on graphicsView
    # ================================================================

    def _my_mouse_event(self, pos):
        self.NCLICKS += 1
        p0 = self._remap_point(pos)

        msg_line=CONFIG["msg_line"]
        msg_column=CONFIG["msg_column"]
        self.statusBar.showMessage(f"{msg_line} {p0.y()}\t{msg_column} {p0.x()}", 3000)

        # ── One-by-one mode ──────────────────────────────────────────
        if self.ONE_BY_ONE_CLICKED and self.NCLICKS > 0:
            if 0 <= p0.x() < self.IMAGEW and 0 <= p0.y() < self.IMAGEH:
                Nlin = self.spinBox_one_by_one_nlin.value()
                Ncol = self.spinBox_one_by_one_ncol.value()
                if (0 <= p0.x() + Ncol - 1 < self.IMAGEW and
                        0 <= p0.y() + Nlin - 1 < self.IMAGEH):
                    self.NCLICKS = 0
                    self.ONE_BY_ONE_CLICKED = False
                    rr = RegionRect(p0.y(), p0.x(), Nlin, Ncol)
                    self.pointl_p0.append(rr)
                    self.label_nregions.setText(str(len(self.pointl_p0)))
                    self._plot_point(p0, self.pen_corner)
                    self._plot_regionrect(rr, self.pen_point)
                    self.statusBar.showMessage(CONFIG["msg_one_by_one"], 3000)
                else:
                    QMessageBox.warning(self, 
                                        CONFIG["msg_warning"],
                                        CONFIG["msg_you_need_select_point"])
            else:
                QMessageBox.warning(self, 
                                    CONFIG["msg_warning"],
                                    CONFIG["msg_you_need_select_point"])

    

        # ── Grid corner 1 ────────────────────────────────────────────
        if self.GRID_C1_CLICKED and self.NCLICKS > 0:
            if 0 <= p0.x() < self.IMAGEW and 0 <= p0.y() < self.IMAGEH:
                self.NCLICKS = 0
                self.GRID_C1_CLICKED = False
                self.spinBox_grid_c1_column.setValue(p0.x())
                self.spinBox_grid_c1_line.setValue(p0.y())
                self.statusBar.showMessage(CONFIG["msg_corner1_selected"], 3000)
            else:
                QMessageBox.warning(self, 
                                    CONFIG["msg_warning"],
                                    CONFIG["msg_need_select_inside"])

        # ── Grid corner 2 ────────────────────────────────────────────
        if self.GRID_C2_CLICKED and self.NCLICKS > 0:
            if 0 <= p0.x() < self.IMAGEW and 0 <= p0.y() < self.IMAGEH:
                self.NCLICKS = 0
                self.GRID_C2_CLICKED = False
                self.spinBox_grid_c2_column.setValue(p0.x())
                self.spinBox_grid_c2_line.setValue(p0.y())
                self.statusBar.showMessage(CONFIG["msg_corner2_selected"], 3000)
            else:
                QMessageBox.warning(self, 
                                    CONFIG["msg_warning"],
                                    CONFIG["msg_need_select_inside"])

    # ================================================================
    # Button slots
    # ================================================================
    
    def _on_pushButton_imagefile_clicked(self):
        start = self.lineEdit_imagefile.text() or os.path.expanduser("~")
        imagefile, _ = QFileDialog.getOpenFileName(
            self, 
            CONFIG["msg_open_image_file"], 
            start,
            "Images (*.png *.bmp *.jpg)")
        if self._load_imagefile(imagefile):
            self.lineEdit_imagefile.setText(imagefile)
        else:
            self.lineEdit_imagefile.setText("")

    def _on_pushButton_outfile_clicked(self):
        if self.lineEdit_outfile.text():
            start = (os.path.dirname(self.lineEdit_outfile.text())
                     + os.sep + "data.listregions")
        else:
            start = os.path.expanduser("~") + os.sep + "data.listregions"

        filename, _ = QFileDialog.getSaveFileName(
            self, 
            CONFIG["msg_select_output_file"], 
            start,
            "Output listregions file (*.listregions);;Output data file (*.dat);;All files (*.*)")
        self.lineEdit_outfile.setText(filename)


    def _on_pushButton_select_one_by_one_clicked(self):
        self.NCLICKS = 0
        self.ONE_BY_ONE_CLICKED = True
        self.statusBar.showMessage(CONFIG["msg_select_central_point"], 3000)

    def _on_pushButton_select_grid_clicked(self):
        NV = self.spinBox_grid_nvregions.value()
        NH = self.spinBox_grid_nhregions.value()
        c1x = self.spinBox_grid_c1_column.value()
        c1y = self.spinBox_grid_c1_line.value()
        c2x = self.spinBox_grid_c2_column.value()
        c2y = self.spinBox_grid_c2_line.value()

        if not (0 <= c1x < self.IMAGEW and 0 <= c1y < self.IMAGEH):
            QMessageBox.warning(self, CONFIG["msg_warning"], CONFIG["msg_corner1_outside"])
            return
        if not (0 <= c2x < self.IMAGEW and 0 <= c2y < self.IMAGEH):
            QMessageBox.warning(self, CONFIG["msg_warning"], CONFIG["msg_corner2_outside"])
            return

        nlin, ncol = self._calcular_nlin_ncol()
        x0 = min(c1x, c2x)
        y0 = min(c1y, c2y)

        for i in range(NV):
            for j in range(NH):
                py = y0 + i * nlin
                px = x0 + j * ncol
                rr = RegionRect(py, px, nlin, ncol)
                self.pointl_p0.append(rr)
                self.label_nregions.setText(str(len(self.pointl_p0)))
                self._plot_regionrect(rr, self.pen_point)


        self._plot_point(QPoint(c1x, c1y), self.pen_corner)
        self._plot_point(QPoint(c2x, c2y), self.pen_corner)
        self.statusBar.showMessage(CONFIG["msg_region_selected"], 3000)


    def _on_pushButton_grid_c1_clicked(self):
        self.NCLICKS = 0
        self.GRID_C1_CLICKED = True
        self.statusBar.showMessage(CONFIG["msg_select_corner1"], 3000)

    def _on_pushButton_grid_c2_clicked(self):
        self.NCLICKS = 0
        self.GRID_C2_CLICKED = True
        self.statusBar.showMessage(CONFIG["msg_select_corner2"], 3000)

    def _on_pushButton_saveexit_clicked(self):
        if self._save_in_outfile():
            QApplication.quit()

    def _on_pushButton_point_color_clicked(self):
        color = QColorDialog.getColor(self.color_point, self)
        if color.isValid():
            self.color_point = color
            self.pen_point = QPen(self.color_point)
            self.pushButton_point_color.setIcon(_solid_icon(self.color_point))

    def _on_pushButton_corner_color_clicked(self):
        color = QColorDialog.getColor(self.color_corner, self)
        if color.isValid():
            self.color_corner = color
            self.pen_corner = QPen(self.color_corner)
            self.pen_corner.setWidth(5)
            self.pushButton_corner_color.setIcon(_solid_icon(self.color_corner))

    # ================================================================
    # Action slots
    # ================================================================


    def _on_actionRemove_regions_triggered(self):
        n = len(self.pointl_p0)
        self.statusBar.showMessage(CONFIG["msg_regions_removed"] + f" {n}", 3000)
        self._clear_regions()
        self._load_imagefile(self.lineEdit_imagefile.text())

    def _on_actionScreenshot_triggered(self):
        if self.lineEdit_outfile.text():
            start = os.path.join(os.path.dirname(self.lineEdit_outfile.text()), "screenshot.bmp")
        else:
            start = os.path.join(os.path.expanduser("~"), "screenshot.bmp")

        filename, _ = QFileDialog.getSaveFileName(  self, 
                                                    CONFIG["msg_define_image"], 
                                                    start,
                                                    "Output image file (*.png *.bmp *.jpg)")
        if not filename:
            return

        self._scene.clearSelection()
        self._scene.setSceneRect(self._scene.itemsBoundingRect())
        image = QImage(self._scene.sceneRect().size().toSize(), QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        self._scene.render(painter)
        painter.end()

        if image.save(filename, None, 100):
            self.statusBar.showMessage(CONFIG["msg_wrote_image"] + f" {filename}", 10000)
        else:
            self.statusBar.showMessage(CONFIG["msg_image_not_was_wrote"] + f" {filename}", 10000)

    def _on_actionLoad_regions_triggered(self):
        self._load_regions("")

    def _on_actionSave_regions_triggered(self):
        self._save_in_outfile()

    # ================================================================
    # UI construction (identical widget names to the .ui file)
    # ================================================================

    def _setup_actions(self):
        #
        self.actionLoad_regions = QAction(  QIcon(resource_path("icons", "edit-add.png")), 
                                            CONFIG["toolbar_load"], 
                                            self)
        self.actionLoad_regions.setToolTip(CONFIG["toolbar_load_tooltip"])
        self.actionLoad_regions.triggered.connect(self._on_actionLoad_regions_triggered)
    
    
        #
        self.actionRemove_regions = QAction(QIcon(resource_path("icons", "edit-rem.png")), 
                                            CONFIG["toolbar_remove"], 
                                            self)
        self.actionRemove_regions.setToolTip(CONFIG["toolbar_remove_tooltip"])
        self.actionRemove_regions.setStatusTip("")
        self.actionRemove_regions.triggered.connect(self._on_actionRemove_regions_triggered)

        #
        self.actionSave_regions = QAction(  QIcon(resource_path("icons", "Gnome-media-floppy.png")), 
                                            CONFIG["toolbar_save"], 
                                            self)
        self.actionSave_regions.setToolTip(CONFIG["toolbar_save_tooltip"])
        self.actionSave_regions.setShortcut("Ctrl+S")
        self.actionSave_regions.triggered.connect(self._on_actionSave_regions_triggered)




        #
        self.actionScreenshot = QAction(QIcon(resource_path("icons", "if_polaroids_1055003.svg")), 
                                        CONFIG["toolbar_screenshot"], 
                                        self)
        self.actionScreenshot.setToolTip(CONFIG["toolbar_screenshot_tooltip"])
        self.actionScreenshot.triggered.connect(self._on_actionScreenshot_triggered)

        
        #
        self.configure_action = QAction(QIcon(resource_path("icons", "text-configure.svg")),
                                        CONFIG["toolbar_configure"], 
                                        self)
        self.configure_action.setToolTip(CONFIG["toolbar_configure_tooltip"])
        self.configure_action.triggered.connect(self.open_configure_editor)

        #
        self.about_action = QAction(QIcon(resource_path("icons", "Information_icon.svg")),
                                    CONFIG["toolbar_about"], 
                                    self)
        self.about_action.setToolTip(CONFIG["toolbar_about_tooltip"])
        self.about_action.triggered.connect(self.open_about)
        

        # Coffee
        self.coffee_action = QAction(   QIcon(resource_path("icons", "emote-love.png")),
                                        CONFIG["toolbar_coffee"], 
                                        self)
        self.coffee_action.setToolTip(CONFIG["toolbar_coffee_tooltip"])
        self.coffee_action.triggered.connect(self.on_coffee_action_click)


    def _setup_menubar(self):
        self.menuBar = QMenuBar(self)
        #self.menuBar.setObjectName("menuBar")
        self.menuBar.setGeometry(0, 0, 790, 25)

        self.menuMenu = QMenu(CONFIG["menubar_menu"], self.menuBar)
        #self.menuMenu.setObjectName("menuMenu")
        self.menuMenu.addAction(self.actionSave_regions)
        self.menuMenu.addAction(self.actionLoad_regions)
        self.menuMenu.addAction(self.actionRemove_regions)
        self.menuMenu.addAction(self.actionScreenshot)


        self.menuAbout = QMenu(CONFIG["menubar_about"], self.menuBar)
        #self.menuAbout.setObjectName("menuAbout")
        self.menuAbout.addAction(self.about_action)

        self.menuBar.addMenu(self.menuMenu)
        self.menuBar.addMenu(self.menuAbout)
        self.setMenuBar(self.menuBar)

    def _setup_toolbar(self):
        self.toolbar = self.addToolBar("Main")
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        #self.toolbar.setObjectName("mainToolBar")
        
        
        self.toolbar.addAction(self.actionLoad_regions)
        self.toolbar.addAction(self.actionRemove_regions)
        self.toolbar.addAction(self.actionSave_regions)
        self.toolbar.addAction(self.actionScreenshot)
        

        # Adicionar o espaçador
        self.toolbar_spacer = QWidget()
        self.toolbar_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.toolbar.addWidget(self.toolbar_spacer)
        
        #
        self.toolbar.addAction(self.configure_action)
        self.toolbar.addAction(self.about_action)
        self.toolbar.addAction(self.coffee_action)

        # Conectar ao sinal de mudança de orientação
        self.toolbar.orientationChanged.connect(self.on_update_spacer_policy)
        self.on_update_spacer_policy()

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
            "program_name": about.__program_regions__,
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
        

    def _setup_statusbar(self):
        self.statusBar = QStatusBar(self)
        #self.statusBar.setObjectName("statusBar")
        self.setStatusBar(self.statusBar)

    def _setup_central_widget(self):
        self.centralWidget = QWidget(self)
        #self.centralWidget.setObjectName("centralWidget")
        self.setCentralWidget(self.centralWidget)

        self.verticalLayout_3 = QVBoxLayout(self.centralWidget)
        #self.verticalLayout_3.setObjectName("verticalLayout_3")

        self.verticalLayout_3.addLayout(self._build_grid_layout())
        self.verticalLayout_3.addLayout(self._build_main_hbox())
        self.verticalLayout_3.addLayout(self._build_bottom_hbox())

    def _build_grid_layout(self):
        self.gridLayout = QGridLayout()
        #self.gridLayout.setObjectName("gridLayout")



        # Row 1 — Background image
        self.label_9 = QLabel(CONFIG["background_label"])
        #self.label_9.setObjectName("label_9")
        self.lineEdit_imagefile = QLineEdit()
        #self.lineEdit_imagefile.setObjectName("lineEdit_imagefile")
        self.lineEdit_imagefile.setToolTip(CONFIG["background_lineedit_tooltip"])
        self.lineEdit_imagefile.setEnabled(False)
        self.pushButton_imagefile = QPushButton(CONFIG["background_button"])
        #self.pushButton_imagefile.setObjectName("pushButton_imagefile")
        self.pushButton_imagefile.setToolTip(CONFIG["background_button_tooltip"])
        self.pushButton_imagefile.setIcon(QIcon(resource_path("icons", "folder-saved-search.png")))
        self.pushButton_imagefile.clicked.connect(self._on_pushButton_imagefile_clicked)

        self.gridLayout.addWidget(self.label_9,            1, 0)
        self.gridLayout.addWidget(self.lineEdit_imagefile, 1, 1)
        self.gridLayout.addWidget(self.pushButton_imagefile, 1, 2)


        # Row 2 — Output file
        self.label_10 = QLabel(CONFIG["output_label"])
        #self.label_10.setObjectName("label_10")
        self.lineEdit_outfile = QLineEdit()
        #self.lineEdit_outfile.setObjectName("lineEdit_outfile")
        self.lineEdit_outfile.setToolTip(CONFIG["output_lineedit_tooltip"])
        self.pushButton_outfile = QPushButton(CONFIG["output_button"])
        #self.pushButton_outfile.setObjectName("pushButton_outfile")
        self.pushButton_outfile.setToolTip(CONFIG["output_button_tooltip"])
        self.pushButton_outfile.setIcon(QIcon(resource_path("icons", "if_compose_1055085.png")))
        self.pushButton_outfile.clicked.connect(self._on_pushButton_outfile_clicked)

        self.gridLayout.addWidget(self.label_10,           2, 0)
        self.gridLayout.addWidget(self.lineEdit_outfile,   2, 1)
        self.gridLayout.addWidget(self.pushButton_outfile, 2, 2)

        # Row 3 — Region mode
        self.label_14 = QLabel(CONFIG["region_mode_label"])
        #self.label_14.setObjectName("label_14")
        self.checkBox_corner_center = QCheckBox(CONFIG["region_mode_checkbox"])
        #self.checkBox_corner_center.setObjectName("checkBox_corner_center")
        self.checkBox_corner_center.setToolTip(CONFIG["region_mode_checkbox_tooltip"])
        self.checkBox_corner_center.setChecked(True)

        self.gridLayout.addWidget(self.label_14,               3, 0)
        self.gridLayout.addWidget(self.checkBox_corner_center, 3, 1)

        return self.gridLayout

    def _build_main_hbox(self):
        self.horizontalLayout_2 = QHBoxLayout()
        #self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        self.graphicsView = MyGraphicsView()
        #self.graphicsView.setObjectName("graphicsView")
        self.graphicsView.setMouseTracking(False)

        self.tabWidget = QTabWidget()
        #self.tabWidget.setObjectName("tabWidget")
        sp = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.tabWidget.setSizePolicy(sp)
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget.addTab(self._build_tab_one_by_one(), CONFIG["tab_one_by_one"])
        self.tabWidget.addTab(self._build_tab_grid(), CONFIG["tab_grid"])

        self.horizontalLayout_2.addWidget(self.graphicsView)
        self.horizontalLayout_2.addWidget(self.tabWidget)
        return self.horizontalLayout_2



    def _build_tab_one_by_one(self):
        self.tab = QWidget()
        #self.tab.setObjectName("tab")
        self.verticalLayout_2 = QVBoxLayout(self.tab)
        #self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.formLayout_2 = QFormLayout()
        #self.formLayout_2.setObjectName("formLayout_2")

        self.label_4 = QLabel(CONFIG["one_by_one_lines_by_regions"])
        #self.label_4.setObjectName("label_4")
        self.spinBox_one_by_one_nlin = QSpinBox()
        #self.spinBox_one_by_one_nlin.setObjectName("spinBox_one_by_one_nlin")
        self.spinBox_one_by_one_nlin.setMinimum(1)
        self.spinBox_one_by_one_nlin.setMaximum(100000)
        self.spinBox_one_by_one_nlin.setValue(32)
        self.spinBox_one_by_one_nlin.setToolTip(CONFIG["one_by_one_lines_by_regions_tooltip"])

        self.label_5 = QLabel(CONFIG["one_by_one_columns_by_regions"])
        #self.label_5.setObjectName("label_5")
        self.spinBox_one_by_one_ncol = QSpinBox()
        #self.spinBox_one_by_one_ncol.setObjectName("spinBox_one_by_one_ncol")
        self.spinBox_one_by_one_ncol.setMinimum(1)
        self.spinBox_one_by_one_ncol.setMaximum(100000)
        self.spinBox_one_by_one_ncol.setValue(48)
        self.spinBox_one_by_one_ncol.setToolTip(CONFIG["one_by_one_columns_by_regions_tooltip"])

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label_4)
        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.spinBox_one_by_one_nlin)
        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.label_5)
        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.spinBox_one_by_one_ncol)

        self.pushButton_select_one_by_one = QPushButton(CONFIG["one_by_one_select_points"])
        #self.pushButton_select_one_by_one.setObjectName("pushButton_select_one_by_one")
        self.pushButton_select_one_by_one.setToolTip(CONFIG["one_by_one_select_points_tooltip"])
        self.pushButton_select_one_by_one.clicked.connect(self._on_pushButton_select_one_by_one_clicked)

        self.verticalLayout_2.addLayout(self.formLayout_2)
        self.verticalLayout_2.addWidget(self.pushButton_select_one_by_one)
        return self.tab

    def _build_tab_grid(self):
        self.tab_2 = QWidget()
        #self.tab_2.setObjectName("tab_2")
        self.verticalLayout_4 = QVBoxLayout(self.tab_2)
        #self.verticalLayout_4.setObjectName("verticalLayout_4")

        self.formLayout = QFormLayout()
        #self.formLayout.setObjectName("formLayout")

        sp_exp = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)


        # Vertical regions
        self.label_2 = QLabel(CONFIG["grid_vertical_regions_label"])
        #self.label_2.setObjectName("label_2")
        self.spinBox_grid_nvregions = QSpinBox()
        #self.spinBox_grid_nvregions.setObjectName("spinBox_grid_nvregions")
        self.spinBox_grid_nvregions.setToolTip(CONFIG["grid_vertical_regions_tooltip"])
        self.spinBox_grid_nvregions.setMinimum(1)
        self.spinBox_grid_nvregions.setMaximum(100000)
        self.spinBox_grid_nvregions.setValue(4)

        # Horizontal regions
        self.label_11 = QLabel(CONFIG["grid_horizontal_regions_label"])
        #self.label_11.setObjectName("label_11")
        self.spinBox_grid_nhregions = QSpinBox()
        #self.spinBox_grid_nhregions.setObjectName("spinBox_grid_nhregions")
        self.spinBox_grid_nhregions.setToolTip(CONFIG["grid_horizontal_regions_tooltip"])
        self.spinBox_grid_nhregions.setMinimum(1)
        self.spinBox_grid_nhregions.setMaximum(100000)
        self.spinBox_grid_nhregions.setValue(4)



        # Select corner 1
        self.pushButton_grid_c1 = QPushButton(CONFIG["grid_select_corner1_button"])
        #self.pushButton_grid_c1.setObjectName("pushButton_grid_c1")
        self.pushButton_grid_c1.setToolTip(CONFIG["grid_select_corner1_button_tooltip"])
        self.pushButton_grid_c1.clicked.connect(self._on_pushButton_grid_c1_clicked)

        # Corner 1 Line
        self.label_3 = QLabel(CONFIG["grid_corner1_line_label"])
        #self.label_3.setObjectName("label_3")
        self.label_3.setSizePolicy(sp_exp)
        self.spinBox_grid_c1_line = QSpinBox()
        #self.spinBox_grid_c1_line.setObjectName("spinBox_grid_c1_line")
        self.spinBox_grid_c1_line.setToolTip(CONFIG["grid_corner1_line_spin_tooltip"])
        self.spinBox_grid_c1_line.setMaximum(100000)

        # Corner 1 Column
        self.label_6 = QLabel(CONFIG["grid_corner1_column_label"])
        #self.label_6.setObjectName("label_6")
        self.label_6.setSizePolicy(sp_exp)
        self.label_6.setLayoutDirection(Qt.RightToLeft)
        self.spinBox_grid_c1_column = QSpinBox()
        #self.spinBox_grid_c1_column.setObjectName("spinBox_grid_c1_column")
        self.spinBox_grid_c1_column.setToolTip(CONFIG["grid_corner1_column_spin_tooltip"])
        self.spinBox_grid_c1_column.setMaximum(100000)

        # Select corner 2
        self.pushButton_grid_c2 = QPushButton(CONFIG["grid_select_corner2_button"])
        #self.pushButton_grid_c2.setObjectName("pushButton_grid_c2")
        self.pushButton_grid_c2.setToolTip(CONFIG["grid_select_corner2_button_tooltip"])
        self.pushButton_grid_c2.clicked.connect(self._on_pushButton_grid_c2_clicked)

        # Corner 2 Line
        self.label_7 = QLabel(CONFIG["grid_corner2_line_label"])
        #self.label_7.setObjectName("label_7")
        self.spinBox_grid_c2_line = QSpinBox()
        #self.spinBox_grid_c2_line.setObjectName("spinBox_grid_c2_line")
        self.spinBox_grid_c2_line.setToolTip(CONFIG["grid_corner2_line_spin_tooltip"])
        self.spinBox_grid_c2_line.setMaximum(100000)

        # Corner 2 Column
        self.label_8 = QLabel(CONFIG["grid_corner2_column_label"])
        #self.label_8.setObjectName("label_8")
        self.spinBox_grid_c2_column = QSpinBox()
        #self.spinBox_grid_c2_column.setObjectName("spinBox_grid_c2_column")
        self.spinBox_grid_c2_column.setToolTip(CONFIG["grid_corner2_column_spin_tooltip"])
        self.spinBox_grid_c2_column.setMaximum(100000)

        # Lines / columns per region (display-only labels)
        self.label_12 = QLabel(CONFIG["grid_number_lines_label"])
        #self.label_12.setObjectName("label_12")
        self.label_grid_nlin = QLabel("0")
        #self.label_grid_nlin.setObjectName("label_grid_nlin")

        self.label_13 = QLabel(CONFIG["grid_number_columns_label"])
        #self.label_13.setObjectName("label_13")
        self.label_grid_ncol = QLabel("0")
        #self.label_grid_ncol.setObjectName("label_grid_ncol")

        # Populate form (rows match original .ui row indices)
        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_2)
        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.spinBox_grid_nvregions)
        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_11)
        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.spinBox_grid_nhregions)
        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.pushButton_grid_c1)
        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_3)
        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.spinBox_grid_c1_line)
        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_6)
        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.spinBox_grid_c1_column)
        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.pushButton_grid_c2)
        self.formLayout.setWidget(6, QFormLayout.LabelRole, self.label_7)
        self.formLayout.setWidget(6, QFormLayout.FieldRole, self.spinBox_grid_c2_line)
        self.formLayout.setWidget(7, QFormLayout.LabelRole, self.label_8)
        self.formLayout.setWidget(7, QFormLayout.FieldRole, self.spinBox_grid_c2_column)
        self.formLayout.setWidget(8, QFormLayout.LabelRole, self.label_12)
        self.formLayout.setWidget(8, QFormLayout.FieldRole, self.label_grid_nlin)
        self.formLayout.setWidget(9, QFormLayout.LabelRole, self.label_13)
        self.formLayout.setWidget(9, QFormLayout.FieldRole, self.label_grid_ncol)

        self.pushButton_select_grid = QPushButton(CONFIG["grid_select_regions"])
        #self.pushButton_select_grid.setObjectName("pushButton_select_grid")
        self.pushButton_select_grid.setToolTip(CONFIG["grid_select_regions_tooltip"])
        self.pushButton_select_grid.clicked.connect(self._on_pushButton_select_grid_clicked)

        self.verticalLayout_4.addLayout(self.formLayout)
        self.verticalLayout_4.addWidget(self.pushButton_select_grid)
        
        return self.tab_2



    def _build_bottom_hbox(self):
        self.horizontalLayout_4 = QHBoxLayout()
        #self.horizontalLayout_4.setObjectName("horizontalLayout_4")

        self.pushButton_point_color = QPushButton(CONFIG["region_color_button"])
        #self.pushButton_point_color.setObjectName("pushButton_point_color")
        self.pushButton_point_color.setToolTip(CONFIG["region_color_button_tooltip"])
        self.pushButton_point_color.clicked.connect(self._on_pushButton_point_color_clicked)

        self.pushButton_corner_color = QPushButton(CONFIG["corner_color_button"])
        #self.pushButton_corner_color.setObjectName("pushButton_corner_color")
        self.pushButton_corner_color.setToolTip(CONFIG["corner_color_button_tooltip"])
        self.pushButton_corner_color.clicked.connect(self._on_pushButton_corner_color_clicked)

        bold14 = QFont()
        bold14.setPointSize(14)
        bold14.setBold(True)

        self.label = QLabel(CONFIG["total_regions_label"])
        #self.label.setObjectName("label")
        self.label.setFont(bold14)

        self.label_nregions = QLabel("0")
        #self.label_nregions.setObjectName("label_nregions")
        self.label_nregions.setFont(bold14)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.pushButton_saveexit = QPushButton(CONFIG["save_exit_button"])
        #self.pushButton_saveexit.setObjectName("pushButton_saveexit")
        self.pushButton_saveexit.setToolTip(CONFIG["save_exit_button_tooltip"])
        self.pushButton_saveexit.setIcon(QIcon(resource_path("icons", "Gnome-media-floppy.png")))
        self.pushButton_saveexit.setIconSize(QSize(48, 48))
        self.pushButton_saveexit.clicked.connect(self._on_pushButton_saveexit_clicked)

        self.horizontalLayout_4.addWidget(self.pushButton_point_color)
        self.horizontalLayout_4.addWidget(self.pushButton_corner_color)
        self.horizontalLayout_4.addWidget(self.label)
        self.horizontalLayout_4.addWidget(self.label_nregions)
        self.horizontalLayout_4.addItem(self.horizontalSpacer)
        self.horizontalLayout_4.addWidget(self.pushButton_saveexit)
        return self.horizontalLayout_4


# ============================================================================
# Entry point — mirrors main.cpp argument parsing
# ============================================================================

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
       

    icon_path=resource_path("icons", "listregions.svg")

    extras=""
    
    create_desktop_directory()    
    create_desktop_menu()
    create_desktop_file(os.path.join("~",".local","share","applications"), 
                        program_name=about.__program_regions__,
                        extras=extras,
                        icon_path=icon_path)
    
    for n in range(len(sys.argv)):
        if sys.argv[n] == "--autostart":
            create_desktop_directory(overwrite = True)
            create_desktop_menu(overwrite = True)
            create_desktop_file(os.path.join("~",".config","autostart"), 
                                overwrite=True, 
                                program_name=about.__program_regions__,
                                extras=extras,
                                icon_path=icon_path)
            return
        if sys.argv[n] == "--applications":
            create_desktop_directory(overwrite = True)
            create_desktop_menu(overwrite = True)
            create_desktop_file(os.path.join("~",".local","share","applications"), 
                                overwrite=True, 
                                program_name=about.__program_regions__,
                                extras=extras,
                                icon_path=icon_path)
            return
    

    parser = argparse.ArgumentParser(prog=about.__program_regions__)
    parser.add_argument("--rootimage",     default="")
    parser.add_argument("--outfile",       default="")
    parser.add_argument("--dis-rootimage", action="store_true")
    parser.add_argument("--en-rootimage",  action="store_true")
    parser.add_argument("--dis-outfile",   action="store_true")
    parser.add_argument("--en-outfile",    action="store_true")
    args = parser.parse_args()

    # dis_rootimage: True means "disable the button" (locked)
    dis_rootimage = bool(args.rootimage)          # default: lock if provided
    if args.dis_rootimage: dis_rootimage = True
    if args.en_rootimage:  dis_rootimage = False

    outfile = args.outfile or os.path.join(os.path.expanduser("~"), "default.listregions")
    dis_outfile = bool(args.outfile)
    if args.dis_outfile: dis_outfile = True
    if args.en_outfile:  dis_outfile = False

    progpath = os.path.abspath(sys.argv[0])
    progdir  = os.path.dirname(progpath)

    app = QApplication(sys.argv)
    window = MainWindow()

    window.set_parameter_progpath(progpath)
    window.set_parameter_progdir(progdir)
    window.set_parameter_rootimage(args.rootimage, dis_rootimage)
    window.set_parameter_outfile(outfile, dis_outfile)

    if args.rootimage:
        window._load_regions(outfile)

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
