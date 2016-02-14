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

from PyQt4.QtCore import pyqtSignal, QFileInfo, QFile, QSettings
from PyQt4.QtGui import QDialog, QComboBox, QDialogButtonBox, QColor
from PyQt4.QtXml import QDomImplementation, QDomDocument

from qgis.core import QGis, QgsMapLayer, QgsMapLayerRegistry, QgsVectorLayer, QgsVectorFileWriter, QgsProject, QgsLayerTreeGroup, NULL, QgsFeature
from qgis.gui import QgsHighlight

import utils
from project import Project

# Layer Widgets

class ArkLayerComboBox(QComboBox):

    layerChanged = pyqtSignal()

    _layerType = None
    _geometryType = None
    _iface = None

    def __init__(self, iface, layerType=None, geometryType=None, parent=None):
        super(ArkLayerComboBox, self).__init__(parent)
        self._iface = iface
        self._layerType = layerType
        self._geometryType = geometryType
        self._loadLayers()

    def _addLayer(self, layer):
        self.addItem(layer.name(), layer.id())

    def _loadLayers(self):
        self.clear()
        for layer in self._iface.legendInterface().layers():
            if self._layerType is None and self._geometryType is None:
                self._addLayer(layer)
            elif (self._layerType == QgsMapLayer.RasterLayer and layer.type() == QgsMapLayer.RasterLayer):
                self._addLayer(layer)
            elif layer.type() == QgsMapLayer.VectorLayer:
                if (self._geometryType == None or layer.geometryType() == self._geometryType):
                    self._addLayer(layer)


class ArkSelectLayerDialog(QDialog):

    def __init__(self, iface, text='', label='', layerType=None, geometryType=None, parent=None):

        self.setWindowTitle(self.tr("Select Layer"))

        self._dialogLayout = QtGui.QVBoxLayout(self)

        if text:
            self._textLabel = QtGui.QLabel(self)
            self._textLabel.setText(text)
            self._dialogLayout.addWidget(self._textLabel)

        if (label or not text):
            self._comboLabel = QtGui.QLabel(self)
            if label:
                self._comboLabel.setText(label)
            elif not text:
                self._comboLabel.setText(self.tr('Layer:'))
            self._comboBox = ArkLayerComboBox(iface, layerType, geometryType, self)
            self._comboLayout = QtGui.QHBoxLayout()
            self._comboLayout.addWidget(self._comboLabel)
            self._comboLayout.addWidget(self._comboBox)
            self._dialogLayout.addLayout(self._comboLayout)
        else:
            self._comboBox = ArkLayerComboBox(iface, layerType, geometryType, self)
            self._dialogLayout.addWidget(self._comboBox)

        self._buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        self._buttonBox.accepted.connect(self.accept)
        self._buttonBox.rejected.connect(self.reject)
        self._comboLayout.addWidget(self._buttonBox)

    def layer(self):
        return QgsMapLayerRegistry.instance().mapLayer(self.layerId())

    def layerName(self):
        return self.layerComboBox.currentText()

    def layerId(self):
        return self.layerComboBox.itemData(self.layerComboBox.currentIndex())


# Layer management utilities

# Try find a style file to match a layer
def styleFilePath(layerPath, layerName, customStylePath, customStyleName, defaultStylePath, defaultStyleName):
    # First see if the layer itself has a default style saved
    if layerPath and layerName:
        filePath = layerPath + '/' + layerName + '.qml'
        if QFile.exists(filePath):
            return filePath
    # Next see if the default name has a style in the style folder
    if customStylePath and customStyleName:
        filePath = customStylePath + '/' + customStyleName + '.qml'
        if QFile.exists(filePath):
            return filePath
    # Finally, check the plugin folder for the default style
    if defaultStylePath and defaultStyleName:
        filePath = defaultStylePath + '/' + defaultStyleName + '.qml'
        if QFile.exists(filePath):
            return filePath
    # If we didn't anythign then don't use a style
    return ''

def shapeFilePath(layerPath, layerName):
    return layerPath + '/' + layerName + '.shp'

def createShapefile(filePath, wkbType, crs, fields):
    # WARNING This will overwrite existing files
    layer = QgsVectorFileWriter(filePath, 'System', fields, wkbType, crs)
    error = layer.hasError()
    del layer
    return error

def createMemoryLayer(name, wkbType, crsId, fields=None, styleURI=None, symbology=None):
    uri = wkbToMemoryType(wkbType) + "?crs=" + crsId + "&index=yes"
    mem = QgsVectorLayer(uri, name, 'memory')
    if (mem is not None and mem.isValid()):
        if fields:
            mem.dataProvider().addAttributes(fields.toList())
        else:
            mem.dataProvider().addAttributes([QgsField('id', QVariant.String, '', 10, 0, 'ID')])
        if styleURI:
            mem.loadNamedStyle(styleURI)
        if symbology:
            mem.readSymbology(symbology, '')
    return mem

def cloneAsMemoryLayer(layer, name, styleURI=None, symbology=None):
    if (layer is not None and layer.isValid() and layer.type() == QgsMapLayer.VectorLayer):
        if styleURI is None and symbology is None:
            symbology = getSymbology(layer)
        return createMemoryLayer(name, layer.wkbType(), layer.crs().authid(), layer.dataProvider().fields(), styleURI, symbology)
    return None

def duplicateAsMemoryLayer(layer, memName):
    mem = cloneAsMemoryLayer(layer, memName)
    mem.startEditing()
    fi = layer.getFeatures()
    for feature in fi:
        mem.addFeature(feature)
    mem.commitChanges()
    return mem

def getSymbology(source):
    di = QDomImplementation()
    documentType = di.createDocumentType('qgis', 'http://mrcc.com/qgis.dtd', 'SYSTEM')
    doc = QDomDocument(documentType)
    rootNode = doc.createElement('qgis')
    rootNode.setAttribute('version', str(QGis.QGIS_VERSION))
    doc.appendChild(rootNode)
    source.writeSymbology(rootNode, doc, '')
    return rootNode

def copySymbology(source, dest):
    dest.readSymbology(getSymbology(source), '')

def getGroupIndex(iface, groupName):
    groupIndex = -1
    i = 0
    for name in iface.legendInterface().groups():
        if (groupIndex < 0 and name == groupName):
            groupIndex = i
        i += 1
    return groupIndex

def createLayerGroup(iface, groupName, parentGroupName=''):
    groupIndex = getGroupIndex(iface, groupName)
    if (groupIndex >= 0):
        return groupIndex
    if parentGroupName:
        parentGroupIndex = getGroupIndex(iface, parentGroupName)
        if (parentGroupIndex >= 0):
            return iface.legendInterface().addGroup(groupName, True, parentGroupIndex)
    return iface.legendInterface().addGroup(groupName, True)

def getLayerId(layerName):
    layerList = QgsMapLayerRegistry.instance().mapLayersByName(layerName)
    if (len(layerList) > 0):
        return layerList[0].id()
    return None

def addLayerToLegend(iface, layer, group):
    if (layer is not None and layer.isValid()):
        ret = QgsMapLayerRegistry.instance().addMapLayer(layer)
        iface.legendInterface().moveLayer(layer, group)
        iface.legendInterface().refreshLayerSymbology(layer)
        return ret
    return layer

def wkbToMemoryType(wkbType):
    if (wkbType == QGis.WKBPoint):
        return 'point'
    elif (wkbType == QGis.WKBLineString):
        return 'linestring'
    elif (wkbType == QGis.WKBPolygon):
        return 'polygon'
    elif (wkbType == QGis.WKBMultiPoint):
        return 'multipoint'
    elif (wkbType == QGis.WKBMultiLineString):
        return 'multilinestring'
    elif (wkbType == QGis.WKBMultiPolygon):
        return 'multipolygon'
    elif (wkbType == QGis.WKBPoint25D):
        return 'point'
    elif (wkbType == QGis.WKBLineString25D):
        return 'linestring'
    elif (wkbType == QGis.WKBPolygon25D):
        return 'polygon'
    elif (wkbType == QGis.WKBMultiPoint25D):
        return 'multipoint'
    elif (wkbType == QGis.WKBMultiLineString25D):
        return 'multilinestring'
    elif (wkbType == QGis.WKBMultiPolygon25D):
        return 'multipolygon'
    return 'unknown'

def copyFeatureRequest(featureRequest, fromLayer, toLayer, undoMessage='Copy features'):
    ok = False
    if isInvalid(fromLayer) or not isWritable(toLayer):
        return ok
    # Stash the current subset
    fromSubset = fromLayer.subsetString()
    if fromSubset:
        fromLayer.setSubsetString('')
    toSubset = toLayer.subsetString()
    if toSubset:
        toLayer.setSubsetString('')
    # Copy the requested features
    wasEditing = toLayer.isEditable()
    if wasEditing or toLayer.startEditing():
        toLayer.beginEditCommand(undoMessage)
        ft = 0
        for feature in fromLayer.getFeatures(featureRequest):
            ft += 1
            ok = toLayer.addFeature(feature, False)
            if not ok:
                break
        if ok:
            toLayer.endEditCommand()
        else:
            toLayer.destroyEditCommand()
        if not wasEditing:
            if ok:
                ok = toLayer.commitChanges()
            else:
                toLayer.rollBack()
        if ft == 0:
            ok = True
    # Restore the previous selection and subset
    if fromSubset:
        fromLayer.setSubsetString(fromSubset)
    if toSubset:
        toLayer.setSubsetString(toSubset)
    return ok

def copyFeatureIds(featureIds, fromLayer, toLayer, undoMessage='Copy features'):
    ok = False
    if isInvalid(fromLayer) or not isWritable(toLayer):
        return ok
    # Stash the current selection and subset
    prevSelect = fromLayer.selectedFeaturesIds()
    fromSubset = fromLayer.subsetString()
    toSubset = toLayer.subsetString()
    fromLayer.removeSelection()
    if fromSubset:
        fromLayer.setSubsetString('')
    if toSubset:
        toLayer.setSubsetString('')
    # Select the requested features
    fromLayer.select(featureIds)
    # Copy the selected features
    if fromLayer.selectedFeatureCount() > 0:
        wasEditing = toLayer.isEditable()
        if wasEditing or toLayer.startEditing():
            toLayer.beginEditCommand(undoMessage)
            ok = toLayer.addFeatures(fromLayer.selectedFeatures(), False)
            if ok:
                toLayer.endEditCommand()
            else:
                toLayer.destroyEditCommand()
            if not wasEditing:
                if ok:
                    ok = toLayer.commitChanges()
                else:
                    toLayer.rollBack()
    else:
        ok = True
    # Restore the previous selection and subset
    fromLayer.removeSelection()
    if fromSubset:
        fromLayer.setSubsetString(fromSubset)
    if toSubset:
        toLayer.setSubsetString(toSubset)
    fromLayer.select(prevSelect)
    return ok

def copyAllFeatures(fromLayer, toLayer, undoMessage='Copy features'):
    ok = False
    if isInvalid(fromLayer) or not isWritable(toLayer):
        return ok
    # Stash the current selection and subset
    prevSelect = fromLayer.selectedFeaturesIds()
    fromSubset = fromLayer.subsetString()
    toSubset = toLayer.subsetString()
    fromLayer.removeSelection()
    if fromSubset:
        fromLayer.setSubsetString('')
    if toSubset:
        toLayer.setSubsetString('')
    # Select the requested features
    fromLayer.selectAll()
    # Copy the selected features
    if fromLayer.selectedFeatureCount() > 0:
        wasEditing = toLayer.isEditable()
        if wasEditing or toLayer.startEditing():
            toLayer.beginEditCommand(undoMessage)
            ok = toLayer.addFeatures(fromLayer.selectedFeatures(), False)
            if ok:
                toLayer.endEditCommand()
            else:
                toLayer.destroyEditCommand()
            if not wasEditing:
                if ok:
                    ok = toLayer.commitChanges()
                else:
                    toLayer.rollBack()
    else:
        ok = True
    # Restore the previous selection and subset
    fromLayer.removeSelection()
    if fromSubset:
        fromLayer.setSubsetString(fromSubset)
    if toSubset:
        toLayer.setSubsetString(toSubset)
    fromLayer.select(prevSelect)
    return ok

def deleteFeatureRequest(featureRequest, layer, undoMessage='Delete features'):
    ok = False
    if not isWritable(layer):
        return ok
    # Stash the current subset
    subset = layer.subsetString()
    if subset:
        layer.setSubsetString('')
    # Copy the requested features
    wasEditing = layer.isEditable()
    if wasEditing or layer.startEditing():
        layer.beginEditCommand(undoMessage)
        ft = 0
        for feature in layer.getFeatures(featureRequest):
            ft += 1
            ok = layer.deleteFeature(feature.id())
            if not ok:
                break
        if ok:
            layer.endEditCommand()
        else:
            layer.destroyEditCommand()
        if not wasEditing:
            if ok:
                ok = layer.commitChanges()
            else:
                layer.rollBack()
        if ft == 0:
            ok = True
    # Restore the previous subset
    if subset:
        layer.setSubsetString(subset)
    return ok

def deleteFeatureIds(featureIds, layer, undoMessage='Delete features'):
    ok = False
    if not isWritable(layer):
        return ok
    # Stash the current subset
    subset = layer.subsetString()
    if subset:
        layer.setSubsetString('')
    # Delete the requested features
    wasEditing = toLayer.isEditable()
    if wasEditing or layer.startEditing():
        layer.beginEditCommand(undoMessage)
        ok = layer.deleteFeatures(featureIds)
    if ok:
        layer.endEditCommand()
    else:
        layer.destroyEditCommand()
    if not wasEditing:
        if ok:
            ok = layer.commitChanges()
        else:
            layer.rollBack()
    # Restore the previous subset
    if subset:
        layer.setSubsetString(subset)
    return ok

def deleteAllFeatures(layer, undoMessage='Delete features'):
    ok = False
    if not isWritable(layer):
        return ok
    # Stash the current selection and subset
    prevSelect = layer.selectedFeaturesIds()
    subset = layer.subsetString()
    if subset:
        layer.setSubsetString('')
    # Select the requested features
    layer.selectAll()
    # Delete the requested features
    wasEditing = layer.isEditable()
    if wasEditing or layer.startEditing():
        layer.beginEditCommand(undoMessage)
        ok = layer.deleteSelectedFeatures()
    if ok:
        layer.endEditCommand()
    else:
        layer.destroyEditCommand()
    if not wasEditing:
        if ok:
            ok = layer.commitChanges()
        else:
            layer.rollBack()
    # Restore the previous selection and subset
    layer.removeSelection()
    if subset:
        layer.setSubsetString(subset)
    layer.select(prevSelect)
    return ok

def childGroupIndex(parentGroupName, childGroupName):
    root = QgsProject.instance().layerTreeRoot()
    if root is None:
        return -1
    parent = root.findGroup(parentGroupName)
    if parent is None:
        return -1
    idx = 0
    for child in parent.children():
        if isinstance(child, QgsLayerTreeGroup) and child.name() == childGroupName:
            break
        idx += 1
    return  idx

def insertChildGroup(parentGroupName, childGroupName, childIndex):
    root = QgsProject.instance().layerTreeRoot()
    if root is None:
        return None
    parent = root.findGroup(parentGroupName)
    if parent is None:
        return None
    return parent.insertGroup(childIndex, childGroupName)

def applyFilter(iface, layer, expression):
    if (layer is None or not layer.isValid() or layer.type() != QgsMapLayer.VectorLayer):
        return
    iface.mapCanvas().stopRendering()
    layer.setSubsetString(expression)
    layer.updateExtents()
    iface.legendInterface().refreshLayerSymbology(layer)

def applyFilterRequest(layer, request):
    applyFilter(request.filterExpression().dump())

def applySelection(layer, expression):
    request = QgsFeatureRequest().setFilterExpression(expression)
    applySelectionRequest(layer, request)

def applySelectionRequest(layer, request):
    if (layer is None or not layer.isValid() or layer.type() != QgsMapLayer.VectorLayer):
        return
    fit = layer.getFeatures(request)
    layer.setSelectedFeatures([f.id() for f in fit])

def uniqueValues(layer, fieldName):
    values = layer.uniqueValues(layer.fieldNameIndex(fieldName))
    res = set()
    for val in values:
        if val != NULL:
            res.add(val)
    return res

def updateAttribute(layer, attribute, value, expression=None):
    idx = layer.fieldNameIndex(attribute)
    fit = None
    if expression is None or expression == '':
        fit = layer.getFeatures()
    else:
        fit = layer.getFeatures(QgsFeatureRequest().setFilterExpression(expression))
    for f in fit:
        layer.changeAttributeValue(f.id(), idx, value)

def isValid(layer):
    return (layer is not None and layer.isValid() and layer.type() == QgsMapLayer.VectorLayer)

def isInvalid(layer):
    return not isValid(layer)

def isWritable(layer):
    if isInvalid(layer) or len(layer.vectorJoins()) > 0:
        return False
    if layer.storageType() == 'ESRI Shapefile':
        sourceList = layer.source().split('|')
        shpFile = QFileInfo(sourceList[0])
        baseFilePath = shpFile.canonicalPath() + '/' + shpFile.completeBaseName()
        shxFile = QFileInfo(baseFilePath + '.shx')
        dbfFile = QFileInfo(baseFilePath + '.dbf')
        return (shpFile.exists() and shpFile.isWritable()
                and shxFile.exists() and shxFile.isWritable()
                and dbfFile.exists() and dbfFile.isWritable())
    return True

def addHighlight(canvas, featureOrGeometry, layer, color=None, buff=None, minWidth=None):
    # TODO Open bug report for QgsHighlight sip not having QgsFeature constructor.
    if type(featureOrGeometry) == QgsFeature:
        featureOrGeometry = featureOrGeometry.geometry()
    hl = QgsHighlight(canvas, featureOrGeometry, layer)
    lineColor = None
    fillColor = None
    if color is None:
        lineColor = Project.highlightLineColor()
        fillColor = Project.highlightFillColor()
    else:
        lineColor = QColor(color.name())
        fillColor = color
    if buff is None:
        buff = Project.highlightBuffer()
    if minWidth is None:
        minWidth = Project.highlightMinimumWidth()
    hl.setColor(lineColor)
    hl.setFillColor(fillColor)
    hl.setBuffer(buff)
    hl.setMinWidth(minWidth)
    return hl
