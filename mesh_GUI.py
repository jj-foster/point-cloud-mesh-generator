import sys
import os
from PyQt5.QtWidgets import *
import json

from mesh_processor import Mesh

class Window(QMainWindow):  #   Class inherets from QMainWindow
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Mesher')
        self.generalLayout=QVBoxLayout()

        self.centralWidget=QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.generalLayout)     
        
        self.createActions()
        self.connectActions()
        self.createMenu()
        self.createStatus()

        self.Sections()
        
        self.createImport()
        self.generatePoints()
        self.processMesh()
        self.createExport()

        self.mesh=Mesh()

    def createActions(self):
        """Defines menu actions"""
        self.openAction=QAction("Open")
        self.saveAction=QAction("Save")
        self.exitAction=QAction("Exit")

    def connectActions(self):
        """Connects menu buttons to actions"""
        self.openAction.triggered.connect(self.openInstance)
        self.saveAction.triggered.connect(self.saveInstance)
        self.exitAction.triggered.connect(self.close)

    def createMenu(self):
        """Draws menu buttons"""
        menuBar=self.menuBar()
        fileMenu=QMenu('File',self)
        menuBar.addMenu(fileMenu)

        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)

    def createStatus(self):
        """Draws status bar (bottom bar)"""
        self.statusbar=self.statusBar()
        self.statusbar.showMessage('Ready',6000)

    def Sections(self):
        """Draws main window sections"""
        importGroup=QGroupBox('Import CAD') #   Initiates group
        self.importLayout=QGridLayout() #   Initiates layout
        importGroup.setLayout(self.importLayout)    #   Assigns layout to group

        pcdGroup=QGroupBox('Generate Mesh')
        self.pcdLayout=QGridLayout()
        pcdGroup.setLayout(self.pcdLayout)

        self.meshGroup=QGroupBox('Post-Process')
        self.meshGroup.setCheckable(True)   #   Enables check box
        self.meshLayout=QVBoxLayout()
        self.meshGroup.setLayout(self.meshLayout)

        exportGroup=QGroupBox('Export Mesh')
        self.exportLayout=QGridLayout()
        exportGroup.setLayout(self.exportLayout)

        #   Groups added to general layout (vertical box stack)
        self.generalLayout.addWidget(importGroup)
        self.generalLayout.addWidget(pcdGroup)
        self.pcdLayout.addWidget(self.meshGroup,2,0,1,3) #   mesh group within pcd group
        self.generalLayout.addWidget(exportGroup)       

    def createImport(self):
        """Draws import widgets & defines import button"""
        btnSelectIn=QPushButton('Open') #   Initiates button widget
        btnSelectIn.setMaximumSize(50,50)   #   Limits button size (more room for text box)
        self.inputMesh=QLineEdit("File path")
        self.btnImport=QPushButton('Import')

        self.importLayout.addWidget(btnSelectIn,0,0)    #   Adds widget to layout
        self.importLayout.addWidget(self.inputMesh,0,1)
        self.importLayout.addWidget(self.btnImport,1,0,1,3)

        #.connect() must be callible (run-able) hence lambda. Opens file explorer window & writes
        btnSelectIn.clicked.connect(lambda: self.inputMesh.setText(self.fileOpenDialog()[0]))

        def importReq(self):
            self.statusbar.showMessage('Importing mesh...')    #   Sets a status bar message
            self.mesh._import(self.inputMesh.text())    #   Reads input mesh with open3d (mesh_processor.py)
            self.statusbar.showMessage('Mesh imported',6000)

        self.btnImport.clicked.connect(lambda: importReq(self))   # On click, import button calls importReq function

    def fileOpenDialog(self):
        """Opens file dialog window. Returns selected file."""
        file_filter='Obj (*.obj);; STL (ASCII) (*.stl);; All Files (*.*)'   #   Mesh fitlers
        file_dir=QFileDialog.getOpenFileName(
            parent=self,
            caption='Select a mesh file',
            directory=os.getcwd(),  #   Initial directory
            filter=file_filter,
            initialFilter='Mesh File (*.obj *.stl)' #   Initial filter
        )
        return file_dir

    def fileSaveDialog(self):
        """Opens file dialog window. Returns save file."""
        file_filter='Obj (*.obj);; STL (ASCII) (*.stl);; All Files (*.*)'
        file_dir=QFileDialog.getSaveFileName(
            parent=self,
            caption='Select a mesh file',
            directory=os.getcwd(),
            filter=file_filter,
            initialFilter='Mesh File (*.obj *.stl)'
        )
        return file_dir

    def generatePoints(self):
        """Draws point cloud GUI. Draws button to generate point cloud & display"""
        self.pcdLayout.addWidget(QLabel('No. Points:'),0,0)
        self.pcdPoints=QLineEdit()
        self.pcdLayout.addWidget(self.pcdPoints,0,1)

        btnShowPoints=QPushButton('Show Points')
        self.pcdLayout.addWidget(btnShowPoints,0,2)    #   Adds generate button to pcd layout next to form
        
        def pointsReq(self):
            self.statusbar.showMessage('Generating point cloud...',6000)
            self.mesh.pointsGen(self,self.pcdPoints.text()) #   Generates points cloud from input mesh with given no. points
            self.statusbar.showMessage('Point cloud generated',6000)
            self.mesh.pointsView()  #   Displays point cloud

        btnShowPoints.clicked.connect(lambda: pointsReq(self))

    def processMesh(self):
        """Draws mesh processing GUI. Draws update mesh button & assigns backend functionality"""
        meshForm=QGridLayout()
        meshForm.addWidget(QLabel('Vertex merge distance [mm]:'),0,0)
        meshForm.addWidget(QLabel('Smoothing iterations:'),1,0)

        self.merge=QLineEdit()
        self.smooth=QLineEdit()
        meshForm.addWidget(self.merge,0,1)
        meshForm.addWidget(self.smooth,1,1)

        self.meshLayout.addLayout(meshForm) #   Adds merge & smooth options to mesh processing group layout (by adding layouts rather than individual widgets)

        btnGenMesh=QPushButton('Update Mesh')
        self.pcdLayout.addWidget(btnGenMesh,3,0,1,3)
        
        def processReq(self):
            #   If 'show point cloud' button hasn't been pressed or no. points has been updated, re-generate pointcloud
            if self.mesh.pcd==None or self.pcdPoints.text()!=self.mesh.points:
                self.statusbar.showMessage('Generating point cloud...')
                self.mesh.pointsGen(self,self.pcdPoints.text()) #   Generates point cloud
                self.statusbar.showMessage('Point cloud generated',6000)

            self.statusbar.showMessage('Generating mesh...')
            self.mesh.generate()    #   Generates mesh based on point cloud

            #   If the post-processing group box is enabled, otherwise skip
            if self.meshGroup.isChecked()==True:
                self.statusbar.showMessage('Smoothing mesh...')
                self.mesh.smooth(self,self.smooth.text())   #   Smoothes mesh vertices with given no. iterations
                self.statusbar.showMessage('Merging vertices...')
                self.mesh.merge(self,self.merge.text()) #   Merges close vertices between given distance
                self.mesh.smooth(self,self.smooth.text())   #   Smoothes again

            self.statusbar.showMessage('Mesh processing complete',6000)
            self.mesh.display() #   Displays mesh

        btnGenMesh.clicked.connect(lambda: processReq(self))    #   Calls above functionality from button press

    def createExport(self):
        """Draws export GUI, adds export buttons"""
        btnSelectOut=QPushButton('Open')
        btnSelectOut.setMaximumSize(50,50)
        self.exportMesh=QLineEdit("File path")
        btnExport=QPushButton('Export')

        self.exportLayout.addWidget(btnSelectOut,0,0)
        self.exportLayout.addWidget(self.exportMesh,0,1)
        self.exportLayout.addWidget(btnExport,1,0,1,3)

        #   Writes to file path textbox result of file explorer
        btnSelectOut.clicked.connect(lambda: self.exportMesh.setText(self.fileSaveDialog()[0]))

        def exportReq(self):
            self.statusbar.showMessage('Exporting mesh...',6000)
            self.mesh.write(self.exportMesh.text()) #   Exports mesh
            self.statusbar.showMessage('Mesh exported',6000)

        btnExport.clicked.connect(lambda: exportReq(self))

    def saveInstance(self):
        data={"input mesh":self.inputMesh.text(),
            "number of points":self.pcdPoints.text(),
            "post-process checked":self.meshGroup.isChecked(),
            "merge distance":self.merge.text(),
            "smooth iterations":self.smooth.text(),
            "output mesh":self.exportMesh.text()
            }

        file=QFileDialog.getSaveFileName(
            caption='Save instance data',
            directory=os.getcwd(),
            filter="JSON (*.json)"
        )[0]

        if file:
            with open(file,"w") as f:
                json.dump(data,f,indent=4)

    def openInstance(self):
        file=QFileDialog.getOpenFileName(
            caption='Open instance data',
            directory=os.getcwd(),
            filter="JSON (*.json)"
        )[0]

        if file:
            with open(file,'r') as f:
                data=json.load(f)

            self.inputMesh.setText(data["input mesh"])
            self.pcdPoints.setText(data["number of points"])
            self.meshGroup.setChecked(data["post-process checked"])
            self.merge.setText(data["merge distance"])
            self.smooth.setText(data["smooth iterations"])
            self.exportMesh.setText(data["output mesh"])

if  __name__=='__main__':
    app=QApplication(sys.argv)
    win=Window()
    win.show()
    sys.exit(app.exec())    #   Main loop