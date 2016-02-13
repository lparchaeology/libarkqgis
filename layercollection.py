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

from PyQt4.QtCore import QVariant, QDir

from qgis.core import QGis, QgsMapLayerRegistry, QgsVectorLayer, QgsProject, QgsSnapper, QgsTolerance, QgsMapLayer, QgsFeatureRequest, QgsRectangle, QgsLayerTreeGroup
from qgis.gui import QgsMessageBar, QgsHighlight

import utils, layers, snapping

class LayerCollectionSettings:

    collection = ''

    collectionGroupName = ''
    parentGroupName = ''

    buffersGroupName = ''
    bufferSuffix = ''

    pointsLayerProvider = ''
    pointsLayerName = ''
    pointsLayerPath = ''
    pointsStylePath = ''

    linesLayerProvider = ''
    linesLayerName = ''
    linesLayerPath = ''
    linesStylePath = ''

    polygonsLayerProvider = ''
    polygonsLayerName = ''
    polygonsLayerPath = ''
    polygonsStylePath = ''

    @staticmethod
    def fromProject(projectScope, collection):
        scope = projectScope + '/collections/' + collection
        lcs = LayerCollectionSettings()
        lcs.collection = Project.readEntry(scope, 'collection')
        lcs.collectionGroupName = Project.readEntry(scope, 'collectionGroupName')
        lcs.parentGroupName = Project.readEntry(scope, 'parentGroupName')
        lcs.buffersGroupName = Project.readEntry(scope, 'buffersGroupName')
        lcs.bufferSuffix = Project.readEntry(scope, 'bufferSuffix')
        lcs.pointsLayerProvider = Project.readEntry(scope, 'pointsLayerProvider')
        lcs.pointsLayerLabel = Project.readEntry(scope, 'pointsLayerLabel')
        lcs.pointsLayerName = Project.readEntry(scope, 'pointsLayerName')
        lcs.pointsLayerPath = Project.readEntry(scope, 'pointsLayerPath')
        lcs.pointsStylePath = Project.readEntry(scope, 'pointsStylePath')
        lcs.linesLayerProvider = Project.readEntry(scope, 'linesLayerProvider')
        lcs.linesLayerLabel = Project.readEntry(scope, 'linesLayerLabel')
        lcs.linesLayerName = Project.readEntry(scope, 'linesLayerName')
        lcs.linesLayerPath = Project.readEntry(scope, 'linesLayerPath')
        lcs.linesStylePath = Project.readEntry(scope, 'linesStylePath')
        lcs.polygonsLayerProvider = Project.readEntry(scope, 'polygonsLayerProvider')
        lcs.poolygonsLayerLabel = Project.readEntry(scope, 'poolygonsLayerLabel')
        lcs.polygonsLayerName = Project.readEntry(scope, 'polygonsLayerName')
        lcs.polygonsLayerPath = Project.readEntry(scope, 'polygonsLayerPath')
        lcs.polygonsStylePath = Project.readEntry(scope, 'polygonsStylePath')
        return lcs

    @staticmethod
    def toProject(projectScope, collection, lcs):
        scope = projectScope + '/collections/' + lcs.collection
        Project.writeEntry(scope, 'collection', lcs.collection)
        Project.writeEntry(scope, 'collectionGroupName', lcs.collectionGroupName)
        Project.writeEntry(scope, 'collectionGroupName', lcs.collectionGroupName)
        Project.writeEntry(scope, 'parentGroupName', lcs.parentGroupName)
        Project.writeEntry(scope, 'buffersGroupName', lcs.buffersGroupName)
        Project.writeEntry(scope, 'bufferSuffix', lcs.bufferSuffix)
        Project.writeEntry(scope, 'pointsLayerProvider', lcs.pointsLayerProvider)
        Project.writeEntry(scope, 'pointsLayerLabel', lcs.pointsLayerLabel)
        Project.writeEntry(scope, 'pointsLayerName', lcs.pointsLayerName)
        Project.writeEntry(scope, 'pointsLayerPath', lcs.pointsLayerPath)
        Project.writeEntry(scope, 'pointsStylePath', lcs.pointsStylePath)
        Project.writeEntry(scope, 'linesLayerProvider', lcs.linesLayerProvider)
        Project.writeEntry(scope, 'linesLayerLabel', lcs.linesLayerLabel)
        Project.writeEntry(scope, 'linesLayerName', lcs.linesLayerName)
        Project.writeEntry(scope, 'linesLayerPath', lcs.linesLayerPath)
        Project.writeEntry(scope, 'linesStylePath', lcs.linesStylePath)
        Project.writeEntry(scope, 'polygonsLayerProvider', lcs.polygonsLayerProvider)
        Project.writeEntry(scope, 'poolygonsLayerLabel', lcs.poolygonsLayerLabel)
        Project.writeEntry(scope, 'polygonsLayerName', lcs.polygonsLayerName)
        Project.writeEntry(scope, 'polygonsLayerPath', lcs.polygonsLayerPath)
        Project.writeEntry(scope, 'polygonsStylePath', lcs.polygonsStylePath)


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

    # Internal variables

    _iface = None # QgsInterface()
    _collectionGroupIndex = -1
    _buffersGroupIndex = -1
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
        self.unloadBuffers()

    def unloadBuffers(self):
        if self.pointsBuffer is not None:
            QgsMapLayerRegistry.instance().removeMapLayer(self.pointsBuffer.id())
        if self.linesBuffer is not None:
            QgsMapLayerRegistry.instance().removeMapLayer(self.linesBuffer.id())
        if self.polygonsBuffer is not None:
            QgsMapLayerRegistry.instance().removeMapLayer(self.polygonsBuffer.id())
        if self._buffersGroupIndex >= 0:
            self._iface.legendInterface().removeGroup(self._buffersGroupIndex)

    def _removeOldBuffers(self):
        layerId = layers.getLayerId(self.settings.pointsLayerName + self.settings.bufferSuffix)
        QgsMapLayerRegistry.instance().removeMapLayer(layerId)
        layerId = layers.getLayerId(self.settings.linesLayerName + self.settings.bufferSuffix)
        QgsMapLayerRegistry.instance().removeMapLayer(layerId)
        layerId = layers.getLayerId(self.settings.polygonsLayerName + self.settings.bufferSuffix)
        QgsMapLayerRegistry.instance().removeMapLayer(layerId)
        buffersGroupIndex = layers.getGroupIndex(self._iface, self.settings.buffersGroupName)
        if buffersGroupIndex >= 0:
            self._iface.legendInterface().removeGroup(buffersGroupIndex)

    def _groupIndexChanged(self, oldIndex, newIndex):
        if (oldIndex == self._collectionGroupIndex):
            self._collectionGroupIndex = newIndex
        elif (oldIndex == self._buffersGroupIndex):
            self._buffersGroupIndex = newIndex

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

    def _loadLayer(self, layerName, layerPath, layerProvider, stylePath, groupIndex):
        if (layerName is None or layerName == '' or layerPath is None or layerPath == ''):
            return None, ''
        layer = None
        # If the layer is already loaded, use it and return
        layerList = QgsMapLayerRegistry.instance().mapLayersByName(layerName)
        if (len(layerList) > 0):
            layer = layerList[0]
            self._iface.legendInterface().moveLayer(layer, groupIndex)
        else:
            # Otherwise load the layer and add it to the legend
            layer = QgsVectorLayer(layerPath, layerName, layerProvider)
            layer = layers.addLayerToLegend(self._iface, layer, groupIndex)

        if (layer is not None and layer.isValid()):
            self._setDefaultSnapping(layer)
            if (stylePath is not None and stylePath != ''):
                layer.loadNamedStyle(stylePath)
            return layer, layer.id()

        return None, ''

    # Load the collection layers if not already loaded
    def loadCollection(self):
        if (self._collectionGroupIndex < 0):
            self._collectionGroupIndex = layers.createLayerGroup(self._iface, self.settings.collectionGroupName, self.settings.parentGroupName)
        self.polygonsLayer, self.polygonsLayerId = self._loadLayer(self.settings.polygonsLayerName, self.settings.polygonsLayerPath, self.settings.polygonsLayerProvider, self.settings.polygonsStylePath, self._collectionGroupIndex)
        self.linesLayer, self.linesLayerId = self._loadLayer(self.settings.linesLayerName, self.settings.linesLayerPath, self.settings.linesLayerProvider, self.settings.linesStylePath, self._collectionGroupIndex)
        self.pointsLayer, self.pointsLayerId = self._loadLayer(self.settings.pointsLayerName, self.settings.pointsLayerPath, self.settings.pointsLayerProvider, self.settings.pointsStylePath, self._collectionGroupIndex)
        # TODO actually check if is OK
        return True

    def _setDefaultSnapping(self, layer):
        res = QgsProject.instance().snapSettingsForLayer(layer.id())
        if not res[0]:
            QgsProject.instance().setSnapSettingsForLayer(layer.id(), True, QgsSnapper.SnapToVertex, QgsTolerance.Pixels, 10.0, False)

    # Setup the in-memory buffer layers
    def createBuffers(self):

        self._removeOldBuffers()

        collectionGroupIndex = layers.childGroupIndex(self.settings.parentGroupName, self.settings.collectionGroupName)
        grp = layers.insertChildGroup(self.settings.parentGroupName, self.settings.buffersGroupName, collectionGroupIndex)
        self._buffersGroupIndex = layers.getGroupIndex(self._iface, self.settings.buffersGroupName)

        self.polygonsBuffer, self.polygonsBufferId = self._createBufferLayer(self.polygonsLayer, self.settings.polygonsStylePath)
        self.linesBuffer, self.linesBufferId = self._createBufferLayer(self.linesLayer, self.settings.linesStylePath)
        self.pointsBuffer, self.pointsBufferId = self._createBufferLayer(self.pointsLayer, self.settings.pointsStylePath)

        for child in grp.children():
            child.setExpanded(False)

    def _createBufferLayer(self, layer, stylePath):
        if (layer is not None and layer.isValid()):
            memLayer = layers.cloneAsMemoryLayer(layer, layer.name() + self.settings.bufferSuffix, stylePath)
            if (memLayer is not None and memLayer.isValid()):
                memLayer = layers.addLayerToLegend(self._iface, memLayer, self._buffersGroupIndex)
                memLayer.startEditing()
                self._setDefaultSnapping(memLayer)
                return memLayer, memLayer.id()
        return None, ''

    def isWritable(self):
        return ((self.pointsLayer is None or layers.isWritable(self.pointsLayer))
                and (self.linesLayer is None or layers.isWritable(self.linesLayer))
                and (self.polygonsLayer is None or layers.isWritable(self.polygonsLayer)))

    def mergeBuffers(self, undoMessage='Merge Buffers'):
        merge = True
        if layers.copyAllFeatures(self.pointsBuffer, self.pointsLayer, undoMessage + ' - copy points'):
            self._clearBuffer(self.pointsBuffer, undoMessage + ' - delete points')
        else:
            merge = False
        if layers.copyAllFeatures(self.linesBuffer, self.linesLayer, undoMessage + ' - copy lines'):
            self._clearBuffer(self.linesBuffer, undoMessage + ' - delete lines')
        else:
            merge = False
        if layers.copyAllFeatures(self.polygonsBuffer, self.polygonsLayer, undoMessage + ' - copy polygons'):
            self._clearBuffer(self.polygonsBuffer, undoMessage + ' - delete polygons')
        else:
            merge = False
        return merge

    def clearBuffers(self, undoMessage='Clear Buffers'):
        self._clearBuffer(self.pointsBuffer, undoMessage + ' - points')
        self._clearBuffer(self.linesBuffer, undoMessage + ' - lines')
        self._clearBuffer(self.polygonsBuffer, undoMessage + ' - polygons')

    def _clearBuffer(self, layer, undoMessage):
        return layers.deleteAllFeatures(layer, undoMessage) and layer.commitChanges() and layer.startEditing()

    def moveFeatureRequestToBuffers(self, featureRequest):
        if self.copyFeatureRequestToBuffers(featureRequest):
            self.deleteFeatureRequest(featureRequest)

    def copyFeatureRequestToBuffers(self, featureRequest):
        return (layers.copyFeatureRequest(featureRequest, self.pointsLayer, self.pointsBuffer, 'Copy point features to buffer')
                and layers.copyFeatureRequest(featureRequest, self.linesLayer, self.linesBuffer, 'Copy line features to buffer')
                and layers.copyFeatureRequest(featureRequest, self.polygonsLayer, self.polygonsBuffer, 'Copy polygon features to buffer'))

    def deleteFeatureRequest(self, featureRequest):
        layers.deleteFeatureRequest(featureRequest, self.pointsLayer, 'Delete point features')
        layers.deleteFeatureRequest(featureRequest, self.linesLayer, 'Delete line features')
        layers.deleteFeatureRequest(featureRequest, self.polygonsLayer, 'Delete polygon features')

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
        return list(vals)

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

    def applyHighlight(self, requestOrExpr, color=None, alpha=None, buff=None, minWidth=None):
        self.clearHighlight()
        self.addHighlight(requestOrExpr, color, alpha, buff, minWidth)

    def addHighlight(self, requestOrExpr, color=None, alpha=None, buff=None, minWidth=None):
        request = None
        if type(requestOrExpr) == QgsFeatureRequest:
            request = requestOrExpr
            self.highlight = request.filterExpression()
        else:
            request = QgsFeatureRequest()
            request.setFilterExpression(requestOrExpr)
            self.highlight = requestOrExpr
        for feature in self.polygonsLayer.getFeatures(request):
            hl = layers.addHighlight(self._iface.mapCanvas(), feature, self.polygonsLayer, color, alpha, buff, minWidth)
            self._highlights.append(hl)
        for feature in self.linesLayer.getFeatures(request):
            hl = layers.addHighlight(self._iface.mapCanvas(), feature, self.linesLayer, color, alpha, buff, minWidth)
            self._highlights.append(hl)
        for feature in self.pointsLayer.getFeatures(request):
            hl = layers.addHighlight(self._iface.mapCanvas(), feature, self.pointsLayer, color, alpha, buff, minWidth)
            self._highlights.append(hl)
