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

"""
Widgets to use to configure QGIS project snapping settings

This module provides a set of widgets to allow easy configuration of QGIS vector layer snapping.

SnappingToolButton: A button to configure snapping options for a given layer.
TopoEditToolButton: A button to configure topological editing for a project.
"""

from PyQt4.QtCore import Qt, pyqtSignal, QSettings
from PyQt4.QtGui import QToolButton, QMenu, QIcon, QAction, QActionGroup, QWidgetAction, QDoubleSpinBox, QComboBox

from qgis.core import QGis, QgsProject, QgsMapLayer, QgsMessageLog, QgsMapLayerRegistry
from qgis.gui import QgsMessageBar

from project import Project

import resources_rc

# Project setting utilities

class Snapping():

    # SnappingMode
    CurrentLayer = 0
    AllLayers = 1
    SelectedLayers = 2

    # SnappingType == QgsSnapper.SnappingType, plus Off, keep values teh same
    Vertex = 0
    Segment = 1
    VertexAndSegment = 2
    Off = 3

    # SnappingUnits == QgsTolerance.UnitType, keep values the same
    LayerUnits = 0
    Pixels = 1
    ProjectUnits = 2

    # Snapping Mode, i.e. what snapping mode currently applies

    @staticmethod
    def snappingMode():
        mode = Project.readEntry("Digitizing", "/SnappingMode", "current_layer")
        if mode == 'advanced':
            return Snapping.SelectedLayers
        elif mode == 'all_layers':
            return Snapping.AllLayers
        else:
            return Snapping.CurrentLayer

    @staticmethod
    def setSnappingMode(mode):
        if mode == Snapping.SelectedLayers:
            Snapping._setSnappingMode('advanced')
        elif mode == Snapping.AllLayers:
            Snapping._setSnappingMode('all_layers')
        elif mode == Snapping.CurrentLayer:
            Snapping._setSnappingMode('current_layer')

    @staticmethod
    def _setSnappingMode(mode='current_layer'):
        return Project.writeEntry("Digitizing", "/SnappingMode", mode);

    # Default Snapping Type, i.e. the system-wdie default

    @staticmethod
    def defaultSnappingType(defaultValue=Off):
        defaultValue = Snapping._toDefaultSnapType(defaultValue)
        value = QSettings().value('/qgis/digitizing/default_snap_mode', defaultValue , str)
        return Snapping._fromDefaultSnapType(value)

    @staticmethod
    def setDefaultSnappingType(snapType=Off):
        snapType = Snapping._toDefaultSnapType(snapType)
        return QSettings().setValue('/qgis/digitizing/default_snap_mode', snapType, str)

    @staticmethod
    def _fromDefaultSnapType(val):
        if val == 'off':
            return Snapping.Off
        elif val == 'to vertex':
            return Snapping.Vertex
        elif val == 'to segment':
            return Snapping.Segment
        elif val == 'to vertex and segment':
            return Snapping.VertexAndSegment
        return Snapping.Off

    @staticmethod
    def _toDefaultSnapType(val):
        if val == Snapping.Off or val == 'off':
            return 'off'
        elif val == Snapping.Vertex or val == 'to_vertex':
            return 'to vertex'
        elif val == Snapping.Segment or val == 'to_segment':
            return 'to segment'
        elif val == Snapping.VertexAndSegment or val == 'to_vertex_and_segment':
            return 'to vertex and segment'
        return 'off'

    # Project Snapping Type, i.e. when snapping mode is CurrentLayer or AllLayers

    @staticmethod
    def projectSnappingType(defaultValue=Off):
        defaultValue = Snapping.defaultSnappingType(defaultValue)
        value = Project.readEntry("Digitizing", "/DefaultSnapType", Snapping._toSnapType(defaultValue));
        return Snapping._fromSnapType(value)

    @staticmethod
    def setProjectSnappingType(snapType=Off):
        return Project.writeEntry("Digitizing", "/DefaultSnapType", Snapping._toSnapType(snapType));

    @staticmethod
    def _fromSnapType(value):
        if value == 'off':
            return Snapping.Off
        elif value == 'to_vertex':
            return Snapping.Vertex
        elif value == 'to_segment':
            return Snapping.Segment
        elif value == 'to_vertex_and_segment':
            return Snapping.VertexAndSegment
        return Snapping.Off

    @staticmethod
    def _toSnapType(val):
        if val == Snapping.Off:
            return 'off'
        elif val == Snapping.Vertex:
            return 'to_vertex'
        elif val == Snapping.Segment:
            return 'to_segment'
        elif val == Snapping.VertexAndSegment:
            return 'to_vertex_and_segment'
        return 'off'

    # Default Snapping Unit, i.e. the system-wide default

    @staticmethod
    def defaultSnappingUnit(defaultValue=ProjectUnits):
        unit = QSettings().value('/qgis/digitizing/default_snapping_tolerance_unit', defaultValue, int)
        # FIXME Sometimes None gets returned even though we give a valid default?
        if unit is None:
            unit = defaultValue
        return unit

    def setDefaultSnappingUnit(unit=ProjectUnits):
        return QSettings().setValue('/qgis/digitizing/default_snapping_tolerance_unit', unit, int)

    # Project Snapping Unit, i.e. when snapping mode is CurrentLayer or AllLayers

    @staticmethod
    def projectSnappingUnit(defaultValue=ProjectUnits):
        defaultValue = Snapping.defaultSnappingUnit(defaultValue)
        return Project.readNumEntry("Digitizing", "/DefaultSnapToleranceUnit", defaultValue)

    @staticmethod
    def setProjectSnappingUnit(unit=ProjectUnits):
        return Project.writeEntry("Digitizing", "/DefaultSnapToleranceUnit", unit)

    # Default Snapping Tolerance, i.e. the system-wide default

    @staticmethod
    def defaultSnappingTolerance(defaultValue=0.0):
        tolerance = QSettings().value('/qgis/digitizing/default_snapping_tolerance', defaultValue, float)
        # FIXME Sometimes None gets returned even though we give a valid default?
        if tolerance is None:
            tolerance = defaultValue
        return tolerance

    @staticmethod
    def setDefaultSnappingTolerance(tolerance=0.0):
        return QSettings().setValue('/qgis/digitizing/default_snapping_tolerance', tolerance, float)

    # Project Snapping Tolerance, i.e. when snapping mode is CurrentLayer or AllLayers

    @staticmethod
    def projectSnappingTolerance(defaultValue=0.0):
        defaultValue = Snapping.defaultSnappingTolerance(defaultValue)
        return Project.readDoubleEntry("Digitizing", "/DefaultSnapTolerance", defaultValue)

    @staticmethod
    def setProjectSnappingTolerance(tolerance=0.0):
        return Project.writeEntry("Digitizing", "/DefaultSnapTolerance", tolerance)

    # Topological Editing, i.e. the system-wide setting

    @staticmethod
    def topologicalEditing():
        return QgsProject.instance().topologicalEditing()

    @staticmethod
    def setTopologicalEditing(enabled=True):
        return QgsProject.instance().setTopologicalEditing(enabled)

    # Intersection Snapping, i.e. the system-wide setting

    @staticmethod
    def intersectionSnapping(defaultValue=True):
        res = Project.readNumEntry("Digitizing", "/IntersectionSnapping", int(defaultValue));
        return bool(res)

    @staticmethod
    def setIntersectionSnapping(enabled=True):
        return Project.writeEntry("Digitizing", "/IntersectionSnapping", int(enabled));

    # Intersection Layers, i.e. the system-wide setting

    @staticmethod
    def intersectionLayers(defaultValue=[]):
        return Project.readListEntry("Digitizing", "/AvoidIntersectionsList", defaultValue);

    # Selected Layer Snapping, i.e when snapping mode is SelectedLayers

    @staticmethod
    def snapSettingsForLayer(layerId):
        return QgsProject.instance().snapSettingsForLayer(layerId)

    @staticmethod
    def setSnapSettingsForLayer(layerId, enabled,snapType, units, tolerance, avoidIntersections):
        return QgsProject.instance().setSnapSettingsForLayer(layerId, enabled,snapType, units, tolerance, avoidIntersections)

    @staticmethod
    def layerSnappingEnabled(layerId):
        layerIdList = Project.readListEntry("Digitizing", "/LayerSnappingList")
        enabledList = Project.readListEntry("Digitizing", "/LayerSnappingEnabledList")
        try:
            idx = layerIdList.index(layerId)
            return enabledList[idx] == 'enabled'
        except:
            pass
        return False

    @staticmethod
    def setLayerSnappingEnabled(layerId, enabled):
        layerIdList = Project.readListEntry("Digitizing", "/LayerSnappingList")
        enabledList = Project.readListEntry("Digitizing", "/LayerSnappingEnabledList")
        try:
            idx = layerIdList.index(layerId)
            if enabled:
                enabledList[idx] = 'enabled'
            else:
                enabledList[idx] = 'disabled'
            Project.writeEntry("Digitizing", "/LayerSnappingEnabledList", enabledList)
        except:
            pass

    @staticmethod
    def layerSnappingEnabledLayers():
        enabledLayers = []
        layerIdList = Project.readListEntry("Digitizing", "/LayerSnappingList")
        enabledList = Project.readListEntry("Digitizing", "/LayerSnappingEnabledList")
        for idx in range(0, len(layerIdList)):
            if enabledList[idx] == 'enabled':
                enabledLayers.append(layerIdList[idx])
        return enabledLayers

    @staticmethod
    def setLayerSnappingEnabledLayers(enabledLayers):
        enabledList = []
        layerIdList, ok = Project.readListEntry("Digitizing", "/LayerSnappingList")
        for layerId in layerIdList:
            if layerId in enabledLayers:
                enabledList.append('enabled')
            else:
                enabledList.append('disabled')
        Project.writeEntry("Digitizing", "/LayerSnappingEnabledList", enabledList)


# Snapping Actions

class SnappingToleranceAction(QWidgetAction):

    """QAction to change Snapping Tolerance for a project
    """

    snappingToleranceChanged = pyqtSignal(float)

    _iface = None
    _project = QgsProject.instance()

    def __init__(self, parent=None):
        """Initialises the Snapping Tolerance Editing Action

        Args:
            parent (QWidget): The parent widget, defaults to None.
        """

        super(SnappingToleranceAction, self).__init__(parent)

        self._toleranceSpin = QDoubleSpinBox(parent)
        self._toleranceSpin.setDecimals(5)
        self._toleranceSpin.setRange(0.0, 100000000.0)
        self.setDefaultWidget(self._toleranceSpin)
        self.setText('Snapping Tolerance')
        self.setStatusTip('Set the snapping tolerance')
        self._refresh()

        self._toleranceSpin.valueChanged.connect(self._changed)
        # Make sure we catch changes in the main snapping dialog
        self._project.snapSettingsChanged.connect(self._refresh)
        # If a new _project is read, update to that _project's setting
        self._project.readProject.connect(self._refresh)
        # If we change the settings, make such others are told
        self.snappingToleranceChanged.connect(self._project.snapSettingsChanged)

    def setInterface(self, iface):
        self._iface = iface
        self._refresh()

    # Private API

    def _changed(self, _tolerance):
        Snapping.setProjectSnappingTolerance(self._toleranceSpin.value())
        self.snappingToleranceChanged.emit(self._toleranceSpin.value())

    def _refresh(self):
        #FIXME Ugly workaround to the reload probem, as if signal not disconnect on deletion?
        if self is None or Snapping is None:
            return
        self.blockSignals(True)
        self._toleranceSpin.setValue(Snapping.projectSnappingTolerance())
        unit = Snapping.projectSnappingUnit()
        if (unit == Snapping.Pixels):
            self._toleranceSpin.setSuffix(' px')
        elif self._iface == None:
            self._toleranceSpin.setSuffix('')
        elif unit == Snapping.LayerUnits: # == MapUnits
            layerUnits = None
            mode = Snapping.snappingMode()
            if mode == Snapping.CurrentLayer:
                layerUnits = self._iface.mapCanvas().currentLayer().crs().mapUnits()
            else:
                # TODO Find out the correct option here for all_layers!
                layerUnits = self._iface.mapCanvas().mapUnits()
            suffix = _unitToSuffix(layerUnits)
            self._toleranceSpin.setSuffix(suffix)
        elif unit == Snapping.ProjectUnits:
            projectUnits = self._iface.mapCanvas().mapUnits()
            suffix = _unitToSuffix(projectUnits)
            self._toleranceSpin.setSuffix(suffix)
        self.blockSignals(False)


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
        self._icon = QIcon(':/plugins/ark/topologicalEditing.png')
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
        self._icon = QIcon(':/plugins/ark/snapIntersections.png')
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
    _prevType = Snapping.Off

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

        self._currentIcon = QIcon(':/plugins/ark/snapLayerCurrent.png')
        self._currentAction = QAction(self._currentIcon, 'Current Layer', self)
        self._currentAction.setStatusTip('Snap to current layer')
        self._currentAction.setCheckable(True)

        self._allIcon = QIcon(':/plugins/ark/snapLayerAll.png')
        self._allAction = QAction(self._allIcon, 'All Layers', self)
        self._allAction.setStatusTip('Snap to all layers')
        self._allAction.setCheckable(True)

        self._selectedIcon = QIcon(':/plugins/ark/snapLayerSelected.png')
        self._selectedAction = QAction(self._selectedIcon, 'Selected Layers', self)
        self._selectedAction.setStatusTip('Snap to selected layers')
        self._selectedAction.setCheckable(True)

        self._snappingModeActionGroup = QActionGroup(self)
        self._snappingModeActionGroup.addAction(self._currentAction)
        self._snappingModeActionGroup.addAction(self._allAction)
        self._snappingModeActionGroup.addAction(self._selectedAction)

        self._toleranceAction = SnappingToleranceAction(self)

        self._menu = QMenu(self)
        self._menu.addActions(self._snappingModeActionGroup.actions())
        self._menu.addSeparator()
        self._menu.addAction(self._toleranceAction)
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
            if Snapping.snappingMode() == Snapping.SelectedLayers:
                Snapping.setLayerSnappingEnabledLayers(self._selectedLayers)
            else:
                Snapping.setProjectSnappingType(self._prevType)
        else:
            if Snapping.snappingMode() == Snapping.SelectedLayers:
                self._selectedLayers = Snapping.layerSnappingEnabledLayers()
                Snapping.setLayerSnappingEnabledLayers([])
            else:
                self._prevType = Snapping.projectSnappingType()
                Snapping.setProjectSnappingType(Snapping.Off)
        self.snapSettingsChanged.emit()

    def _snapCurrentLayer(self):
        Snapping.setSnappingMode(Snapping.CurrentLayer)
        self.snapSettingsChanged.emit()

    def _snapAllLayers(self):
        Snapping.setSnappingMode(Snapping.AllLayers)
        self.snapSettingsChanged.emit()

    def _snapSelectedLayers(self):
        Snapping.setSnappingMode(Snapping.SelectedLayers)
        self.snapSettingsChanged.emit()

    def _refresh(self):
        #FIXME Ugly workaround to the reload probem, as if signal not disconnect on deletion?
        if self is None or Snapping is None:
            return
        self.blockSignals(True)
        snapMode = Snapping.snappingMode()
        snapType = Snapping.projectSnappingType()
        if snapType != Snapping.Off:
            self._prevType = snapType
        self._selectedLayers = Snapping.layerSnappingEnabledLayers()
        if snapMode == Snapping.SelectedLayers:
            enabled = (len(self._selectedLayers) > 0)
            self.setChecked(enabled)
            self._setActiveAction(self._selectedAction)
        else:
            self.setChecked(snapType != Snapping.Off)
            if snapMode == Snapping.CurrentLayer:
                self._setActiveAction(self._currentAction)
            elif snapMode == Snapping.AllLayers:
                self._setActiveAction(self._allAction)
        self.blockSignals(False)

    def _setActiveAction(self, action):
        action.setChecked(True)
        self.setIcon(action.icon())


class SnappingModeCombo(QComboBox):

    snappingModeChanged = pyqtSignal(int)

    _project = QgsProject.instance()
    _snapMode = ''
    _snapType = ''

    def __init__(self, parent=None):

        super(SnappingModeCombo, self).__init__(parent)

        self.addItem('Off', Snapping.Off)
        self.addItem('Current Layer', Snapping.CurrentLayer)
        self.addItem('All Layers', Snapping.AllLayers)
        self.addItem('Selected Layers', Snapping.SelectedLayers)
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
        if mode == Snapping.Off:
            Snapping.setProjectSnappingType(Snapping.Off)
            Snapping.setSnappingMode(Snapping.CurrentLayer)
        else:
            if self._snapMode == Snapping.Off and mode != Snapping.Off:
                Snapping.setProjectSnappingType(self._snapType)
            Snapping.setSnappingMode(mode)
        self._snapMode = mode
        self.snappingModeChanged.emit(mode)

    def _refresh(self):
        mode = Snapping.snappingMode()
        if self._snapMode == Snapping.Off and mode == Snapping.CurrentLayer:
            return
        self._snapType = Snapping.projectSnappingType()
        self._snapMode = mode
        idx = self.findData(self._snapMode)
        self.setCurrentIndex(idx)


class SnappingTypeCombo(QComboBox):

    snappingTypeChanged = pyqtSignal(int)

    _project = QgsProject.instance()

    def __init__(self, parent=None):

        super(SnappingTypeCombo, self).__init__(parent)

        self.addItem('Off', Snapping.Off)
        self.addItem('Vertex', Snapping.Vertex)
        self.addItem('Segment', Snapping.Segment)
        self.addItem('Vertex and Segment', Snapping.VertexAndSegment)
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

        self.addItem('Pixels', Snapping.Pixels)
        self.addItem('Layer Units', Snapping.LayerUnits)
        self.addItem('Project Units', Snapping.ProjectUnits)
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
        if (unit == Snapping.Pixels):
            self.setSuffix(' px')
        elif self._iface == None:
            self.setSuffix('')
        elif unit == Snapping.LayerUnits: # == MapUnits
            layerUnits = None
            mode = Snapping.snappingMode()
            if mode == Snapping.CurrentLayer:
                layerUnits = self._iface.mapCanvas().currentLayer().crs().mapUnits()
            else:
                # TODO Find out the correct option here for all_layers!
                layerUnits = self._iface.mapCanvas().mapUnits()
            suffix = _unitToSuffix(layerUnits)
            self.setSuffix(suffix)
        elif unit == Snapping.ProjectUnits:
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
        snapSettingsChanged(str, bool, str, Snapping.SnappingType, Snapping.UnitType, float, bool): Signal that the layer's snap settings have been changed by the button
    """

    snapSettingsChanged = pyqtSignal(str, bool, int, int, float, bool)

    _layer = None
    _layerId = ''
    _snapEnabled = False
    _snappingType = Snapping.Vertex
    _unitType = Snapping.Pixels
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

        self._vertexIcon = QIcon(':/plugins/ark/snapVertex.png')
        self._vertexAction = QAction(self._vertexIcon, 'Vertex', self)
        self._vertexAction.setStatusTip('Snap to vertex')
        self._vertexAction.setCheckable(True)

        self._segmentIcon = QIcon(':/plugins/ark/snapSegment.png')
        self._segmentAction = QAction(self._segmentIcon, 'Segment', self)
        self._segmentAction.setStatusTip('Snap to segment')
        self._segmentAction.setCheckable(True)

        self._vertexSegmentIcon = QIcon(':/plugins/ark/snapVertexSegment.png')
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

        if (self._snappingType == Snapping.Segment):
            self.setIcon(self._segmentIcon)
            self._segmentAction.setChecked(True)
        elif (self._snappingType == Snapping.VertexAndSegment):
            self.setIcon(self._vertexSegmentIcon)
            self._vertexSegmentAction.setChecked(True)
        else: # Snapping.Vertex or undefined
            self.setIcon(self._vertexIcon)
            self._vertexAction.setChecked(True)

        if (self._unitType == Snapping.Pixels):
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
        self._snappingType = Snapping.Vertex
        self._updateSnapSettings()

    def _snapToSegment(self):
        self._snappingType = Snapping.Segment
        self._updateSnapSettings()

    def _snapToVertexSegment(self):
        self._snappingType = Snapping.VertexAndSegment
        self._updateSnapSettings()

    def _usePixelUnits(self):
        self._unitType = Snapping.Pixels
        self._updateSnapSettings()

    def _useLayerUnits(self):
        self._unitType = Snapping.LayerUnits
        self._updateSnapSettings()

    def _toleranceChanged(self, _tolerance):
        self._tolerance = _tolerance
        self._updateSnapSettings()

    def _avoidToggled(self, status):
        self._avoidIntersections = status
        self._updateSnapSettings()
