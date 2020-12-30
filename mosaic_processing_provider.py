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
from qgis.core import QgsProcessingProvider
from .mosaic_processing_algorithm import s2mosaicProcessingAlgorithm
import os.path

class mosaicProcessingProvider(QgsProcessingProvider):

    def __init__(self):
        QgsProcessingProvider.__init__(self)

    def unload(self):
        pass

    def loadAlgorithms(self):
        self.addAlgorithm(s2mosaicProcessingAlgorithm())

    def id(self):
        return 's2_mosaic'

    def name(self):
        return 's2_mosaic'

    def icon(self):
        return QIcon(os.path.dirname(__file__) + '/mosaic-2.png')

    def longName(self):
        return self.name()
