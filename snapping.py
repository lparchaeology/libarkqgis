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

from qgis.core import QGis, QgsTolerance, QgsProject, QgsSnapper, QgsMapLayer, QgsMessageLog
from qgis.gui import QgsMessageBar

import resources_rc

# Project setting utilities

def projectSnappingMode(defaultValue='current_layer'):
    res = QgsProject.instance().readEntry("Digitizing", "/SnappingMode", defaultValue);
    if res is not None and res[1]:
        return res[0]
    else:
        return defaultValue

def setProjectSnappingMode(mode='current_layer'):
    return QgsProject.instance().writeEntry("Digitizing", "/SnappingMode", mode);


def defaultSnapperType():
    defaultSnappingTypeString = defaultSnappingType()
    if (defaultSnappingTypeString == "to vertex and segment" or defaultSnappingTypeString == "to_vertex_and_segment"):
        return QgsSnapper.SnapToVertexAndSegment
    elif (defaultSnappingTypeString == 'to segment' or defaultSnappingTypeString == 'to_segment'):
        return QgsSnapper.SnapToSegment
    return QgsSnapper.SnapToVertex

def defaultSnappingType(defaultValue='off'):
    mode = QSettings().value('/qgis/digitizing/default_snap_mode', defaultValue, str)
    if mode is None or mode == '':
        mode = defaultValue
    return mode

def projectSnappingType(defaultValue='off'):
    defaultValue = defaultSnappingType(defaultValue)
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

def setProjectSnappingType(snapType='off'):
    return QgsProject.instance().writeEntry("Digitizing", "/DefaultSnapType", snapType);


def defaultSnappingUnit(defaultValue=QgsTolerance.ProjectUnits):
    unit = QSettings().value('/qgis/digitizing/default_snapping_tolerance_unit', defaultValue, int)
    # Huh???
    if unit is None:
        unit = defaultValue
    return unit

def projectSnappingUnit(defaultValue=QgsTolerance.ProjectUnits):
    defaultValue = defaultSnappingUnit(defaultValue)
    res = QgsProject.instance().readNumEntry("Digitizing", "/DefaultSnapToleranceUnit", defaultValue);
    if res is not None and res[1]:
        return res[0]
    else:
        return defaultValue

def setProjectSnappingUnit(unit=QgsTolerance.ProjectUnits):
    return QgsProject.instance().writeEntry("Digitizing", "/DefaultSnapToleranceUnit", unit);


def defaultSnappingTolerance(defaultValue=0.0):
    tolerance = QSettings().value('/qgis/digitizing/default_snapping_tolerance', defaultValue, float)
    # Huh???
    if tolerance is None:
        tolerance = defaultValue
    return tolerance

def projectSnappingTolerance(defaultValue=0.0):
    defaultValue = defaultSnappingTolerance(defaultValue)
    res = QgsProject.instance().readDoubleEntry("Digitizing", "/DefaultSnapTolerance", defaultValue);
    if res is not None and res[1]:
        return res[0]
    else:
        return defaultValue

def setProjectSnappingTolerance(tolerance=0.0):
    return QgsProject.instance().writeEntry("Digitizing", "/DefaultSnapTolerance", tolerance);


def topologicalEditing(defaultValue=True):
    value = 0
    if defaultValue:
        value = 1
    res = QgsProject.instance().readNumEntry("Digitizing", "/TopologicalEditing", value);
    if res is not None and res[1]:
        return res[0] > 0
    else:
        return defaultValue > 0


def intersectionSnapping(defaultValue=True):
    value = 0
    if defaultValue:
        value = 1
    res = QgsProject.instance().readNumEntry("Digitizing", "/IntersectionSnapping", value);
    if res is not None and res[1]:
        return res[0] > 0
    else:
        return defaultValue > 0

def setIntersectionSnapping(enabled=True):
    value = 0
    if enabled:
        value = 1
    return QgsProject.instance().writeEntry("Digitizing", "/IntersectionSnapping", value);


def intersectionLayers(defaultValue=[]):
    res = QgsProject.instance().readListEntry("Digitizing", "/AvoidIntersectionsList", defaultValue);
    if res is not None and res[1]:
        return res[0]
    else:
        return defaultValue


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
        self._icon = QIcon(':/plugins/Ark/draw-bezier-curves.png')
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
        self._icon = QIcon(':/plugins/Ark/snap-intersection.png')
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
        setIntersectionSnapping(status)

    def _refresh(self):
        self.setChecked(intersectionSnapping())


# Snapping Widgets

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
            setProjectSnappingType('off')
            setProjectSnappingMode('current_layer')
        else:
            if self._snapMode == 'off' and mode != 'off':
                setProjectSnappingType(self._snapType)
            setProjectSnappingMode(mode)
        self._snapMode = mode
        self.snappingModeChanged.emit(mode)

    def _refresh(self):
        mode = projectSnappingMode()
        if self._snapMode == 'off' and mode == 'current_layer':
            return
        self._snapType = projectSnappingType()
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
        setProjectSnappingType(snapType)
        self.snappingTypeChanged.emit(snapType)

    def _refresh(self):
        snapType = projectSnappingType()
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
        setProjectSnappingUnit(snapUnit)
        self.snappingUnitChanged.emit(snapUnit)

    def _refresh(self):
        snapUnit = projectSnappingUnit()
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
        setProjectSnappingTolerance(self.value())
        self.snappingToleranceChanged.emit(self.value())

    def _refresh(self):
        self.setValue(projectSnappingTolerance())
        unit = projectSnappingUnit()
        if (unit == QgsTolerance.Pixels):
            self.setSuffix(' px')
        elif self._iface == None:
            self.setSuffix('')
        elif unit == QgsTolerance.LayerUnits: # == MapUnits
            layerUnits = None
            mode = projectSnappingMode()
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

        self._vertexIcon = QIcon(':/plugins/Ark/iconSnapVertex.png')
        self._vertexAction = QAction(self._vertexIcon, 'Vertex', self)
        self._vertexAction.setStatusTip('Snap to vertex')
        self._vertexAction.setCheckable(True)

        self._segmentIcon = QIcon(':/plugins/Ark/iconSnapSegment.png')
        self._segmentAction = QAction(self._segmentIcon, 'Segment', self)
        self._segmentAction.setStatusTip('Snap to segment')
        self._segmentAction.setCheckable(True)

        self._vertexSegmentIcon = QIcon(':/plugins/Ark/iconSnapVertexSegment.png')
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
            self.setEnabled(False)
            self._snapEnabled = False
            self._refreshButton()
        elif (layer.isValid() and layer.type() == QgsMapLayer.VectorLayer):
            self._layer = layer
            self.setEnabled(True)
            self._avoidAction.setEnabled(layer.geometryType() == QGis.Polygon)
            self.updateButton()

    def updateButton(self):
        """Updates the button with the current snapping settings."""
        if (self._layer is None):
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

        self.setChecked(self._snapEnabled)

        if (self._snappingType == QgsSnapper.SnapToVertex):
            self.setIcon(self._vertexIcon)
            self._vertexAction.setChecked(True)
        elif (self._snappingType == QgsSnapper.SnapToSegment):
            self.setIcon(self._segmentIcon)
            self._segmentAction.setChecked(True)
        elif (self._snappingType == QgsSnapper.SnapToVertexAndSegment):
            self.setIcon(self._vertexSegmentIcon)
            self._vertexSegmentAction.setChecked(True)

        if (self._unitType == QgsTolerance.Pixels):
            self._pixelUnitsAction.setChecked(True)
            self._toleranceSpin.setSuffix(' px')
        else:
            self._layerUnitsAction.setChecked(True)
            layerUnits = self._layer.crs().mapUnits()
            suffix = _unitToSuffix(layerUnits)
            self._toleranceSpin.setSuffix(suffix)

        self._toleranceSpin.setValue(self._tolerance)

        self._avoidAction.setChecked(self._avoidIntersections)

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
