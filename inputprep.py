# -*- coding: utf-8 -*-
"""
/***************************************************************************
 inputprep
                                 A QGIS plugin
 This plugin prepares vector and raster datasets for us in the beaver dam tools location generator and water storage estimators
                              -------------------
        begin                : 2017-07-04
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Konrad Hafen
        email                : k.hafen@aggiemail.usu.edu
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import*
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from inputprep_dialog import inputprepDialog
import os


class inputprep:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'inputprep_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = inputprepDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Input Prep')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'inputprep')
        self.toolbar.setObjectName(u'inputprep')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('inputprep', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        # Check if the menu exists and get it
        self.menu = self.iface.mainWindow().findChild(QMenu, '&Beaver Dam Tools')

        # If the menu does not exist, create it!
        if not self.menu:
            self.menu = QMenu('&Beaver Dam Tools', self.iface.mainWindow().menuBar())
            self.menu.setObjectName('&Beaver Dam Tools')
            actions = self.iface.mainWindow().menuBar().actions()
            lastAction = actions[-1]
            self.iface.mainWindow().menuBar().insertMenu(lastAction, self.menu)

        self.action = QAction(QIcon(":/plugins/inputprep/icon.png"), "Input prep",
                              self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.menu.addAction(self.action)
        self.dlg = inputprepDialog()

        self.dlg.cb_soilRaster.stateChanged.connect(self.enableSoilRasters)
        self.dlg.tb_loadShp.clicked.connect(self.loadShpClip)
        self.dlg.tb_outDir.clicked.connect(self.loadDir)
        self.dlg.tb_inBrat.clicked.connect(self.loadShp)
        self.dlg.tb_inDem.clicked.connect(lambda: self.setRasterLineEditText(self.dlg.le_inDem))
        self.dlg.tb_inFac.clicked.connect(lambda: self.setRasterLineEditText(self.dlg.le_inFac))
        self.dlg.tb_inFdir.clicked.connect(lambda: self.setRasterLineEditText(self.dlg.le_inFdir))
        self.dlg.tb_hka.clicked.connect(lambda: self.setRasterLineEditText(self.dlg.le_hka))
        self.dlg.tb_vka.clicked.connect(lambda: self.setRasterLineEditText(self.dlg.le_vka))
        self.dlg.tb_fc.clicked.connect(lambda: self.setRasterLineEditText(self.dlg.le_rc))
        self.dlg.cb_layers.activated.connect(self.showFields)
        self.importLayers()

            #activate layout


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Input Prep'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def enableSoilRasters(self):
        if self.dlg.cb_soilRaster.isChecked():
            self.dlg.label_8.setEnabled(True)
            self.dlg.label_9.setEnabled(True)
            self.dlg.label_10.setEnabled(True)
            self.dlg.le_hka.setEnabled(True)
            self.dlg.le_vka.setEnabled(True)
            self.dlg.le_fc.setEnabled(True)
            self.dlg.tb_hka.setEnabled(True)
            self.dlg.tb_vka.setEnabled(True)
            self.dlg.tb_fc.setEnabled(True)
        else:
            self.dlg.label_8.setEnabled(False)
            self.dlg.label_9.setEnabled(False)
            self.dlg.label_10.setEnabled(False)
            self.dlg.le_hka.setEnabled(False)
            self.dlg.le_vka.setEnabled(False)
            self.dlg.le_fc.setEnabled(False)
            self.dlg.tb_hka.setEnabled(False)
            self.dlg.tb_vka.setEnabled(False)
            self.dlg.tb_fc.setEnabled(False)

    def importLayers(self, layerName = None):
        self.dlg.cb_layers.clear()
        layers = self.iface.legendInterface().layers()
        layer_list = []
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer:
                layer_list.append(layer.name())

        self.dlg.cb_layers.addItems(layer_list)
        if layerName is None:
            if len(layer_list)>0:
                self.dlg.cb_layers.setCurrentIndex(0)
        else:
            self.dlg.cb_layers.setCurrentIndex(layer_list.index(layerName))

        self.showFields()

    def loadDir(self):
        self.dlg.le_outDir.setText(str(QFileDialog.getExistingDirectory(caption = "Select output directory")))

    def loadRaster(self):
        inRas = str(QFileDialog.getOpenFileNameAndFilter(filter="GeoTiff File (*.tif *.tiff *.TIF *.TIFF)")[0])
        if inRas:
            self.iface.addRasterLayer(inRas, os.path.basename(inRas))
            return inRas

    def loadShp(self):
        inShp = str(QFileDialog.getOpenFileNameAndFilter(filter = "Shapefiles (*.shp)")[0])
        if inShp is not None:
            newLayer = self.iface.addVectorLayer(inShp, str.split(os.path.basename(inShp),".")[0], "ogr")
            if not newLayer:
                print "layer failed to load"

    def loadShpClip(self):
        self.inShp = str(QFileDialog.getOpenFileNameAndFilter(filter = "Shapefiles (*.shp)")[0])
        newLayer = self.iface.addVectorLayer(self.inShp, str.split(os.path.basename(self.inShp),".")[0], "ogr")
        if not newLayer:
            print "layer failed to load"
        else:
            self.importLayers(newLayer.name())

    def setRasterLineEditText(self, lineEdit):
        lineEdit.setText(self.loadRaster())

    def showFields(self):
        self.dlg.cb_fields.clear()
        layerName = self.dlg.cb_layers.currentText()
        layers = self.iface.legendInterface().layers()
        for layer in layers:
            if layer.name() == layerName:
                fields = [field.name() for field in layer.pendingFields()]
                self.dlg.cb_fields.addItems(fields)
                break

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
