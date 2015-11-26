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

"""
Widgets to use to configure QGIS project snapping settings

This module provides a set of widgets to allow easy configuration of QGIS vector layer snapping.

SnappingToolButton: A button to configure snapping options for a given layer.
TopoEditToolButton: A button to configure topological editing for a project.
"""

from PyQt4.QtCore import Qt, pyqtSignal, QSettings
from PyQt4.QtGui import QToolButton, QMenu, QIcon, QAction, QActionGroup, QWidgetAction, QDoubleSpinBox, QComboBox

from qgis.core import QGis, QgsTolerance, QgsProject, QgsSnapper, QgsMapLayer, QgsMessageLog, QgsMapLayerRegistry
from qgis.gui import QgsMessageBar

import resources_rc

# Project setting utilities

class Snapping():

    # SnappingMode
    CurrentLayer = 0
    AllLayers = 1
    SelectedLayers = 2

    # SnappingType
    Vertex = 0
    Segment = 1
    VertexAndSegment = 2

    @staticmethod
    def projectSnappingMode(defaultValue='current_layer'):
        res = QgsProject.instance().readEntry("Digitizing", "/SnappingMode", defaultValue);
        if res is not None and res[1]:
            return res[0]
        else:
            return defaultValue

    @staticmethod
    def setProjectSnappingMode(mode='current_layer'):
        return QgsProject.instance().writeEntry("Digitizing", "/SnappingMode", mode);

    @staticmethod
    def defaultSnapperType():
        defaultSnappingTypeString = Snapping.defaultSnappingType()
        if (defaultSnappingTypeString == "to vertex and segment" or defaultSnappingTypeString == "to_vertex_and_segment"):
            return QgsSnapper.SnapToVertexAndSegment
        elif (defaultSnappingTypeString == 'to segment' or defaultSnappingTypeString == 'to_segment'):
            return QgsSnapper.SnapToSegment
        return QgsSnapper.SnapToVertex

    @staticmethod
    def defaultSnappingType(defaultValue='off'):
        mode = QSettings().value('/qgis/digitizing/default_snap_mode', defaultValue, str)
        if mode is None or mode == '':
            mode = defaultValue
        return mode

    @staticmethod
    def projectSnappingType(defaultValue='off'):
        defaultValue = Snapping.defaultSnappingType(defaultValue)
        if defaultValue == 'to vertex':
            defaultValue = 'to_vertex'
        elif defaultValue == 'to segment':
            defaultValue = 'to_segment'
        elif defaultValue == 'to vertex and segment':
            defaultValue = 'to_vertex_and_segment'
        res = QgsProject.instance().readEntry("Digitizing", "/DefaultSnapType", defaultValue);
        if res is not None and res[1]:
            return res[0]
        else:
            return defaultValue

    @staticmethod
    def setProjectSnappingType(snapType='off'):
        return QgsProject.instance().writeEntry("Digitizing", "/DefaultSnapType", snapType);

    @staticmethod
    def defaultSnappingUnit(defaultValue=QgsTolerance.ProjectUnits):
        unit = QSettings().value('/qgis/digitizing/default_snapping_tolerance_unit', defaultValue, int)
        # Huh???
        if unit is None:
            unit = defaultValue
        return unit

    @staticmethod
    def projectSnappingUnit(defaultValue=QgsTolerance.ProjectUnits):
        defaultValue = Snapping.defaultSnappingUnit(defaultValue)
        res = QgsProject.instance().readNumEntry("Digitizing", "/DefaultSnapToleranceUnit", defaultValue);
        if res is not None and res[1]:
            return res[0]
        else:
            return defaultValue

    @staticmethod
    def setProjectSnappingUnit(unit=QgsTolerance.ProjectUnits):
        return QgsProject.instance().writeEntry("Digitizing", "/DefaultSnapToleranceUnit", unit);


    @staticmethod
    def defaultSnappingTolerance(defaultValue=0.0):
        tolerance = QSettings().value('/qgis/digitizing/default_snapping_tolerance', defaultValue, float)
        # Huh???
        if tolerance is None:
            tolerance = defaultValue
        return tolerance

    @staticmethod
    def projectSnappingTolerance(defaultValue=0.0):
        defaultValue = Snapping.defaultSnappingTolerance(defaultValue)
        res = QgsProject.instance().readDoubleEntry("Digitizing", "/DefaultSnapTolerance", defaultValue);
        if res is not None and res[1]:
            return res[0]
        else:
            return defaultValue

    @staticmethod
    def setProjectSnappingTolerance(tolerance=0.0):
        return QgsProject.instance().writeEntry("Digitizing", "/DefaultSnapTolerance", tolerance);

    @staticmethod
    def topologicalEditing(defaultValue=True):
        value = 0
        if defaultValue:
            value = 1
        res = QgsProject.instance().readNumEntry("Digitizing", "/TopologicalEditing", value);
        if res is not None and res[1]:
            return res[0] > 0
        else:
            return defaultValue > 0

    @staticmethod
    def intersectionSnapping(defaultValue=True):
        value = 0
        if defaultValue:
            value = 1
        res = QgsProject.instance().readNumEntry("Digitizing", "/IntersectionSnapping", value);
        if res is not None and res[1]:
            return res[0] > 0
        else:
            return defaultValue > 0

    @staticmethod
    def setIntersectionSnapping(enabled=True):
        value = 0
        if enabled:
            value = 1
        return QgsProject.instance().writeEntry("Digitizing", "/IntersectionSnapping", value);

    @staticmethod
    def intersectionLayers(defaultValue=[]):
        res = QgsProject.instance().readListEntry("Digitizing", "/AvoidIntersectionsList", defaultValue);
        if res is not None and res[1]:
            return res[0]
        else:
            return defaultValue

    @staticmethod
    def layerSnappingEnabled(layerId):
        layerIdList, ok = QgsProject.instance().readListEntry("Digitizing", "/LayerSnappingList")
        enabledList, ok = QgsProject.instance().readListEntry("Digitizing", "/LayerSnappingEnabledList")
        try:
            idx = layerIdList.index(layerId)
            return enabledList[idx] == 'enabled'
        except:
            pass
        return False

    @staticmethod
    def setLayerSnappingEnabled(layerId, enabled):
        layerIdList, ok = QgsProject.instance().readListEntry("Digitizing", "/LayerSnappingList")
        enabledList, ok = QgsProject.instance().readListEntry("Digitizing", "/LayerSnappingEnabledList")
        try:
            idx = layerIdList.index(layerId)
            if enabled:
                enabledList[idx] = 'enabled'
            else:
                enabledList[idx] = 'disabled'
            QgsProject.instance().writeEntry("Digitizing", "/LayerSnappingEnabledList", enabledList)
        except:
            pass

    @staticmethod
    def layerSnappingEnabledLayers():
        enabledLayers = []
        layerIdList, ok = QgsProject.instance().readListEntry("Digitizing", "/LayerSnappingList")
        enabledList, ok = QgsProject.instance().readListEntry("Digitizing", "/LayerSnappingEnabledList")
        for idx in range(0, len(layerIdList)):
            if enabledList[idx] == 'enabled':
                enabledLayers.append(layerIdList[idx])
        return enabledLayers

    @staticmethod
    def setLayerSnappingEnabledLayers(enabledLayers):
        enabledList = []
        layerIdList, ok = QgsProject.instance().readListEntry("Digitizing", "/LayerSnappingList")
        for layerId in layerIdList:
            if layerId in enabledLayers:
                enabledList.append('enabled')
            else:
                enabledList.append('disabled')
        QgsProject.instance().writeEntry("Digitizing", "/LayerSnappingEnabledList", enabledList)


# Snapping Actions

class TopologicalEditingAction(QAction):

    """QAction to toggle Topological Editing for a project
    """

    def __init__(self, parent=None):
        """Initialises the Topological Editing Action

        Args:
            parent (QWidget): The parent widget, defaults to None.
        """

        super(TopologicalEditingAction, self).__init__(parent)

        self.setCheckable(True)
        self._icon = QIcon(':/plugins/Ark/topologicalEditing.png')
        self.setIcon(self._icon)
        self.setText('Topological Editing')

        self._project = QgsProject.instance()

        self._refresh()
        self.toggled.connect(self._toggled)

        # Make sure we catch changes in the main snapping dialog
        self._project.snapSettingsChanged.connect(self._refresh)
        # If a new _project is read, update to that _project's setting
        self._project.readProject.connect(self._refresh)

    # Private API

    def _toggled(self, status):
        self._project.setTopologicalEditing(status)

    def _refresh(self):
        self.setChecked(self._project.topologicalEditing())


class IntersectionSnappingAction(QAction):

    """QAction to toggle Intersection Snapping for a project
    """

    def __init__(self, parent=None):
        """Initialises the Intersection Snapping Action

        Args:
            parent (QWidget): The parent widget, defaults to None.
        """

        super(IntersectionSnappingAction, self).__init__(parent)

        self.setCheckable(True)
        self._icon = QIcon(':/plugins/Ark/snapIntersections.png')
        self.setIcon(self._icon)
        self.setText('Intersection Snapping')

        self._project = QgsProject.instance()

        self._refresh()
        self.toggled.connect(self._toggled)

        # Make sure we catch changes in the main snapping dialog
        self._project.snapSettingsChanged.connect(self._refresh)
        # If a new _project is read, update to that _project's setting
        self._project.readProject.connect(self._refresh)

    # Private API

    def _toggled(self, status):
        Snapping.setIntersectionSnapping(status)

    def _refresh(self):
        self.setChecked(Snapping.intersectionSnapping())


# Snapping Widgets

class SnappingModeTool(QToolButton):

    """Tool button to change snapping mode

    Signals:
            snapSettingsChanged(): Signal that the snapping settings has been changed by the button
    """

    snapSettingsChanged = pyqtSignal()

    _project = None # QgsProject()
    _selectedLayers = []
    _prevType = 'off'
    _ignoreRefresh = False

    def __init__(self, parent=None):
        """
        Initialises the snapping mode button

        Args:
            parent (QWidget): The parent widget, defaults to None.
        """

        super(SnappingModeTool, self).__init__(parent)
        self.setCheckable(True)
        self.setPopupMode(QToolButton.MenuButtonPopup)

        self._project = QgsProject.instance()

        self._currentIcon = QIcon(':/plugins/Ark/snapLayerCurrent.png')
        self._currentAction = QAction(self._currentIcon, 'Current Layer', self)
        self._currentAction.setStatusTip('Snap to current layer')
        self._currentAction.setCheckable(True)

        self._allIcon = QIcon(':/plugins/Ark/snapLayerAll.png')
        self._allAction = QAction(self._allIcon, 'All Layers', self)
        self._allAction.setStatusTip('Snap to all layers')
        self._allAction.setCheckable(True)

        self._selectedIcon = QIcon(':/plugins/Ark/snapLayerSelected.png')
        self._selectedAction = QAction(self._selectedIcon, 'Selected Layers', self)
        self._selectedAction.setStatusTip('Snap to selected layers')
        self._selectedAction.setCheckable(True)

        self._snappingModeActionGroup = QActionGroup(self)
        self._snappingModeActionGroup.addAction(self._currentAction)
        self._snappingModeActionGroup.addAction(self._allAction)
        self._snappingModeActionGroup.addAction(self._selectedAction)

        self._menu = QMenu(self)
        self._menu.addActions(self._snappingModeActionGroup.actions())
        self.setMenu(self._menu)

        self._refresh()

        self.toggled.connect(self._snappingToggled)
        self._currentAction.triggered.connect(self._snapCurrentLayer)
        self._allAction.triggered.connect(self._snapAllLayers)
        self._selectedAction.triggered.connect(self._snapSelectedLayers)

        # Make sure we catch changes in the main snapping dialog
        self._project.snapSettingsChanged.connect(self._refresh)
        # If a new _project is read, update to that _project's setting
        self._project.readProject.connect(self._refresh)
        self.snapSettingsChanged.connect(self._project.snapSettingsChanged)

    # Private API

    def _snappingToggled(self, checked):
        if checked:
            if Snapping.projectSnappingMode() == 'advanced':
                Snapping.setLayerSnappingEnabledLayers(self._selectedLayers)
            else:
                Snapping.setProjectSnappingType(self._prevType)
        else:
            if Snapping.projectSnappingMode() == 'advanced':
                self._selectedLayers = Snapping.layerSnappingEnabledLayers()
                Snapping.setLayerSnappingEnabledLayers([])
            else:
                self._prevType = Snapping.projectSnappingType()
                Snapping.setProjectSnappingType('off')
        self._ignoreRefresh = True
        self.snapSettingsChanged.emit()

    def _snapCurrentLayer(self):
        Snapping.setProjectSnappingMode('current_layer')
        self._ignoreRefresh = True
        self.snapSettingsChanged.emit()

    def _snapAllLayers(self):
        Snapping.setProjectSnappingMode('all_layers')
        self._ignoreRefresh = True
        self.snapSettingsChanged.emit()

    def _snapSelectedLayers(self):
        Snapping.setProjectSnappingMode('advanced')
        self._ignoreRefresh = True
        self.snapSettingsChanged.emit()

    def _refresh(self):
        if self._ignoreRefresh:
            self._ignoreRefresh = False
            return
        self.blockSignals(True)
        snapMode = Snapping.projectSnappingMode()
        snapType = Snapping.projectSnappingType()
        if snapType != 'off':
            self._prevType = snapType
        self._selectedLayers = Snapping.layerSnappingEnabledLayers()
        if snapMode == 'advanced':
            enabled = (len(self._selectedLayers) > 0)
            self.setChecked(enabled)
            self._setActiveAction(self._selectedAction)
        else:
            self.setChecked(snapType != 'off')
            if snapMode == 'current_layer':
                self._setActiveAction(self._currentAction)
            elif snapMode == 'all_layers':
                self._setActiveAction(self._allAction)
        self.blockSignals(False)

    def _setActiveAction(self, action):
        action.setChecked(True)
        self.setIcon(action.icon())


class SnappingModeCombo(QComboBox):

    snappingModeChanged = pyqtSignal(str)

    _project = QgsProject.instance()
    _snapMode = ''
    _snapType = ''

    def __init__(self, parent=None):

        super(SnappingModeCombo, self).__init__(parent)

        self.addItem('Off', 'off')
        self.addItem('Current Layer', 'current_layer')
        self.addItem('All Layers', 'all_layers')
        self.addItem('Selected Layers', 'advanced')
        self.setCurrentIndex(0)

        self._refresh()
        self.currentIndexChanged.connect(self._changed)

        # Make sure we catch changes in the main snapping dialog
        self._project.snapSettingsChanged.connect(self._refresh)
        # If a new _project is read, update to that _project's setting
        self._project.readProject.connect(self._refresh)
        self.snappingModeChanged.connect(self._project.snapSettingsChanged)

    def currentMode(self):
        return self.itemData(self.currentIndex())

    # Private API

    def _changed(self, idx):
        mode = self.currentMode()
        if mode == 'off':
            Snapping.setProjectSnappingType('off')
            Snapping.setProjectSnappingMode('current_layer')
        else:
            if self._snapMode == 'off' and mode != 'off':
                Snapping.setProjectSnappingType(self._snapType)
            Snapping.setProjectSnappingMode(mode)
        self._snapMode = mode
        self.snappingModeChanged.emit(mode)

    def _refresh(self):
        mode = Snapping.projectSnappingMode()
        if self._snapMode == 'off' and mode == 'current_layer':
            return
        self._snapType = Snapping.projectSnappingType()
        self._snapMode = mode
        idx = self.findData(self._snapMode)
        self.setCurrentIndex(idx)


class SnappingTypeCombo(QComboBox):

    snappingTypeChanged = pyqtSignal(str)

    _project = QgsProject.instance()

    def __init__(self, parent=None):

        super(SnappingTypeCombo, self).__init__(parent)

        self.addItem('Off', 'off')
        self.addItem('Vertex', 'to_vertex')
        self.addItem('Segment', 'to_segment')
        self.addItem('Vertex and Segment', 'to_vertex_and_segment')
        self.setCurrentIndex(0)

        self._refresh()
        self.currentIndexChanged.connect(self._changed)

        # Make sure we catch changes in the main snapping dialog
        self._project.snapSettingsChanged.connect(self._refresh)
        # If a new _project is read, update to that _project's setting
        self._project.readProject.connect(self._refresh)
        self.snappingTypeChanged.connect(self._project.snapSettingsChanged)

    # Private API

    def _changed(self, idx):
        snapType = self.itemData(self.currentIndex())
        Snapping.setProjectSnappingType(snapType)
        self.snappingTypeChanged.emit(snapType)

    def _refresh(self):
        snapType = Snapping.projectSnappingType()
        idx = self.findData(snapType)
        self.setCurrentIndex(idx)


class SnappingUnitCombo(QComboBox):

    snappingUnitChanged = pyqtSignal(int)

    _project = QgsProject.instance()

    def __init__(self, parent=None):

        super(SnappingUnitCombo, self).__init__(parent)

        self.addItem('Pixels', QgsTolerance.Pixels)
        self.addItem('Layer Units', QgsTolerance.LayerUnits)
        self.addItem('Project Units', QgsTolerance.ProjectUnits)
        self.setCurrentIndex(0)

        self._refresh()
        self.currentIndexChanged.connect(self._changed)

        # Make sure we catch changes in the main snapping dialog
        self._project.snapSettingsChanged.connect(self._refresh)
        # If a new _project is read, update to that _project's setting
        self._project.readProject.connect(self._refresh)
        self.snappingUnitChanged.connect(self._project.snapSettingsChanged)

    # Private API

    def _changed(self, idx):
        snapUnit = self.itemData(self.currentIndex())
        Snapping.setProjectSnappingUnit(snapUnit)
        self.snappingUnitChanged.emit(snapUnit)

    def _refresh(self):
        snapUnit = Snapping.projectSnappingUnit()
        idx = self.findData(snapUnit)
        self.setCurrentIndex(idx)


class SnappingToleranceSpinBox(QDoubleSpinBox):

    snappingToleranceChanged = pyqtSignal(float)

    _iface = None
    _project = QgsProject.instance()

    def __init__(self, parent=None):

        super(SnappingToleranceSpinBox, self).__init__(parent)

        self.setDecimals(5)
        self.setRange(0.0, 100000000.0)

        self._refresh()
        self.valueChanged.connect(self._changed)

        # Make sure we catch changes in the main snapping dialog
        self._project.snapSettingsChanged.connect(self._refresh)
        # If a new _project is read, update to that _project's setting
        self._project.readProject.connect(self._refresh)
        self.snappingToleranceChanged.connect(self._project.snapSettingsChanged)

    def setIface(self, iface):
        self._iface = iface
        self._refresh()

    # Private API

    def _changed(self, idx):
        Snapping.setProjectSnappingTolerance(self.value())
        self.snappingToleranceChanged.emit(self.value())

    def _refresh(self):
        self.setValue(Snapping.projectSnappingTolerance())
        unit = Snapping.projectSnappingUnit()
        if (unit == QgsTolerance.Pixels):
            self.setSuffix(' px')
        elif self._iface == None:
            self.setSuffix('')
        elif unit == QgsTolerance.LayerUnits: # == MapUnits
            layerUnits = None
            mode = Snapping.projectSnappingMode()
            if mode == 'current_layer':
                layerUnits = self._iface.mapCanvas().currentLayer().crs().mapUnits()
            else:
                # TODO Find out the correct option here for all_layers!
                layerUnits = self._iface.mapCanvas().mapUnits()
            suffix = _unitToSuffix(layerUnits)
            self.setSuffix(suffix)
        elif unit == QgsTolerance.ProjectUnits:
            projectUnits = self._iface.mapCanvas().mapUnits()
            suffix = _unitToSuffix(projectUnits)
            self.setSuffix(suffix)

def _unitToSuffix(unit):
    if unit == QGis.Meters:
        return ' m'
    elif unit == QGis.Feet:
        return ' ft'
    elif unit == QGis.NauticalMiles:
        return ' NM'
    else:
        return ' °'


class SnappingToolButton(QToolButton):

    """Tool button to change snapping settings for a QGIS vector layer

    Signals:
        snapSettingsChanged(str, bool, str, QgsSnapper.SnappingType, QgsTolerance.UnitType, float, bool): Signal that the layer's snap settings have been changed by the button
    """

    snapSettingsChanged = pyqtSignal(str, bool, QgsSnapper.SnappingType, QgsTolerance.UnitType, float, bool)

    _layer = None
    _layerId = ''
    _snapEnabled = False
    _snappingType = QgsSnapper.SnapToVertex
    _unitType = QgsTolerance.Pixels
    _tolerance = 10.0
    _avoidIntersections = False

    def __init__(self, parent=None):
        """Initialises the snapping tool button

        After creating the button, you must call setLayer().

        Args:
            parent (QWidget): The parent widget, defaults to None.
        """

        QToolButton.__init__(self, parent)

        self._project = QgsProject.instance()

        #Disable until we have a _layerId
        self.setEnabled(False)

        self._vertexIcon = QIcon(':/plugins/Ark/snapVertex.png')
        self._vertexAction = QAction(self._vertexIcon, 'Vertex', self)
        self._vertexAction.setStatusTip('Snap to vertex')
        self._vertexAction.setCheckable(True)

        self._segmentIcon = QIcon(':/plugins/Ark/snapSegment.png')
        self._segmentAction = QAction(self._segmentIcon, 'Segment', self)
        self._segmentAction.setStatusTip('Snap to segment')
        self._segmentAction.setCheckable(True)

        self._vertexSegmentIcon = QIcon(':/plugins/Ark/snapVertexSegment.png')
        self._vertexSegmentAction = QAction(self._vertexSegmentIcon, 'Vertex and Segment', self)
        self._vertexSegmentAction.setStatusTip('Snap to vertex and segment')
        self._vertexSegmentAction.setCheckable(True)

        self._snappingTypeActionGroup = QActionGroup(self)
        self._snappingTypeActionGroup.addAction(self._vertexAction)
        self._snappingTypeActionGroup.addAction(self._segmentAction)
        self._snappingTypeActionGroup.addAction(self._vertexSegmentAction)

        self._pixelUnitsAction = QAction('Pixels', self)
        self._pixelUnitsAction.setStatusTip('Use Pixels')
        self._pixelUnitsAction.setCheckable(True)

        self._layerUnitsAction = QAction('Layer Units', self)
        self._layerUnitsAction.setStatusTip('Use Layer Units')
        self._layerUnitsAction.setCheckable(True)

        self._unitTypeActionGroup = QActionGroup(self)
        self._unitTypeActionGroup.addAction(self._pixelUnitsAction)
        self._unitTypeActionGroup.addAction(self._layerUnitsAction)

        self._avoidAction = QAction('Snap overlapping edges', self)
        self._avoidAction.setStatusTip('Snap to edges of any overlapping polygons, aka "Avoid Intersections"')
        self._avoidAction.setCheckable(True)

        self._toleranceSpin = QDoubleSpinBox(self)
        self._toleranceSpin.setDecimals(5)
        self._toleranceSpin.setRange(0.0, 100000000.0)
        self._toleranceAction = QWidgetAction(self)
        self._toleranceAction.setDefaultWidget(self._toleranceSpin)
        self._toleranceAction.setStatusTip('Set the snapping tolerance')

        self._menu = QMenu(self)
        self._menu.addActions(self._snappingTypeActionGroup.actions())
        self._menu.addSeparator()
        self._menu.addActions(self._unitTypeActionGroup.actions())
        self._menu.addAction(self._toleranceAction)
        self._menu.addSeparator()
        self._menu.addAction(self._avoidAction)
        self.setMenu(self._menu)

        self.toggled.connect(self._snapToggled)
        self._vertexAction.triggered.connect(self._snapToVertex)
        self._segmentAction.triggered.connect(self._snapToSegment)
        self._vertexSegmentAction.triggered.connect(self._snapToVertexSegment)
        self._pixelUnitsAction.triggered.connect(self._usePixelUnits)
        self._layerUnitsAction.triggered.connect(self._useLayerUnits)
        self._toleranceSpin.valueChanged.connect(self._toleranceChanged)
        self._avoidAction.toggled.connect(self._avoidToggled)

        # Make sure we catch changes in the main snapping dialog
        # TODO This responds to all updates, make it only respond to our layer changing
        self._project.snapSettingsChanged.connect(self.updateButton)
        # If a new _project is read then layer is no longer valid
        self._project.readProject.connect(self.disableButton)
        QgsMapLayerRegistry.instance().layerRemoved.connect(self._layerRemoved)

    # Public API

    def layer(self):
        """Returns the ID of the layer the button applies to"""
        return self._layer

    def setLayer(self, layer):
        """Sets the layer the button applies to

        Args:
            layer (QgsVectorLayer): Vector layer the button is to apply to.
        """
        if (layer is None):
            self._layer = None
            self._layerId = ''
            self.setEnabled(False)
            self._snapEnabled = False
            self._refreshButton()
        elif (layer.isValid() and layer.type() == QgsMapLayer.VectorLayer):
            self._layer = layer
            self._layerId = layer.id()
            self.setEnabled(True)
            self._avoidAction.setEnabled(layer.geometryType() == QGis.Polygon)
            self.updateButton()

    def _layerRemoved(self, layerId):
        if layerId == self._layerId:
            self.disableButton()

    def updateButton(self):
        """Updates the button with the current snapping settings."""
        if (self._layer is None or not self._layer.isValid()):
            return
        ok, self._snapEnabled, self._snappingType, self._unitType, self._tolerance, self._avoidIntersections = self._project.snapSettingsForLayer(self._layer.id())
        self._refreshButton()

    def disableButton(self):
        """Disables the button and unlinks from the layer."""
        self.setLayer(None)

    # Private API

    def _updateSnapSettings(self):
        if (self._layer is None):
            return
        self._project.setSnapSettingsForLayer(self._layer.id(), self._snapEnabled, self._snappingType, self._unitType, self._tolerance, self._avoidIntersections)
        self._refreshButton()
        self.snapSettingsChanged.emit(self._layer.id(), self._snapEnabled, self._snappingType, self._unitType, self._tolerance, self._avoidIntersections)

    def _refreshButton(self):

        self.blockSignals(True)
        self.setChecked(self._snapEnabled)

        if (self._snappingType == QgsSnapper.SnapToSegment):
            self.setIcon(self._segmentIcon)
            self._segmentAction.setChecked(True)
        elif (self._snappingType == QgsSnapper.SnapToVertexAndSegment):
            self.setIcon(self._vertexSegmentIcon)
            self._vertexSegmentAction.setChecked(True)
        else: # QgsSnapper.SnapToVertex or undefined
            self.setIcon(self._vertexIcon)
            self._vertexAction.setChecked(True)

        if (self._unitType == QgsTolerance.Pixels):
            self._pixelUnitsAction.setChecked(True)
            self._toleranceSpin.setSuffix(' px')
        else:
            self._layerUnitsAction.setChecked(True)
            layerUnits = QGis.Meters
            if self._layer is not None:
                layerUnits = self._layer.crs().mapUnits()
            suffix = _unitToSuffix(layerUnits)
            self._toleranceSpin.setSuffix(suffix)

        self._toleranceSpin.setValue(self._tolerance)

        self._avoidAction.setChecked(self._avoidIntersections)
        self.blockSignals(False)

    def _snapToggled(self, _snapEnabled):
        self._snapEnabled = bool(_snapEnabled)
        self._updateSnapSettings()

    def _snapToVertex(self):
        self._snappingType = QgsSnapper.SnapToVertex
        self._updateSnapSettings()

    def _snapToSegment(self):
        self._snappingType = QgsSnapper.SnapToSegment
        self._updateSnapSettings()

    def _snapToVertexSegment(self):
        self._snappingType = QgsSnapper.SnapToVertexAndSegment
        self._updateSnapSettings()

    def _usePixelUnits(self):
        self._unitType = QgsTolerance.Pixels
        self._updateSnapSettings()

    def _useLayerUnits(self):
        self._unitType = QgsTolerance.LayerUnits
        self._updateSnapSettings()

    def _toleranceChanged(self, _tolerance):
        self._tolerance = _tolerance
        self._updateSnapSettings()

    def _avoidToggled(self, status):
        self._avoidIntersections = status
        self._updateSnapSettings()
