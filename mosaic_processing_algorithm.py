# -*- coding: utf-8 -*-

"""
/***************************************************************************
 AtlasGridProcessingAlgorithm
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

from qgis.PyQt.QtGui import QIcon
from qgis.core import (QgsFeatureSink,
                       QgsFeature,
                       QgsGeometry,
                       QgsPointXY,
                       QgsWkbTypes,
                       QgsProcessing,
                       QgsProcessingException,
                       QgsProcessingParameterExtent,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterDateTime,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSink,
                       #QgsProcessingParameterNumber,
                       QgsProcessingParameterScale,
                       QgsVectorLayer)
from processing.core.Processing import Processing
import os.path, math, time
import ee
from ee_plugin import Map


class s2mosaicProcessingAlgorithm(QgsProcessingAlgorithm):

    DATE1 = 'DATE1'
    DATE2 = 'DATE2'
    EXTENT = 'EXTENT'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):

        self.addParameter(QgsProcessingParameterDateTime(self.DATE1, 'Left date'))
        self.addParameter(QgsProcessingParameterDateTime(self.DATE2, 'Right date'))
        self.addParameter(QgsProcessingParameterExtent(self.EXTENT, 'Mosaic extent'))
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT, 'Result mosaic', type=QgsProcessing.TypeVectorPolygon))
       
    def processAlgorithm(self, parameters, context, feedback):

        crs = context.project().crs()
        #fmt = self.parameterAsEnum(parameters, self.FORMAT, context)
        #scale = self.parameterAsInt(parameters, self.SCALE, context)
        #scale = int(self.parameterAsDouble(parameters, self.SCALE, context)/100)
        bbox = self.parameterAsExtent(parameters, self.EXTENT, context, crs)

        date_start='2020-08-01'
        date_end='2020-08-31'

        #Выбираем область (можно рисовать в code.earthengine.google.com)и вставлять сюда
        aoi=ee.FeatureCollection(ee.Geometry.Polygon(
                [[[29, 57],
                  [29, 55],
                  [38, 55],
                  [38, 57]]]))

        cloudiness = 50
        #Параметры визуализации
        r_band = 'B12'
        g_band = 'B8'
        b_band = 'B4'
        bands = [r_band,g_band,b_band]
        vis_min = 30
        vis_max = 7000.
        vis_gamma = 1.7
        visParams = {'bands': bands,'min': vis_min,'max': vis_max,'gamma': vis_gamma}
        layer_name_1 = 'S2SRC-%s-%s'%(date_start,date_end)
        layer_name_2 = 'Sent-2-%s-%s-stretch'%(date_start,date_end)
        #Выбираем коллекцию снимков  и фильтруем по общей облачности
        collection = ee.ImageCollection('COPERNICUS/S2').filterMetadata('CLOUDY_PIXEL_PERCENTAGE','less_than', cloudiness).filterBounds(aoi).map(self.filterCloudSentinel2)
        #Напечаем размер коллекции в консоли
        col_size = collection.size().getInfo()
        #Создадим медианный композит и обрежем по аои
        im1 = collection.filterDate(date_start,date_end).median().clipToCollection(aoi)
        #добавим на карту
        Map.addLayer(im1,visParams,layer_name_1,False)
        #Парметры каналы, исходное изображение, АОИ, шкала (чем больше тем быстрее),перцентили)
        s2str=self.stretcher(bands,im1.updateMask(im1.gt(0)),aoi,1500,3,97)
        #извлекаем rgb и определяем его как image
        im2 = ee.Image(s2str.get('imRGB')).clipToCollection(aoi)
        #добавим на карту
        Map.addLayer(im2,{},layer_name_2,False)

        return {self.OUTPUT: col_size}
     
    def stretcher(self, bands,im,AOI,scale,range1,range2):
        stats = im.select(bands).clipToCollection(AOI).reduceRegion(
        reducer=ee.Reducer.percentile([range1,range2]),
        geometry=AOI,
        scale=scale,
        maxPixels= 1e15)
        imRGB = im.select(bands).visualize(
           min=ee.List([stats.get(bands[0]+'_p'+str(range1)), stats.get(bands[1]+'_p'+str(range1)), stats.get(bands[2]+'_p'+str(range1))]), 
           max=ee.List([stats.get(bands[0]+'_p'+str(range2)), stats.get(bands[1]+'_p'+str(range2)), stats.get(bands[2]+'_p'+str(range2))]), 
        )
        return im.set('imRGB', imRGB)#Добавляем rgb к исходным каналам в виде метаданных

    def filterCloudSentinel2 (self, img): 
        quality = img.select('QA60').int()
        cloudBit = ee.Number(1024)
        cirrusBit = ee.Number(2048)
        cloudFree = quality.bitwiseAnd(cloudBit).eq(0)
        cirrusFree = quality.bitwiseAnd(cirrusBit).eq(0)
        clear = cloudFree.bitwiseAnd(cirrusFree)
        return img.updateMask(clear)

    def name(self):
        return 'Sentinel2 Mosaic'

    def icon(self):
        return QIcon(os.path.dirname(__file__) + '/mosaic-2.png')

    def displayName(self):
        return self.name()

    def group(self):
        return self.groupId()

    def groupId(self):
        return ''

    def createInstance(self):
        return s2mosaicProcessingAlgorithm()
