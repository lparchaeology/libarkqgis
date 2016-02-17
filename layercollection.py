# -*- coding: utf-8 -*-
"""
/***************************************************************************
                                ARK QGIS
                        A QGIS utilities library.
        Part of the Archaeological Recording Kit by L-P : Archaeology
                        http://ark.lparchaeology.com
                              -------------------
        begin                : 2014-12-07
        git sha              : $Format:%H$
        copyright            : 2014, 2015 by L-P : Heritage LLP
        email                : ark@lparchaeology.com
        copyright            : 2014, 2015 by John Layt
        email                : john@layt.net
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

from sets import Set

from PyQt4.QtCore import QVariant, QDir, QFile

from qgis.core import QGis, QgsMapLayerRegistry, QgsVectorLayer, QgsProject, QgsSnapper, QgsTolerance, QgsMapLayer, QgsFeatureRequest, QgsRectangle, QgsLayerTreeGroup, NULL, QgsField
from qgis.gui import QgsMessageBar, QgsHighlight

import utils, layers, snapping
from project import Project

class LayerCollectionSettings:

    collection = ''
    collectionPath = ''

    parentGroupName = ''
    collectionGroupName = ''
    bufferGroupName = ''
    log = False

    pointsLayerLabel = ''
    pointsLayerName = ''
    pointsLayerPath = ''
    pointsStylePath = ''
    pointsBufferName = ''
    pointsBufferPath = ''
    pointsLogName = ''
    pointsLogPath = ''

    linesLayerLabel = ''
    linesLayerName = ''
    linesLayerPath = ''
    linesStylePath = ''
    linesBufferName = ''
    linesBufferPath = ''
    linesLogName = ''
    linesLogPath = ''

    polygonsLayerLabel = ''
    polygonsLayerName = ''
    polygonsLayerPath = ''
    polygonsStylePath = ''
    polygonsBufferName = ''
    polygonsBufferPath = ''
    polygonsLogName = ''
    polygonsLogPath = ''

    @staticmethod
    def fromProject(projectScope, collection):
        scope = projectScope + '/collections/' + collection
        lcs = LayerCollectionSettings()
        lcs.collection = Project.readEntry(scope, 'collection')
        lcs.collectionPath = Project.readEntry(scope, 'collectionPath')
        lcs.collectionGroupName = Project.readEntry(scope, 'collectionGroupName')
        lcs.parentGroupName = Project.readEntry(scope, 'parentGroupName')
        lcs.bufferGroupName = Project.readEntry(scope, 'bufferGroupName')
        lcs.log = Project.readBoolEntry(scope, 'log')
        lcs.pointsLayerLabel = Project.readEntry(scope, 'pointsLayerLabel')
        lcs.pointsLayerName = Project.readEntry(scope, 'pointsLayerName')
        lcs.pointsLayerPath = Project.readEntry(scope, 'pointsLayerPath')
        lcs.pointsStylePath = Project.readEntry(scope, 'pointsStylePath')
        lcs.pointsBufferName = Project.readEntry(scope, 'pointsBufferName')
        lcs.pointsBufferPath = Project.readEntry(scope, 'pointsBufferPath')
        lcs.pointsLogName = Project.readEntry(scope, 'pointsLogName')
        lcs.pointsLogPath = Project.readEntry(scope, 'pointsLogPath')
        lcs.linesLayerLabel = Project.readEntry(scope, 'linesLayerLabel')
        lcs.linesLayerName = Project.readEntry(scope, 'linesLayerName')
        lcs.linesLayerPath = Project.readEntry(scope, 'linesLayerPath')
        lcs.linesStylePath = Project.readEntry(scope, 'linesStylePath')
        lcs.linesBufferName = Project.readEntry(scope, 'linesBufferName')
        lcs.linesBufferPath = Project.readEntry(scope, 'linesBufferPath')
        lcs.linesLogName = Project.readEntry(scope, 'linesLogName')
        lcs.linesLogPath = Project.readEntry(scope, 'linesLogPath')
        lcs.polygonsLayerLabel = Project.readEntry(scope, 'polygonsLayerLabel')
        lcs.polygonsLayerName = Project.readEntry(scope, 'polygonsLayerName')
        lcs.polygonsLayerPath = Project.readEntry(scope, 'polygonsLayerPath')
        lcs.polygonsStylePath = Project.readEntry(scope, 'polygonsStylePath')
        lcs.polygonsBufferName = Project.readEntry(scope, 'polygonsBufferName')
        lcs.polygonsBufferPath = Project.readEntry(scope, 'polygonsBufferPath')
        lcs.polygonsLogName = Project.readEntry(scope, 'polygonsLogName')
        lcs.polygonsLogPath = Project.readEntry(scope, 'polygonsLogPath')
        return lcs

    def toProject(self, projectScope):
        scope = projectScope + '/collections/' + self.collection
        Project.writeEntry(scope, 'collection', self.collection)
        Project.writeEntry(scope, 'collectionPath', self.collectionPath)
        Project.writeEntry(scope, 'collectionGroupName', self.collectionGroupName)
        Project.writeEntry(scope, 'parentGroupName', self.parentGroupName)
        Project.writeEntry(scope, 'bufferGroupName', self.bufferGroupName)
        Project.writeEntry(scope, 'log', self.log)
        Project.writeEntry(scope, 'pointsLayerLabel', self.pointsLayerLabel)
        Project.writeEntry(scope, 'pointsLayerName', self.pointsLayerName)
        Project.writeEntry(scope, 'pointsLayerPath', self.pointsLayerPath)
        Project.writeEntry(scope, 'pointsStylePath', self.pointsStylePath)
        Project.writeEntry(scope, 'pointsBufferName', self.pointsBufferName)
        Project.writeEntry(scope, 'pointsBufferPath', self.pointsBufferPath)
        Project.writeEntry(scope, 'pointsLogName', self.pointsLogName)
        Project.writeEntry(scope, 'pointsLogPath', self.pointsLogPath)
        Project.writeEntry(scope, 'linesLayerLabel', self.linesLayerLabel)
        Project.writeEntry(scope, 'linesLayerName', self.linesLayerName)
        Project.writeEntry(scope, 'linesLayerPath', self.linesLayerPath)
        Project.writeEntry(scope, 'linesStylePath', self.linesStylePath)
        Project.writeEntry(scope, 'linesBufferName', self.linesBufferName)
        Project.writeEntry(scope, 'linesBufferPath', self.linesBufferPath)
        Project.writeEntry(scope, 'linesLogName', self.linesLogName)
        Project.writeEntry(scope, 'linesLogPath', self.linesLogPath)
        Project.writeEntry(scope, 'polygonsLayerLabel', self.polygonsLayerLabel)
        Project.writeEntry(scope, 'polygonsLayerName', self.polygonsLayerName)
        Project.writeEntry(scope, 'polygonsLayerPath', self.polygonsLayerPath)
        Project.writeEntry(scope, 'polygonsStylePath', self.polygonsStylePath)
        Project.writeEntry(scope, 'polygonsBufferName', self.polygonsBufferName)
        Project.writeEntry(scope, 'polygonsBufferPath', self.polygonsBufferPath)
        Project.writeEntry(scope, 'polygonsLogName', self.polygonsLogName)
        Project.writeEntry(scope, 'polygonsLogPath', self.polygonsLogPath)


class LayerCollection:

    settings = None  # LayerCollectionSettings()

    pointsLayer = None
    pointsLayerId = ''
    linesLayer = None
    linesLayerId = ''
    polygonsLayer = None
    polygonsLayerId = ''

    pointsBuffer = None
    pointsBufferId = ''
    linesBuffer = None
    linesBufferId = ''
    polygonsBuffer = None
    polygonsBufferId = ''

    pointsLog = None
    pointsLogId = ''
    linesLog = None
    linesLogId = ''
    polygonsLog = None
    polygonsLogId = ''

    # Internal variables

    _iface = None # QgsInterface()
    _collectionGroupIndex = -1
    _bufferGroupIndex = -1
    _highlights = []  # [QgsHighlight]

    filter = ''
    selection = ''
    highlight = ''

    def __init__(self, iface, settings):
        self._iface = iface
        self.settings = settings
        # If the legend indexes change make sure we stay updated
        self._iface.legendInterface().groupIndexChanged.connect(self._groupIndexChanged)
        # If the layers are removed we need to remove them too
        QgsMapLayerRegistry.instance().layersRemoved.connect(self._layersRemoved)

    def initialise(self):
        return self.loadCollection()

    def unload(self):
        pass

    def _groupIndexChanged(self, oldIndex, newIndex):
        if (oldIndex == self._collectionGroupIndex):
            self._collectionGroupIndex = newIndex
        elif (oldIndex == self._bufferGroupIndex):
            self._bufferGroupIndex = newIndex

    # If a layer is removed from the registry, (i.e. closed), we can't use it anymore
    def _layersRemoved(self, layerList):
        for layerId in layerList:
            if layerId == '':
                pass
            elif layerId == self.pointsLayerId:
                self.pointsLayer = None
                self.pointsLayerId = ''
            elif layerId == self.linesLayerId:
                self.linesLayer = None
                self.linesLayerId = ''
            elif layerId == self.polygonsLayerId:
                self.polygonsLayer = None
                self.polygonsLayerId = ''
            elif layerId == self.pointsBufferId:
                self.pointsBuffer = None
                self.pointsBufferId = ''
            elif layerId == self.linesBufferId:
                self.linesBuffer = None
                self.linesBufferId = ''
            elif layerId == self.polygonsBufferId:
                self.polygonsBuffer = None
                self.polygonsBufferId = ''

    def _removeLayer(self, layerName):
        layerList = QgsMapLayerRegistry.instance().mapLayersByName(layerName)
        for layer in layerList:
            QgsMapLayerRegistry.instance().removeMapLayer(layer.id())

    # Load the main layer, must alreay exist
    def _loadLayer(self, layerPath, layerName, stylePath):
        layer = None
        layerId = ''
        if (layerName and layerPath):
            self._removeLayer(layerName)
            layer = QgsVectorLayer(layerPath, layerName, 'ogr')
        if layer and layer.isValid():
            layerId = layer.id()
            self._setDefaultSnapping(layer)
            layer.loadNamedStyle(stylePath)
            layer = layers.addLayerToLegend(self._iface, layer, self._collectionGroupIndex)
        else:
            layer = None
        return layer, layerId

    # Load the buffer layer, create it if it doesn't alreay exist
    def _loadBufferLayer(self, sourceLayer, layerPath, layerName):
        layer = None
        layerId = ''
        if (layerName and layerPath and sourceLayer and sourceLayer.isValid()):
            self._removeLayer(layerName)
            if not QFile.exists(layerPath):
                # If the layer doesn't exist, clone from the source layer
                layer = layers.cloneAsShapefile(sourceLayer, layerPath, layerName)
            else:
                # If the layer does exist, then load it and copy the style
                layer = QgsVectorLayer(layerPath, layerName, 'ogr')
                if layer and layer.isValid():
                    layers.loadStyle(layer, fromLayer=sourceLayer)
        if layer and layer.isValid():
            layerId = layer.id()
            self._setDefaultSnapping(layer)
            layer.startEditing()
            layer = layers.addLayerToLegend(self._iface, layer, self._bufferGroupIndex)
        else:
            layer = None
        return layer, layerId

    # Load the log layer, create it if it doesn't alreay exist
    def _loadLogLayer(self, sourceLayer, layerPath, layerName):
        layer = None
        layerId = ''
        if (layerName and layerPath and sourceLayer and sourceLayer.isValid()):
            self._removeLayer(layerName)
            if not QFile.exists(layerPath):
                # If the layer doesn't exist, clone from the source layer
                layer = layers.cloneAsShapefile(sourceLayer, layerPath, layerName)
                if layer and layer.isValid():
                    layer.dataProvider().addAttributes([QgsField('timestamp', QVariant.String, '', 10, 0, 'timestamp')])
                    layer.dataProvider().addAttributes([QgsField('event', QVariant.String, '', 6, 0, 'event')])
            else:
                # If the layer does exist, then load it and copy the style
                layer = QgsVectorLayer(layerPath, layerName, 'ogr')
                if layer and layer.isValid():
                    layers.loadStyle(layer, fromLayer=sourceLayer)
        if layer and layer.isValid():
            layerId = layer.id()
            layer.setFeatureFormSuppress(QgsVectorLayer.SuppressOn)
        else:
            layer = None
        return layer, layerId

    # Load the collection layers if not already loaded
    def loadCollection(self):

        # Load the main layers
        if self._collectionGroupIndex < 0:
            self._collectionGroupIndex = layers.createLayerGroup(self._iface, self.settings.collectionGroupName, self.settings.parentGroupName)
        self.polygonsLayer, self.polygonsLayerId = self._loadLayer(self.settings.polygonsLayerPath, self.settings.polygonsLayerName, self.settings.polygonsStylePath)
        self.linesLayer, self.linesLayerId = self._loadLayer(self.settings.linesLayerPath, self.settings.linesLayerName, self.settings.linesStylePath)
        self.pointsLayer, self.pointsLayerId = self._loadLayer(self.settings.pointsLayerPath, self.settings.pointsLayerName, self.settings.pointsStylePath)

        # Load the edit buffers if required
        if self.settings.bufferGroupName:
            if self._bufferGroupIndex < 0:
                grp = layers.insertChildGroup(self.settings.collectionGroupName, self.settings.bufferGroupName, 0)
                self._bufferGroupIndex = layers.getGroupIndex(self._iface, self.settings.bufferGroupName)
            self.polygonsBuffer, self.polygonsBufferId = self._loadBufferLayer(self.polygonsLayer, self.settings.polygonsBufferPath, self.settings.polygonsBufferName)
            self.linesBuffer, self.linesBufferId = self._loadBufferLayer(self.linesLayer, self.settings.linesBufferPath, self.settings.linesBufferName)
            self.pointsBuffer, self.pointsBufferId = self._loadBufferLayer(self.pointsLayer, self.settings.pointsBufferPath, self.settings.pointsBufferName)
            for child in grp.children():
                child.setExpanded(False)

        # Load the log buffers if required
        if self.settings.log:
            self.polygonsLog, self.polygonsLogId = self._loadLogLayer(self.polygonsLayer, self.settings.polygonsLogPath, self.settings.polygonsLogName)
            self.linesLog, self.linesLogId = self._loadLogLayer(self.linesLayer, self.settings.linesLogPath, self.settings.linesLogName)
            self.pointsLog, self.pointsLogId = self._loadLogLayer(self.pointsLayer, self.settings.pointsLogPath, self.settings.pointsLogName)

        # TODO actually check if is OK
        return True

    def _setDefaultSnapping(self, layer):
        res = QgsProject.instance().snapSettingsForLayer(layer.id())
        if not res[0]:
            QgsProject.instance().setSnapSettingsForLayer(layer.id(), True, QgsSnapper.SnapToVertex, QgsTolerance.Pixels, 10.0, False)

    def isWritable(self):
        return ((self.pointsLayer is None or layers.isWritable(self.pointsLayer))
                and (self.linesLayer is None or layers.isWritable(self.linesLayer))
                and (self.polygonsLayer is None or layers.isWritable(self.polygonsLayer))
                and (self.pointsBuffer is None or layers.isWritable(self.pointsBuffer))
                and (self.linesBuffer is None or layers.isWritable(self.linesBuffer))
                and (self.polygonsBuffer is None or layers.isWritable(self.polygonsBuffer))
                and (self.pointsLog is None or layers.isWritable(self.pointsLog))
                and (self.linesLog is None or layers.isWritable(self.linesLog))
                and (self.polygonsLog is None or layers.isWritable(self.polygonsLog)))

    def mergeBuffers(self, undoMessage='Merge Buffers', timestamp=None):
        if timestamp is None and self.settings.log:
            timestamp = utils.timestamp()
        merge = True
        if layers.copyAllFeatures(self.pointsBuffer, self.pointsLayer, undoMessage + ' - copy points', self.pointsLog, timestamp):
            self._clearBuffer(self.pointsBuffer, undoMessage + ' - delete points')
        else:
            merge = False
        if layers.copyAllFeatures(self.linesBuffer, self.linesLayer, undoMessage + ' - copy lines', self.linesLog, timestamp):
            self._clearBuffer(self.linesBuffer, undoMessage + ' - delete lines')
        else:
            merge = False
        if layers.copyAllFeatures(self.polygonsBuffer, self.polygonsLayer, undoMessage + ' - copy polygons', self.polygonsLog, timestamp):
            self._clearBuffer(self.polygonsBuffer, undoMessage + ' - delete polygons')
        else:
            merge = False
        return merge

    def clearBuffers(self, undoMessage='Clear Buffers'):
        self._clearBuffer(self.pointsBuffer, undoMessage + ' - points')
        self._clearBuffer(self.linesBuffer, undoMessage + ' - lines')
        self._clearBuffer(self.polygonsBuffer, undoMessage + ' - polygons')

    def _clearBuffer(self, layer, undoMessage, timestamp=None):
        return layers.deleteAllFeatures(layer, undoMessage, timestamp) and layer.commitChanges() and layer.startEditing()

    def moveFeatureRequestToBuffers(self, featureRequest, logMessage='Move Features', timestamp=None):
        if self.copyFeatureRequestToBuffers(featureRequest, logMessage, timestamp):
            self.deleteFeatureRequest(featureRequest, logMessage, timestamp)

    def copyFeatureRequestToBuffers(self, featureRequest, logMessage='Copy Features to Buffer', timestamp=None):
        return (layers.copyFeatureRequest(featureRequest, self.pointsLayer, self.pointsBuffer, logMessage + ' - points', self.pointsLog, timestamp)
                and layers.copyFeatureRequest(featureRequest, self.linesLayer, self.linesBuffer, logMessage + ' - lines', self.linesLog, timestamp)
                and layers.copyFeatureRequest(featureRequest, self.polygonsLayer, self.polygonsBuffer, logMessage + ' - polygons', self.polygonsLog, timestamp))

    def deleteFeatureRequest(self, featureRequest, logMessage = 'Delete Features', timestamp=None):
        if timestamp is None and self.settings.log:
            timestamp = utils.timestamp()
        layers.deleteFeatureRequest(featureRequest, self.pointsLayer, logMessage + ' - points', self.pointsLog, timestamp)
        layers.deleteFeatureRequest(featureRequest, self.linesLayer, logMessage + ' - lines', self.linesLog, timestamp)
        layers.deleteFeatureRequest(featureRequest, self.polygonsLayer, logMessage + ' - polygons', self.polygonsLog, timestamp)

    def setVisible(self, status):
        self.setPointsVisible(status)
        self.setLinesVisible(status)
        self.setPolygonsVisible(status)

    def setPointsVisible(self, status):
        self._iface.legendInterface().setLayerVisible(self.pointsLayer, status)

    def setLinesVisible(self, status):
        self._iface.legendInterface().setLayerVisible(self.linesLayer, status)

    def setPolygonsVisible(self, status):
        self._iface.legendInterface().setLayerVisible(self.polygonsLayer, status)

    def applyFilter(self, expression):
        self.filter = expression
        layers.applyFilter(self._iface, self.pointsLayer, expression)
        layers.applyFilter(self._iface, self.linesLayer, expression)
        layers.applyFilter(self._iface, self.polygonsLayer, expression)

    def clearFilter(self):
        self.applyFilter('')

    def applySelection(self, expression):
        self.selection = expression
        request = QgsFeatureRequest().setFilterExpression(expression)
        layers.applySelectionRequest(self.pointsLayer, request)
        layers.applySelectionRequest(self.linesLayer, request)
        layers.applySelectionRequest(self.polygonsLayer, request)

    def clearSelection(self):
        if self.pointsLayer:
            self.pointsLayer.removeSelection()
        if self.linesLayer:
            self.linesLayer.removeSelection()
        if self.polygonsLayer:
            self.polygonsLayer.removeSelection()

    def zoomToExtent(self):
        extent = self.extent()
        if (extent is not None and not extent.isNull()):
            extent.scale(1.05)
            self._iface.mapCanvas().setExtent(extent)
            self._iface.mapCanvas().refresh()

    def extent(self):
        extent = None
        extent = self._extendExtent(extent, self.pointsLayer)
        extent = self._extendExtent(extent, self.linesLayer)
        extent = self._extendExtent(extent, self.polygonsLayer)
        extent = self._extendExtent(extent, self.pointsBuffer)
        extent = self._extendExtent(extent, self.linesBuffer)
        extent = self._extendExtent(extent, self.polygonsBuffer)
        return extent

    def _extendExtent(self, extent, layer):
        if (layer is not None and layer.isValid() and layer.featureCount() > 0 and self._iface.legendInterface().isLayerVisible(layer)):
            layer.updateExtents()
            layerExtent = layer.extent()
            if layerExtent.isNull() or layerExtent.isEmpty():
                return extent
            if extent == None:
                extent = layerExtent
            else:
                extent.combineExtentWith(layerExtent)
        return extent

    def uniqueValues(self, fieldName):
        vals = set()
        vals.update(layers.uniqueValues(self.pointsLayer, fieldName))
        vals.update(layers.uniqueValues(self.linesLayer, fieldName))
        vals.update(layers.uniqueValues(self.polygonsLayer, fieldName))
        vals.discard(None)
        vals.discard(NULL)
        vals.discard('')
        return sorted(vals)

    def updateAttribute(self, attribute, value, expression=None):
        layers.updateAttribute(self.pointsLayer, attribute, value, expression)
        layers.updateAttribute(self.linesLayer, attribute, value, expression)
        layers.updateAttribute(self.polygonsLayer, attribute, value, expression)

    def updateBufferAttribute(self, attribute, value, expression=None):
        layers.updateAttribute(self.pointsBuffer, attribute, value, expression)
        layers.updateAttribute(self.linesBuffer, attribute, value, expression)
        layers.updateAttribute(self.polygonsBuffer, attribute, value, expression)

    def clearHighlight(self):
        self.highlight = ''
        del self._highlights[:]

    def applyHighlight(self, requestOrExpr, color=None, buff=None, minWidth=None):
        self.clearHighlight()
        self.addHighlight(requestOrExpr, color, buff, minWidth)

    def addHighlight(self, requestOrExpr, color=None, buff=None, minWidth=None):
        request = None
        if type(requestOrExpr) == QgsFeatureRequest:
            request = requestOrExpr
            self.highlight = request.filterExpression()
        else:
            request = QgsFeatureRequest()
            request.setFilterExpression(requestOrExpr)
            self.highlight = requestOrExpr
        for feature in self.polygonsLayer.getFeatures(request):
            hl = layers.addHighlight(self._iface.mapCanvas(), feature, self.polygonsLayer, color, buff, minWidth)
            self._highlights.append(hl)
        for feature in self.linesLayer.getFeatures(request):
            hl = layers.addHighlight(self._iface.mapCanvas(), feature, self.linesLayer, color, buff, minWidth)
            self._highlights.append(hl)
        for feature in self.pointsLayer.getFeatures(request):
            hl = layers.addHighlight(self._iface.mapCanvas(), feature, self.pointsLayer, color, buff, minWidth)
            self._highlights.append(hl)
