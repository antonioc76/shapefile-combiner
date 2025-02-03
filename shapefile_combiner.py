import PyQt6 as qt
import PyQt6.QtWidgets as wdg
from PyQt6.uic import loadUi
import os
import sys
import geopandas as gpd
import pandas as pd
import webbrowser
import pyogrio

import matplotlib
matplotlib.use('qtagg')
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)


class MainWindow(wdg.QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()

        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle, the PyInstaller bootloader
            # extends the sys module by a flag frozen=True and sets the app 
            # path into variable _MEIPASS'.
            self.this_exec_dir = os.path.dirname(sys._MEIPASS)
        else:
            self.this_exec_dir = os.path.dirname(os.path.abspath(__file__))

        # self.this_exec_dir = os.path.dirname(os.path.abspath(__file__))
        loadUi(self.this_exec_dir + "\\mockup1.ui", self)

        # type annotations for intellisense
        # buttons
        self.addFiles: wdg.QPushButton
        self.removeFiles: wdg.QPushButton
        self.combineFiles: wdg.QPushButton
        self.browseDestinationFolder: wdg.QPushButton
        self.crsHelp: wdg.QPushButton
        self.previewButton: wdg.QPushButton


        # labels
        self.destinationLabel: wdg.QLabel
        self.doneLabel: wdg.QLabel
        self.crsLabel: wdg.QLabel

        # line edits
        self.destinationLineEdit: wdg.QLineEdit
        self.crsFormatLine: wdg.QLineEdit
        
        # progress bars
        self.progressBar: wdg.QProgressBar

        # list widgets
        self.shapefileList: wdg.QListWidget


        # implement element functionalities
        self.addFiles.clicked.connect(self.addFilesCallback)
        self.removeFiles.clicked.connect(self.removeFilesCallback)
        self.browseDestinationFolder.clicked.connect(self.browseDestinationFolderCallback)
        self.crsHelp.clicked.connect(self.crsHelpCallback)
        self.combineFiles.clicked.connect(self.combineFilesCallback)
        self.previewButton.clicked.connect(self.previewCallback)


    def addFilesCallback(self):
        filenames = wdg.QFileDialog.getOpenFileNames(self, 'Open Shapefile(s)', 'C:/', '*.shp')[0]
        if filenames is None:
            return

        self.shapefileList.addItems(filenames)


    def removeFilesCallback(self):
        selected = self.shapefileList.selectedItems()
        if not selected:
            return
        for item in selected:
            self.shapefileList.takeItem(self.shapefileList.row(item))


    def browseDestinationFolderCallback(self):
        foldername = wdg.QFileDialog.getExistingDirectory(self, 'Select Destination Folder', 'C:/')
        self.destinationLineEdit.setText(foldername)


    def crsHelpCallback(self):
        webbrowser.open("https://sis.apache.org/tables/CoordinateReferenceSystems.html")


    def combineFilesCallback(self):
        combined_shapefile = self.previewCallback(True)

        # filenames = [self.shapefileList.item(x).text() for x in range(self.shapefileList.count())]
        filenames = [item.text() for item in self.shapefileList.selectedItems()]
        shapefiles = [gpd.read_file(filename) for filename in filenames]

        if shapefiles == []:
            return

        if not os.path.exists(f'{self.destinationLineEdit.text()}/Result'):
            os.makedirs(f'{self.destinationLineEdit.text()}/Result')

        combined_shapefile.to_file(f"{self.destinationLineEdit.text()}/Result/output.shp", mode='w')

        self.progressBar.setValue(100)

        self.doneLabel.setText(f"Success! Results created at {self.destinationLineEdit.text()}/Result")


    def previewCallback(self, output=False):
        # filenames = [self.shapefileList.item(x).text() for x in range(self.shapefileList.count())]
        filenames = [item.text() for item in self.shapefileList.selectedItems()]
        shapefiles = [gpd.read_file(filename) for filename in filenames]

        if shapefiles == []:
            return
        
        if output: self.progressBar.setValue(20)

        crs = self.crsFormatLine.text()
        print(crs)

        if output: self.progressBar.setValue(40)

        if crs == '':
            return
        
        for shapefile in shapefiles:
            if shapefile.crs is None:
                shapefile.set_crs(crs)

            else:
                shapefile.to_crs(crs, inplace=True)

        if output: self.progressBar.setValue(60)

        combined_shapefile = pd.concat(shapefiles)

        if output: self.progressBar.setValue(80)

        sc = MplCanvas()
        combined_shapefile.plot(ax=sc.axes, color='None', edgecolor='Black')

        # breakout plot
        self.popup = wdg.QWidget()
        self.popup.setMinimumWidth(500)
        self.popup.setMinimumHeight(500)
        self.popup.setWindowTitle("Shapefile preview")
        self.layout = wdg.QVBoxLayout(self.popup)
        self.layout.addWidget(sc)
        self.popup.show()

        return combined_shapefile


if __name__ == "__main__":
    app = wdg.QApplication(sys.argv)
    app.setStyle('windowsvista')
    mainWindow = MainWindow()
    mainWindow.show()

    sys.exit(app.exec())