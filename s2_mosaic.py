# -*- coding: utf-8 -*-
"""
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsApplication
import processing, os.path

# Initialize Qt resources from file resources.py
from .resources import *

# Import the code for the dialog
from .mosaic_processing_provider import mosaicProcessingProvider

class s2mosaic:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.provider = None
        self.first_start = None
        self.toolbar = self.iface.addToolBar('Mosaic Toolbar')
        self.toolbar.setObjectName('MosaicToolbar')

    def initGui(self):
    
        iconS2mosaic = QIcon(os.path.dirname(__file__) + '/mosaic-2.png')
        self.s2mosaicAction = QAction(iconS2mosaic, "s2_mosaic", self.iface.mainWindow())
        self.s2mosaicAction.setObjectName("s2mocaic")
        self.s2mosaicAction.triggered.connect(self.s2mosaic)
        self.s2mosaicAction.setEnabled(True)
        #self.iface.addToolBarIcon(self.s2mosaicAction)
        self.toolbar.addAction(self.s2mosaicAction)
        self.iface.addPluginToVectorMenu('&Mosaic', self.s2mosaicAction)
 
        self.initProcessing()
        self.first_start = True

    def initProcessing(self):
        self.provider = mosaicProcessingProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        self.iface.removePluginVectorMenu('&Mosaic', self.s2mosaicAction)
        self.iface.removeToolBarIcon(self.s2mosaicAction)
        QgsApplication.processingRegistry().removeProvider(self.provider)
        del self.toolbar

    def s2mosaic(self):
        processing.execAlgorithmDialog('s2_mosaic:Sentinel2 Mosaic', {})
