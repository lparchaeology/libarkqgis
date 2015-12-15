# -*- coding: utf-8 -*-
"""
/***************************************************************************
                                      Ark
                                 A QGIS plugin
             QGIS Plugin for ARK, the Archaeological Recording Kit
                              -------------------
        begin                : 2015-03-02
        git sha              : $Format:%H$
        copyright            : (C) 2015 by L - P: Heritage LLP
        copyright            : (C) 2015 by John Layt
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
from qgis.gui import QgsMessageBar

import utils, layers, snapping

class LayerCollectionSettings:

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


class LayerCollection:

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
    _settings = LayerCollectionSettings()
    _collectionGroupIndex = -1
    _buffersGroupIndex = -1

    filter = ''
    selection = ''

    def __init__(self, iface, settings):
        self._iface = iface
        self._settings = settings
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
        layerId = layers.getLayerId(self._settings.pointsLayerName + self._settings.bufferSuffix)
        QgsMapLayerRegistry.instance().removeMapLayer(layerId)
        layerId = layers.getLayerId(self._settings.linesLayerName + self._settings.bufferSuffix)
        QgsMapLayerRegistry.instance().removeMapLayer(layerId)
        layerId = layers.getLayerId(self._settings.polygonsLayerName + self._settings.bufferSuffix)
        QgsMapLayerRegistry.instance().removeMapLayer(layerId)
        buffersGroupIndex = layers.getGroupIndex(self._iface, self._settings.buffersGroupName)
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
            self._collectionGroupIndex = layers.createLayerGroup(self._iface, self._settings.collectionGroupName, self._settings.parentGroupName)
        self.polygonsLayer, self.polygonsLayerId = self._loadLayer(self._settings.polygonsLayerName, self._settings.polygonsLayerPath, self._settings.polygonsLayerProvider, self._settings.polygonsStylePath, self._collectionGroupIndex)
        self.linesLayer, self.linesLayerId = self._loadLayer(self._settings.linesLayerName, self._settings.linesLayerPath, self._settings.linesLayerProvider, self._settings.linesStylePath, self._collectionGroupIndex)
        self.pointsLayer, self.pointsLayerId = self._loadLayer(self._settings.pointsLayerName, self._settings.pointsLayerPath, self._settings.pointsLayerProvider, self._settings.pointsStylePath, self._collectionGroupIndex)
        # TODO actually check if is OK
        return True

    def _setDefaultSnapping(self, layer):
        # TODO Check if layer id already in settings, only set defaults if it isn't
        res = QgsProject.instance().snapSettingsForLayer(layer.id())
        if not res[0]:
            QgsProject.instance().setSnapSettingsForLayer(layer.id(), True, QgsSnapper.SnapToVertex, QgsTolerance.Pixels, 10.0, False)

    # Setup the in-memory buffer layers
    def createBuffers(self):

        self._removeOldBuffers()

        collectionGroupIndex = layers.childGroupIndex(self._settings.parentGroupName, self._settings.collectionGroupName)
        grp = layers.insertChildGroup(self._settings.parentGroupName, self._settings.buffersGroupName, collectionGroupIndex)
        self._buffersGroupIndex = layers.getGroupIndex(self._iface, self._settings.buffersGroupName)

        if (self.polygonsBuffer is None or not self.polygonsBuffer.isValid()):
            self.polygonsBuffer, self.polygonsBufferId = self._createBufferLayer(self.polygonsLayer, self._settings.polygonsStylePath)

        if (self.linesBuffer is None or not self.linesBuffer.isValid()):
            self.linesBuffer, self.linesBufferId = self._createBufferLayer(self.linesLayer, self._settings.linesStylePath)

        if (self.pointsBuffer is None or not self.pointsBuffer.isValid()):
            self.pointsBuffer, self.pointsBufferId = self._createBufferLayer(self.pointsLayer, self._settings.pointsStylePath)

        for child in grp.children():
            child.setExpanded(False)

    def _createBufferLayer(self, layer, stylePath):
        if (layer is not None and layer.isValid()):
            buffer = layers.cloneAsMemoryLayer(layer, layer.name() + self._settings.bufferSuffix, stylePath)
            if (buffer is not None and buffer.isValid()):
                buffer = layers.addLayerToLegend(self._iface, buffer, self._buffersGroupIndex)
                buffer.startEditing()
                self._setDefaultSnapping(buffer)
                return buffer, buffer.id()
        return None, ''

    def okToMergeBuffers(self):
        return self.isCollectionEditable()

    def isCollectionEditable(self):
        return ((self.pointsLayer is None or self._isLayerEditable(self.pointsLayer)) and
                (self.linesLayer is None or self._isLayerEditable(self.linesLayer)) and
                (self.polygonsLayer is None or self._isLayerEditable(self.polygonsLayer)))

    def _isLayerEditable(self, layer):
        if (layer is None or not layer.isValid()):
            utils.showCriticalMessage(self._iface, 'Cannot edit layer - Not a layer object')
            return False
        if (layer is None or not layer.isValid()):
            utils.showCriticalMessage(self._iface, 'Cannot edit layer ' + layer.name() + ' - Not a valid layer')
            return False
        if (layer.type() != QgsMapLayer.VectorLayer):
            utils.showCriticalMessage(self._iface, 'Cannot edit layer ' + layer.name() + ' - Not a vector layer')
            return False
        if (layer.isModified()):
            utils.showCriticalMessage(self._iface, 'Cannot edit layer ' + layer.name() + ' - Has pending modifications')
            return False
        # We don't check here as can turn filter off temporarily
        #if (layer.subsetString()):
        #    utils.showCriticalMessage(self._iface, 'Cannot edit layer ' + layer.name() + ' - Filter is applied')
        #    return False
        if (len(layer.vectorJoins()) > 0):
            utils.showCriticalMessage(self._iface, 'Cannot edit layer ' + layer.name() + ' - Layer has joins')
            return False
        return True

    def mergeBuffers(self, undoMessage):
        if layers.copyAllFeatures(self.pointsBuffer, self.pointsLayer, undoMessage + ' - points'):
            self._clearBuffer(self.pointsBuffer, undoMessage + ' - points')
        if layers.copyAllFeatures(self.linesBuffer, self.linesLayer, undoMessage + ' - lines'):
            self._clearBuffer(self.linesBuffer, undoMessage + ' - lines')
        if layers.copyAllFeatures(self.polygonsBuffer, self.polygonsLayer, undoMessage + ' - polygons'):
            self._clearBuffer(self.polygonsBuffer, undoMessage + ' - polygons')

    def clearBuffers(self, undoMessage):
        self._clearBuffer(self.pointsBuffer, undoMessage + ' - points')
        self._clearBuffer(self.linesBuffer, undoMessage + ' - lines')
        self._clearBuffer(self.polygonsBuffer, undoMessage + ' - polygons')

    def _clearBuffer(self, layer, undoMessage):
        ok = layers.deleteAllFeatures(layer, undoMessage)
        if ok:
            layer.commitChanges()
            layer.startEditing()

    def moveToBuffers(self, featureRequest):
        if (layers.copyFeatureRequest(featureRequest, self.pointsLayer, self.pointsBuffer, 'Copy point features to buffer')
            and layers.copyFeatureRequest(featureRequest, self.linesLayer, self.linesBuffer, 'Copy line features to buffer')
            and layers.copyFeatureRequest(featureRequest, self.polygonsLayer, self.polygonsBuffer, 'Copy polygon features to buffer')):
            layers.deleteFeatureRequest(featureRequest, self.pointsLayer, 'Delete point features')
            layers.deleteFeatureRequest(featureRequest, self.linesLayer, 'Delete line features')
            layers.deleteFeatureRequest(featureRequest, self.polygonsLayer, 'Delete polygon features')
        else:
            self.clearBuffers('')

    def deleteRequest(self, featureRequest):
        layers.deleteFeatureRequest(featureRequest, self.pointsLayer, 'Delete point features')
        layers.deleteFeatureRequest(featureRequest, self.linesLayer, 'Delete line features')
        layers.deleteFeatureRequest(featureRequest, self.polygonsLayer, 'Delete polygon features')

    def showPoints(self, status):
        self._iface.legendInterface().setLayerVisible(self.pointsLayer, status)

    def showLines(self, status):
        self._iface.legendInterface().setLayerVisible(self.linesLayer, status)

    def showPolygons(self, status):
        self._iface.legendInterface().setLayerVisible(self.polygonsLayer, status)


    def applyFieldFilterRange(self, field, valueRange):
        # TODO string versus decimal field type!
        filter = ''
        for cxtStr in valueRange.split():
            clause = ''
            if cxtStr.find('-') >= 0:
                cxtList = cxtStr.split('-')
                clause = '("%s" >= %d and "%s" <= %d)' % (field, int(cxtList[0]), field, int(cxtList[1]))
            else:
                clause = '"%s" = %d' % (field, int(cxtStr))
            if filter:
                filter += ' or '
            filter += clause
        self.applyFilter(filter)


    def applyFieldFilterList(self, field, valueList):
        # TODO string versus decimal field type!
        clause = '"' + field + '" = %d'
        filter = ''
        if (len(valueList) > 0):
            filter += clause % valueList[0]
            for value in valueList[1:]:
                filter += ' or '
                filter += clause % value
        self.applyFilter(filter)


    def applyFilter(self, filter):
        self.filter = filter
        self._applyLayerFilter(self.pointsLayer, self.filter)
        self._applyLayerFilter(self.linesLayer, self.filter)
        self._applyLayerFilter(self.polygonsLayer, self.filter)


    def _applyLayerFilter(self, layer, filter):
        if (layer is None or not layer.isValid()):
            return
        self._iface.mapCanvas().stopRendering()
        if (layer.type() != QgsMapLayer.VectorLayer):
            utils.showMessage(self._iface, 'Cannot apply filter: Not a vector layer', QgsMessageBar.WARNING, 3)
            return
        if (layer.isEditable()):
            utils.showMessage(self._iface, 'Cannot apply filter: Layer is in editing mode', QgsMessageBar.WARNING, 3)
            return
        if (not layer.dataProvider().supportsSubsetString()):
            utils.showMessage(self._iface, 'Cannot apply filter: Subsets not supported by layer', QgsMessageBar.WARNING, 3)
            return
        if (len(layer.vectorJoins()) > 0):
            utils.showMessage(self._iface, 'Cannot apply filter: Layer has joins', QgsMessageBar.WARNING, 3)
            return
        if (self._iface.mapCanvas().isDrawing()):
            utils.showMessage(self._iface, 'Cannot apply filter: Canvas is drawing', QgsMessageBar.WARNING, 3)
            return
        layer.setSubsetString(filter)
        self._iface.mapCanvas().refresh()
        self._iface.legendInterface().refreshLayerSymbology(layer)


    def applySelection(self, expression):
        self.selection = expression
        self._applyLayerSelection(self.pointsLayer, self.selection)
        self._applyLayerSelection(self.linesLayer, self.selection)
        self._applyLayerSelection(self.polygonsLayer, self.selection)


    def _applyLayerSelection(self, layer, expression):
        if layer is None or not layer.isValid():
            return
        fit = layer.getFeatures(QgsFeatureRequest().setFilterExpression(expression))
        layer.setSelectedFeatures([f.id() for f in fit])


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
        vals.update(self._uniqueValues(self.pointsLayer, fieldName))
        vals.update(self._uniqueValues(self.linesLayer, fieldName))
        vals.update(self._uniqueValues(self.polygonsLayer, fieldName))
        return list(vals)


    def _uniqueValues(self, layer, fieldName):
        return layer.uniqueValues(layer.fieldNameIndex(fieldName))


    def updateAttribute(self, attribute, value, expression=None):
        self._updateAttribute(self.pointsLayer, attribute, value, expression)
        self._updateAttribute(self.linesLayer, attribute, value, expression)
        self._updateAttribute(self.polygonsLayer, attribute, value, expression)


    def updateBufferAttribute(self, attribute, value, expression=None):
        self._updateAttribute(self.pointsBuffer, attribute, value, expression)
        self._updateAttribute(self.linesBuffer, attribute, value, expression)
        self._updateAttribute(self.polygonsBuffer, attribute, value, expression)


    def _updateAttribute(self, layer, attribute, value, expression=None):
        idx = layer.fieldNameIndex(attribute)
        fit = None
        if expression is None or expression == '':
            fit = layer.getFeatures()
        else:
            fit = layer.getFeatures(QgsFeatureRequest().setFilterExpression(expression))
        for f in fit:
            layer.changeAttributeValue(f.id(), idx, value)
