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
API and Widgets to use to configure QGIS project snapping settings

This module provides a set of widgets to allow easy configuration of QGIS vector layer snapping.
"""

from PyQt4.QtCore import Qt, pyqtSignal, QSettings
from PyQt4.QtGui import QWidget, QToolButton, QMenu, QIcon, QAction, QActionGroup, QWidgetAction, QDoubleSpinBox, QComboBox

from qgis.core import QGis, QgsProject, QgsMapLayer, QgsMessageLog, QgsMapLayerRegistry

from project import Project
from dock import ArkDockWidget

import resources_rc

# Project setting utilities

class Snapping():

    # SnappingMode
    CurrentLayer = 0
    AllLayers = 1
    SelectedLayers = 2

    # SnappingType == QgsSnapper.SnappingType, plus Off, keep values the same
    Vertex = 0
    Segment = 1
    VertexAndSegment = 2
    Off = 3

    # SnappingUnit == QgsTolerance.UnitType, keep values the same
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
        return Snapping._fromSnapType(value)

    @staticmethod
    def setDefaultSnappingType(snapType=Off):
        snapType = Snapping._toDefaultSnapType(snapType)
        return QSettings().setValue('/qgis/digitizing/default_snap_mode', snapType, str)

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
        value = Project.readEntry("Digitizing", "/DefaultSnapType", Snapping._toDefaultSnapType(defaultValue));
        return Snapping._fromSnapType(value)

    @staticmethod
    def setProjectSnappingType(snapType=Off):
        return Project.writeEntry("Digitizing", "/DefaultSnapType", Snapping._toDefaultSnapType(snapType));

    @staticmethod
    def _fromSnapType(value):
        if value == 'off':
            return Snapping.Off
        elif value == 'to_vertex' or value == 'to vertex':
            return Snapping.Vertex
        elif value == 'to_segment' or value == 'to segment':
            return Snapping.Segment
        elif value == 'to_vertex_and_segment' or value == 'to vertex and segment':
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
    def setSnapSettingsForLayer(layerId, enabled, snapType, units, tolerance, avoidIntersections):
        return QgsProject.instance().setSnapSettingsForLayer(layerId, enabled,snapType, units, tolerance, avoidIntersections)

    @staticmethod
    def layerSnappingEnabled(layerId):
        value = Snapping._layerSnappingValue(layerId, "/LayerSnappingEnabledList", Snapping.Vertex)
        return (value == u'enabled')

    @staticmethod
    def setLayerSnappingEnabled(layerId, enabled):
        value = u'disabled'
        if enabled:
            value = u'enabled'
        Snapping._setLayerSnappingValue(layerId, "/LayerSnappingEnabledList", value)

    @staticmethod
    def layerSnappingType(layerId):
        value = Snapping._layerSnappingValue(layerId, "/LayerSnapToList", Snapping.Vertex)
        return Snapping._fromSnapType(value)

    @staticmethod
    def setLayerSnappingType(layerId, snapType):
        Snapping._setLayerSnappingValue(layerId, "/LayerSnapToList", Snapping._toSnapType(snapType))

    @staticmethod
    def layerSnappingUnit(layerId):
        return int(Snapping._layerSnappingValue(layerId, "/LayerSnappingToleranceUnitList", Snapping.Pixels))

    @staticmethod
    def setLayerSnappingUnit(layerId, snapUnit):
        Snapping._setLayerSnappingValue(layerId, "/LayerSnappingToleranceUnitList", snapUnit)

    @staticmethod
    def layerSnappingTolerance(layerId):
        return float(Snapping._layerSnappingValue(layerId, "/LayerSnappingToleranceList", 0.0))

    @staticmethod
    def setLayerSnappingTolerance(layerId, tolerance):
        Snapping._setLayerSnappingValue(layerId, "/LayerSnappingToleranceList", tolerance)

    @staticmethod
    def layerSnappingAvoidIntersections(layerId):
        layerIdList = Project.readListEntry("Digitizing", "/AvoidIntersectionsList")
        try:
            idx = layerIdList.index(layerId)
            return True
        except:
            return False

    @staticmethod
    def setLayerSnappingAvoidIntersections(layerId, avoid):
        layerIdList = Project.readListEntry("Digitizing", "/AvoidIntersectionsList")
        try:
            idx = layerIdList.index(layerId)
            if not avoid:
                layerIdList.pop(idx)
        except:
            if avoid:
                layerIdList.append(layerId)
        Project.writeEntry("Digitizing", "/AvoidIntersectionsList", layerIdList)

    @staticmethod
    def _layerSnappingValue(layerId, layerListId, defaultValue):
        layerIdList = Project.readListEntry("Digitizing", "/LayerSnappingList")
        valueList = Project.readListEntry("Digitizing", layerListId)
        try:
            idx = layerIdList.index(layerId)
            return valueList[idx]
        except:
            return defaultValue

    @staticmethod
    def _setLayerSnappingValue(layerId, layerListId, value):
        layerIdList = Project.readListEntry("Digitizing", "/LayerSnappingList")
        valueList = Project.readListEntry("Digitizing", layerListId)
        try:
            idx = layerIdList.index(layerId)
            valueList[idx] = str(value)
            Project.writeEntry("Digitizing", layerListId, valueList)
        except:
            pass

    @staticmethod
    def layerSnappingEnabledLayers():
        enabledLayers = []
        layerIdList = Project.readListEntry("Digitizing", "/LayerSnappingList")
        enabledList = Project.readListEntry("Digitizing", "/LayerSnappingEnabledList")
        for idx in range(0, len(layerIdList)):
            if enabledList[idx] == u'enabled':
                enabledLayers.append(layerIdList[idx])
        return enabledLayers

    @staticmethod
    def setLayerSnappingEnabledLayers(enabledLayers):
        enabledList = []
        layerIdList = Project.readListEntry("Digitizing", "/LayerSnappingList")
        for layerId in layerIdList:
            if layerId in enabledLayers:
                enabledList.append(u'enabled')
            else:
                enabledList.append(u'disabled')
        Project.writeEntry("Digitizing", "/LayerSnappingEnabledList", enabledList)


# Snapping Actions

class ProjectSnappingEnabledAction(QAction):

    """QAction to enable snapping

    Signals:
            snapSettingsChanged(): Signal that the snapping settings has been changed by the button
    """

    snappingEnabledChanged = pyqtSignal()

    _selectedLayers = []
    _prevType = Snapping.Off

    def __init__(self, parent=None):
        """
        Initialises the snapping mode button

        Args:
            parent (QWidget): The parent widget, defaults to None.
        """

        super(ProjectSnappingEnabledAction, self).__init__(parent)

        self.setText('Toggle Snapping')
        self.setStatusTip('Enbale/disable snapping')
        self.setIcon(QIcon(':/plugins/ark/snapEnable.png'))
        self.setCheckable(True)
        self._refresh()
        self.triggered.connect(self._triggered)

        # Make sure we catch changes in the main snapping dialog
        QgsProject.instance().snapSettingsChanged.connect(self._refresh)
        # If a new project is read, update to that project's setting
        QgsProject.instance().readProject.connect(self._refresh)
        self.snappingEnabledChanged.connect(QgsProject.instance().snapSettingsChanged)

    def setInterface(self, iface):
        self._toleranceAction.setInterface(iface)

    # Private API

    def _triggered(self, checked):
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
        self.snappingEnabledChanged.emit()

    def _refresh(self):
        self.blockSignals(True)
        snapMode = Snapping.snappingMode()
        snapType = Snapping.projectSnappingType()
        if snapType != Snapping.Off:
            self._prevType = snapType
        selectedLayers = Snapping.layerSnappingEnabledLayers()
        if len(selectedLayers) > 0:
            self._selectedLayers = selectedLayers
        if snapMode == Snapping.SelectedLayers:
            self.setChecked(len(selectedLayers) > 0)
        else:
            self.setChecked(snapType != Snapping.Off)
        self.blockSignals(False)


class SnappingModeAction(QAction):

    """QAction to change Snapping Mode for a project
    """

    snappingModeChanged = pyqtSignal(int)

    def __init__(self, snapMode, parent=None):
        """Initialises the Snapping Mode Action

        Args:
            snapMode (Snapping.SnappingMode): The Snapping Mode for this action
            parent (QWidget): The parent widget, defaults to None.
        """

        super(SnappingModeAction, self).__init__(parent)

        self._snapMode = snapMode
        if snapMode == Snapping.CurrentLayer:
            self.setText('Current Layer')
            self.setStatusTip('Snap to current layer')
            self._icon = QIcon(':/plugins/ark/snapLayerCurrent.png')
        elif snapMode == Snapping.AllLayers:
            self.setText('All Layers')
            self.setStatusTip('Snap to all layers')
            self._icon = QIcon(':/plugins/ark/snapLayerAll.png')
        elif snapMode == Snapping.SelectedLayers:
            self.setText('Selected Layers')
            self.setStatusTip('Snap to selected layers')
            self._icon = QIcon(':/plugins/ark/snapLayerSelected.png')

        self.setIcon(self._icon)
        self.setCheckable(True)

        self._refresh()
        self.triggered.connect(self._triggered)

        # Make sure we catch changes in the main snapping dialog
        QgsProject.instance().snapSettingsChanged.connect(self._refresh)
        # If a new project is read, update to that project's setting
        QgsProject.instance().readProject.connect(self._refresh)
        # If we change the settings, make such others are told
        self.snappingModeChanged.connect(QgsProject.instance().snapSettingsChanged)

    # Private API

    def _triggered(self, checked):
        if checked:
            Snapping.setSnappingMode(self._snapMode)
            self.snappingModeChanged.emit(self._snapMode)

    def _refresh(self):
        self.blockSignals(True)
        self.setChecked(self._snapMode == Snapping.snappingMode())
        self.blockSignals(False)

class SnappingTypeAction(QAction):

    """QAction base class for Snapping Type
    """

    def __init__(self, snapType, parent=None):
        """Initialises the Snapping Type Action

        Args:
            snapType (Snapping.SnappingType): The Snapping Type for this action
            parent (QWidget): The parent widget, defaults to None.
        """

        super(SnappingTypeAction, self).__init__(parent)

        self._snapType = snapType
        if snapType == Snapping.CurrentLayer:
            self.setText('Vertex')
            self.setStatusTip('Snap to vertex')
            self._icon = QIcon(':/plugins/ark/snapVertex.png')
        elif snapType == Snapping.AllLayers:
            self.setText('Segment')
            self.setStatusTip('Snap to segment')
            self._icon = QIcon(':/plugins/ark/snapSegment.png')
        elif snapType == Snapping.SelectedLayers:
            self.setText('Vertex and Segment')
            self.setStatusTip('Snap to vertex and segment')
            self._icon = QIcon(':/plugins/ark/snapVertexSegment.png')
        self.setIcon(self._icon)
        self.setCheckable(True)

        self._refresh()
        self.triggered.connect(self._triggered)

    # Private API

    def _triggered(self, checked):
        pass

    def _refresh(self):
        pass

class ProjectSnappingTypeAction(SnappingTypeAction):

    """QAction to change Project Snapping Type for a project
    """

    snappingTypeChanged = pyqtSignal(int)

    def __init__(self, snapType, parent=None):
        """Initialises the Project Snapping Type Action

        Args:
            snapType (Snapping.SnappingType): The Snapping Type for this action
            parent (QWidget): The parent widget, defaults to None.
        """

        super(ProjectSnappingTypeAction, self).__init__(snapType, parent)

        # Make sure we catch changes in the main snapping dialog
        QgsProject.instance().snapSettingsChanged.connect(self._refresh)
        # If a new project is read, update to that project's setting
        QgsProject.instance().readProject.connect(self._refresh)
        # If we change the settings, make such others are told
        self.snappingTypeChanged.connect(QgsProject.instance().snapSettingsChanged)

    # Private API

    def _triggered(self, checked):
        if checked:
            Snapping.setProjectSnappingType(self._snapType)
            self.snappingTypeChanged.emit(self._snapType)

    def _refresh(self):
        self.blockSignals(True)
        self.setChecked(Snapping.projectSnappingType() == self._snapType)
        self.setEnabled(Snapping.snappingMode() != Snapping.SelectedLayers)
        self.blockSignals(False)

class LayerSnappingTypeAction(SnappingTypeAction):

    """QAction to change Layer Snapping Type
    """

    snappingTypeChanged = pyqtSignal(str, int)

    _layerId = ''

    def __init__(self, layerId, snapType, parent=None):
        """Initialises the Layer Snapping Type Action

        Args:
            layerId (str): The Layer ID for this action
            snapType (Snapping.SnappingType): The Snapping Type for this action
            parent (QWidget): The parent widget, defaults to None.
        """

        super(LayerSnappingTypeAction, self).__init__(snapType, parent)
        self._layerId = layerId

        # Make sure we catch changes in the main snapping dialog
        QgsProject.instance().snapSettingsChanged.connect(self._refresh)
        # If the layer is removed then disable the button
        QgsMapLayerRegistry.instance().layerRemoved.connect(self._layerRemoved)
        # If we change the settings, make sure others are told
        self.snappingTypeChanged.connect(QgsProject.instance().snapSettingsChanged)

    # Private API

    def _layerRemoved(self, layerId):
        if layerId == self._layerId:
            self._layerId = ''
            self.setEnabled(False)
            QgsProject.instance().snapSettingsChanged.disconnect(self._refresh)
            QgsMapLayerRegistry.instance().layerRemoved.disconnect(self._layerRemoved)
            self.snappingTypeChanged.disconnect(QgsProject.instance().snapSettingsChanged)

    def _triggered(self, checked):
        if checked and self._layerId:
            Snapping.setLayerSnappingType(self._layerId, self._snapType)
            self.snappingTypeChanged.emit(self._layerId, self._snapType)

    def _refresh(self):
        self.blockSignals(True)
        if self._layerId:
            self.setChecked(Snapping.layerSnappingType(self._layerId) == self._snapType)
        else:
            self.setChecked(False)
        self.blockSignals(False)

class SnappingUnitAction(QAction):

    """QAction base class for Snapping Unit
    """

    def __init__(self, snapUnit, parent=None):
        """Initialises the Snapping Unit Action

        Args:
            snapUnits (Snapping.SnappingUnits): The Snapping Units for this action
            parent (QWidget): The parent widget, defaults to None.
        """

        super(SnappingUnitAction, self).__init__(parent)

        self._snapUnit = snapUnit
        if snapUnit == Snapping.Pixels:
            self.setText('Pixels')
            self.setStatusTip('Use pixels')
        elif snapUnit == Snapping.LayerUnits:
            self.setText('Layer Units')
            self.setStatusTip('Use layer units')
        elif snapUnit == Snapping.ProjectUnits:
            self.setText('Project Units')
            self.setStatusTip('Use project units')

        self.setCheckable(True)

        self._refresh()
        self.triggered.connect(self._triggered)

    # Private API

    def _triggered(self, checked):
        pass

    def _refresh(self):
        pass

class ProjectSnappingUnitAction(SnappingUnitAction):

    """QAction to change Snapping Unit for a project
    """

    snappingUnitChanged = pyqtSignal(int)

    def __init__(self, snapUnit, parent=None):
        """Initialises the Snapping Unit Action

        Args:
            snapUnits (Snapping.SnappingUnits): The Snapping Units for this action
            parent (QWidget): The parent widget, defaults to None.
        """

        super(ProjectSnappingUnitAction, self).__init__(snapUnit, parent)

        # Make sure we catch changes in the main snapping dialog
        QgsProject.instance().snapSettingsChanged.connect(self._refresh)
        # If a new project is read, update to that project's setting
        QgsProject.instance().readProject.connect(self._refresh)
        # If we change the settings, make such others are told
        self.snappingUnitChanged.connect(QgsProject.instance().snapSettingsChanged)

    # Private API

    def _triggered(self, checked):
        if checked:
            Snapping.setProjectSnappingUnit(self._snapUnit)
            self.snappingUnitChanged.emit(self._snapUnit)

    def _refresh(self):
        self.blockSignals(True)
        self.setChecked(Snapping.projectSnappingUnit() == self._snapUnit)
        self.setEnabled(Snapping.snappingMode() != Snapping.SelectedLayers)
        self.blockSignals(False)

class LayerSnappingUnitAction(SnappingUnitAction):

    """QAction to change Layer Snapping Unit
    """

    snappingUnitChanged = pyqtSignal(str, int)

    _layerId = ''

    def __init__(self, layerId, snapUnit, parent=None):
        """Initialises the Snapping Unit Action

        Args:
            layerId (str): The Layer ID for this action
            snapUnits (Snapping.SnappingUnits): The Snapping Units for this action
            parent (QWidget): The parent widget, defaults to None.
        """

        super(LayerSnappingUnitAction, self).__init__(snapUnit, parent)
        self._layerId = layerId

        # Make sure we catch changes in the main snapping dialog
        QgsProject.instance().snapSettingsChanged.connect(self._refresh)
        # If the layer is removed then disable the button
        QgsMapLayerRegistry.instance().layerRemoved.connect(self._layerRemoved)
        # If we change the settings, make such others are told
        self.snappingUnitChanged.connect(QgsProject.instance().snapSettingsChanged)

    # Private API

    def _layerRemoved(self, layerId):
        if layerId == self._layerId:
            self._layerId = ''
            self.setEnabled(False)
            QgsProject.instance().snapSettingsChanged.disconnect(self._refresh)
            QgsMapLayerRegistry.instance().layerRemoved.disconnect(self._layerRemoved)
            self.snappingUnitChanged.disconnect(QgsProject.instance().snapSettingsChanged)

    def _triggered(self, checked):
        if checked and self._layerId:
            Snapping.setLayerSnappingUnit(self._layerId, self._snapUnit)
            self.snappingUnitChanged.emit(self._layerId, self._snapUnit)

    def _refresh(self):
        self.blockSignals(True)
        self.setChecked(Snapping.layerSnappingUnit(self._layerId) == self._snapUnit)
        self.blockSignals(False)

class SnappingToleranceAction(QWidgetAction):

    """QAction base class for Snapping Tolerance
    """

    snappingToleranceChanged = pyqtSignal(float)

    _iface = None

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

    def setInterface(self, iface):
        self._iface = iface
        self._refresh()

    # Private API

    def _changed(self, tolerance):
        pass

    def _refresh(self):
        pass

class ProjectSnappingToleranceAction(SnappingToleranceAction):

    """QAction to change Project Snapping Tolerance
    """

    snappingToleranceChanged = pyqtSignal(float)

    _iface = None

    def __init__(self, parent=None):
        """Initialises the Snapping Tolerance Editing Action

        Args:
            parent (QWidget): The parent widget, defaults to None.
        """

        super(ProjectSnappingToleranceAction, self).__init__(parent)

        # Make sure we catch changes in the main snapping dialog
        QgsProject.instance().snapSettingsChanged.connect(self._refresh)
        # If a new project is read, update to that project's setting
        QgsProject.instance().readProject.connect(self._refresh)
        # If we change the settings, make such others are told
        self.snappingToleranceChanged.connect(QgsProject.instance().snapSettingsChanged)

    def setInterface(self, iface):
        self._iface = iface
        self._refresh()

    # Private API

    def _changed(self, tolerance):
        Snapping.setProjectSnappingTolerance(tolerance)
        self.snappingToleranceChanged.emit(tolerance)

    def _refresh(self):
        self.blockSignals(True)
        self._toleranceSpin.blockSignals(True)
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
        self.setEnabled(Snapping.snappingMode() != Snapping.SelectedLayers)
        self._toleranceSpin.blockSignals(False)
        self.blockSignals(False)

class LayerSnappingToleranceAction(SnappingToleranceAction):

    """QAction to change Layer Snapping Tolerance
    """

    snappingToleranceChanged = pyqtSignal(str, float)

    _iface = None
    _layerId = ''

    def __init__(self, layerId, parent=None):
        """Initialises the Snapping Tolerance Editing Action

        Args:
            layerId (str): The Layer ID for this action
            parent (QWidget): The parent widget, defaults to None.
        """

        super(LayerSnappingToleranceAction, self).__init__(parent)
        self._layerId = layerId

        # Make sure we catch changes in the main snapping dialog
        QgsProject.instance().snapSettingsChanged.connect(self._refresh)
        # If the layer is removed then disable the button
        QgsMapLayerRegistry.instance().layerRemoved.connect(self._layerRemoved)
        # If we change the settings, make such others are told
        self.snappingToleranceChanged.connect(QgsProject.instance().snapSettingsChanged)

    def setInterface(self, iface):
        self._iface = iface
        self._refresh()

    # Private API

    def _layerRemoved(self, layerId):
        if layerId == self._layerId:
            self._layerId = ''
            self.setEnabled(False)
            QgsProject.instance().snapSettingsChanged.disconnect(self._refresh)
            QgsMapLayerRegistry.instance().layerRemoved.disconnect(self._layerRemoved)
            self.snappingToleranceChanged.disconnect(QgsProject.instance().snapSettingsChanged)

    def _changed(self, tolerance):
        Snapping.setLayerSnappingTolerance(self._layerId, tolerance)
        self.snappingToleranceChanged.emit(self._layerId, tolerance)

    def _refresh(self):
        self.blockSignals(True)
        self._toleranceSpin.blockSignals(True)
        if self._layerId:
            self._toleranceSpin.setValue(Snapping.layerSnappingTolerance(self._layerId))
            unit = Snapping.layerSnappingUnit(self._layerId)
            if (unit == Snapping.Pixels):
                self._toleranceSpin.setSuffix(' px')
            elif self._iface == None:
                self._toleranceSpin.setSuffix('')
            elif unit == Snapping.LayerUnits:
                layerUnits = QgsMapLayerRegistry.instance().mapLayer(self._layerId).crs().mapUnits()
                suffix = _unitToSuffix(layerUnits)
                self._toleranceSpin.setSuffix(suffix)
            elif unit == Snapping.ProjectUnits:
                projectUnits = self._iface.mapCanvas().mapUnits()
                suffix = _unitToSuffix(projectUnits)
                self._toleranceSpin.setSuffix(suffix)
        else:
            self._toleranceSpin.setValue(0.0)
            self._toleranceSpin.setSuffix('')
        self._toleranceSpin.blockSignals(False)
        self.blockSignals(False)

class LayerSnappingEnabledAction(QAction):

    """QAction for Layer Snapping Enabled
    """

    layerId = ''

    snappingEnabledChanged = pyqtSignal(str, bool)

    def __init__(self, layerId, parent=None):
        """Initialises the Layer Snapping Enabled Action

        Args:
            layerId (str): The Layer ID for this action
            parent (QWidget): The parent widget, defaults to None.
        """

        super(LayerSnappingEnabledAction, self).__init__(parent)
        self._layerId = layerId

        self.setCheckable(True)
        self.setText('Toggle Layer Snapping')
        self.setStatusTip('Toggled snapping on this layer')
        self.setIcon(QIcon(':/plugins/ark/snapEnable.png'))

        self._refresh()
        self.triggered.connect(self._triggered)

        # Make sure we catch changes in the main snapping dialog
        QgsProject.instance().snapSettingsChanged.connect(self._refresh)
        # If the layer is removed then disable the button
        QgsMapLayerRegistry.instance().layerRemoved.connect(self._layerRemoved)
        # If we change the settings, make such others are told
        self.snappingEnabledChanged.connect(QgsProject.instance().snapSettingsChanged)

    # Private API

    def _layerRemoved(self, layerId):
        if layerId == self._layerId:
            self._layerId = ''
            self.setEnabled(False)
            QgsProject.instance().snapSettingsChanged.disconnect(self._refresh)
            QgsMapLayerRegistry.instance().layerRemoved.disconnect(self._layerRemoved)
            self.snappingEnabledChanged.disconnect(QgsProject.instance().snapSettingsChanged)

    def _triggered(self, status):
        Snapping.setLayerSnappingEnabled(self._layerId, status)
        self.snappingEnabledChanged.emit(self._layerId, status)

    def _refresh(self):
        if self._layerId:
            self.blockSignals(True)
            self.setChecked(Snapping.layerSnappingEnabled(self._layerId))
            self.blockSignals(False)
        else:
            self.setChecked(False)

class LayerSnappingAvoidIntersectionsAction(QAction):

    """QAction to toggle Layer Avoid Intersections
    """

    layerId = ''

    avoidIntersectionsChanged = pyqtSignal(str, bool)

    def __init__(self, layerId, parent=None):
        """Initialises the Layer Avoid Intersections Action

        Args:
            layerId (str): The Layer ID for this action
            parent (QWidget): The parent widget, defaults to None.
        """

        super(LayerSnappingAvoidIntersectionsAction, self).__init__(parent)
        self._layerId = layerId

        self.setCheckable(True)
        self.setText('Snap overlapping edges')
        self.setStatusTip('Snap to edges of any overlapping polygons, aka "Avoid Intersections"')

        self._refresh()
        self.triggered.connect(self._triggered)

        # Make sure we catch changes in the main snapping dialog
        QgsProject.instance().snapSettingsChanged.connect(self._refresh)
        # If the layer is removed then disable the button
        QgsMapLayerRegistry.instance().layerRemoved.connect(self._layerRemoved)
        # If we change the settings, make such others are told
        self.avoidIntersectionsChanged.connect(QgsProject.instance().snapSettingsChanged)

    # Private API

    def _layerRemoved(self, layerId):
        if layerId == self._layerId:
            self._layerId = ''
            self.setEnabled(False)
            QgsProject.instance().snapSettingsChanged.disconnect(self._refresh)
            QgsMapLayerRegistry.instance().layerRemoved.disconnect(self._layerRemoved)
            self.avoidIntersectionsChanged.disconnect(QgsProject.instance().snapSettingsChanged)

    def _triggered(self, status):
        Snapping.setLayerSnappingAvoidIntersections(self._layerId, status)
        self.avoidIntersectionsChanged.emit(self._layerId, status)

    def _refresh(self):
        if self._layerId:
            self.blockSignals(True)
            self.setChecked(Snapping.layerSnappingAvoidIntersections(self._layerId))
            self.blockSignals(False)
        else:
            self.setChecked(False)

class TopologicalEditingAction(QAction):

    """QAction to toggle Topological Editing for a project
    """

    topologicalEditingChanged = pyqtSignal(bool)

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

        self._refresh()
        self.triggered.connect(self._triggered)

        # Make sure we catch changes in the main snapping dialog
        QgsProject.instance().snapSettingsChanged.connect(self._refresh)
        # If a new project is read, update to that project's setting
        QgsProject.instance().readProject.connect(self._refresh)
        # If we change the settings, make such others are told
        self.topologicalEditingChanged.connect(QgsProject.instance().snapSettingsChanged)

    # Private API

    def _triggered(self, status):
        Snapping.setTopologicalEditing(status)
        self.topologicalEditingChanged.emit(status)

    def _refresh(self):
        self.blockSignals(True)
        self.setChecked(Snapping.topologicalEditing())
        self.blockSignals(False)

class IntersectionSnappingAction(QAction):

    """QAction to toggle Intersection Snapping for a project
    """

    intersectionSnappingChanged = pyqtSignal(bool)

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

        self._refresh()
        self.triggered.connect(self._triggered)

        # Make sure we catch changes in the main snapping dialog
        QgsProject.instance().snapSettingsChanged.connect(self._refresh)
        # If a new project is read, update to that project's setting
        QgsProject.instance().readProject.connect(self._refresh)
        # If we change the settings, make such others are told
        self.intersectionSnappingChanged.connect(QgsProject.instance().snapSettingsChanged)

    # Private API

    def _triggered(self, status):
        Snapping.setIntersectionSnapping(status)
        self.intersectionSnappingChanged.emit(status)

    def _refresh(self):
        self.blockSignals(True)
        self.setChecked(Snapping.intersectionSnapping())
        self.blockSignals(False)

# Snapping Widgets

class ControlMenu(QMenu):

    """Menu to change snapping mode
    """

    def __init__(self, parent=None):
        super(ControlMenu, self).__init__(parent)

    def keyPressEvent(self, e):
        action = self.activeAction()
        if ((e.key() == Qt.Key_Return or e.key() == Qt.Key_Enter)
            and e.modifiers() == Qt.ControlModifier and action is not None and action.isEnabled()):
            action.trigger()
        else:
            super(ControlMenu, self).keyPressEvent(e)

    def mouseReleaseEvent(self, e):
        action = self.activeAction()
        if e.modifiers() == Qt.ControlModifier and action is not None and action.isEnabled():
            action.trigger()
        else:
            super(ControlMenu, self).mouseReleaseEvent(e)

class ProjectSnappingAction(ProjectSnappingEnabledAction):

    """QAction to configure snapping

    Signals:
            snapSettingsChanged(): Signal that the snapping settings has been changed by the action
    """

    snapSettingsChanged = pyqtSignal()

    def __init__(self, parent=None):
        """
        Initialises the snapping mode button

        Args:
            parent (QWidget): The parent widget, defaults to None.
        """

        super(ProjectSnappingAction, self).__init__(parent)
        self.setCheckable(True)

        self._currentAction = SnappingModeAction(Snapping.CurrentLayer, self)
        self._allAction = SnappingModeAction(Snapping.AllLayers, self)
        self._selectedAction = SnappingModeAction(Snapping.SelectedLayers, self)

        self._snappingModeActionGroup = QActionGroup(self)
        self._snappingModeActionGroup.addAction(self._currentAction)
        self._snappingModeActionGroup.addAction(self._allAction)
        self._snappingModeActionGroup.addAction(self._selectedAction)

        self._vertexAction = ProjectSnappingTypeAction(Snapping.Vertex, self)
        self._segmentAction = ProjectSnappingTypeAction(Snapping.Segment, self)
        self._vertexSegmentAction = ProjectSnappingTypeAction(Snapping.VertexAndSegment, self)

        self._snappingTypeActionGroup = QActionGroup(self)
        self._snappingTypeActionGroup.addAction(self._vertexAction)
        self._snappingTypeActionGroup.addAction(self._segmentAction)
        self._snappingTypeActionGroup.addAction(self._vertexSegmentAction)

        self._pixelUnitsAction = ProjectSnappingUnitAction(Snapping.Pixels, self)
        self._layerUnitsAction = ProjectSnappingUnitAction(Snapping.LayerUnits, self)
        self._projectUnitsAction = ProjectSnappingUnitAction(Snapping.ProjectUnits, self)

        self._unitTypeActionGroup = QActionGroup(self)
        self._unitTypeActionGroup.addAction(self._pixelUnitsAction)
        self._unitTypeActionGroup.addAction(self._layerUnitsAction)
        self._unitTypeActionGroup.addAction(self._projectUnitsAction)

        self._toleranceAction = ProjectSnappingToleranceAction(parent)

        menu = ControlMenu(parent)
        menu.addActions(self._snappingModeActionGroup.actions())
        menu.addSeparator()
        menu.addActions(self._snappingTypeActionGroup.actions())
        menu.addSeparator()
        menu.addAction(self._toleranceAction)
        menu.addActions(self._unitTypeActionGroup.actions())
        self.setMenu(menu)

        self._refreshIcon()

        # Make sure we catch changes in the main snapping dialog
        QgsProject.instance().snapSettingsChanged.connect(self._refreshIcon)

    def setInterface(self, iface):
        self._toleranceAction.setInterface(iface)

    # Private API

    def _refreshIcon(self):
        snapMode = Snapping.snappingMode()
        if snapMode == Snapping.SelectedLayers:
            self.setIcon(self._selectedAction.icon())
        elif snapMode == Snapping.CurrentLayer:
            self.setIcon(self._currentAction.icon())
        elif snapMode == Snapping.AllLayers:
            self.setIcon(self._allAction.icon())

class LayerSnappingAction(LayerSnappingEnabledAction):

    """Action to change snapping settings for a QGIS vector layer

    Signals:
        snapSettingsChanged(str): Signal that the layer's snap settings have been changed by the button
    """

    snapSettingsChanged = pyqtSignal(str)

    _layerId = ''
    _toleranceAction = None # LayerSnappingToleranceAction()

    def __init__(self, layer, parent=None):
        """Initialises the snapping action

        After creating the button, you must call setLayer().

        Args:
            parent (QWidget): The parent widget, defaults to None.
        """

        #Disable until we have a _layerId
        if (layer is None or not layer.isValid() or layer.type() != QgsMapLayer.VectorLayer):
            super(LayerSnappingAction, self).__init__('', parent)
            self.setEnabled(False)
            return

        super(LayerSnappingAction, self).__init__(layer.id(), parent)

        self._vertexAction = LayerSnappingTypeAction(self._layerId, Snapping.Vertex, self)
        self._segmentAction = LayerSnappingTypeAction(self._layerId, Snapping.Segment, self)
        self._vertexSegmentAction = LayerSnappingTypeAction(self._layerId, Snapping.VertexAndSegment, self)

        self._snappingTypeActionGroup = QActionGroup(self)
        self._snappingTypeActionGroup.addAction(self._vertexAction)
        self._snappingTypeActionGroup.addAction(self._segmentAction)
        self._snappingTypeActionGroup.addAction(self._vertexSegmentAction)

        self._toleranceAction = LayerSnappingToleranceAction(self._layerId, parent)

        self._pixelUnitsAction = LayerSnappingUnitAction(self._layerId, Snapping.Pixels, self)
        self._layerUnitsAction = LayerSnappingUnitAction(self._layerId, Snapping.LayerUnits, self)
        self._projectUnitsAction = LayerSnappingUnitAction(self._layerId, Snapping.ProjectUnits, self)

        self._unitTypeActionGroup = QActionGroup(self)
        self._unitTypeActionGroup.addAction(self._pixelUnitsAction)
        self._unitTypeActionGroup.addAction(self._layerUnitsAction)
        self._unitTypeActionGroup.addAction(self._projectUnitsAction)

        menu = ControlMenu(parent)
        menu.addActions(self._snappingTypeActionGroup.actions())
        menu.addSeparator()
        menu.addAction(self._toleranceAction)
        menu.addActions(self._unitTypeActionGroup.actions())
        if layer.geometryType() == QGis.Polygon:
            self._avoidAction = LayerSnappingAvoidIntersectionsAction(self._layerId, self)
            menu.addSeparator()
            menu.addAction(self._avoidAction)
        self.setMenu(menu)

        self._refreshIcon()

        # Make sure we catch changes in the main snapping dialog
        QgsProject.instance().snapSettingsChanged.connect(self._refreshIcon)
        # If any of the settings change then signal, but don't tell project as actions already have
        self.snappingEnabledChanged.connect(self.snapSettingsChanged)
        self._vertexAction.snappingTypeChanged.connect(self.snapSettingsChanged)
        self._segmentAction.snappingTypeChanged.connect(self.snapSettingsChanged)
        self._vertexSegmentAction.snappingTypeChanged.connect(self.snapSettingsChanged)
        self._toleranceAction.snappingToleranceChanged.connect(self.snapSettingsChanged)
        self._pixelUnitsAction.snappingUnitChanged.connect(self.snapSettingsChanged)
        self._layerUnitsAction.snappingUnitChanged.connect(self.snapSettingsChanged)
        self._projectUnitsAction.snappingUnitChanged.connect(self.snapSettingsChanged)
        if layer.geometryType() == QGis.Polygon:
            self._avoidAction.avoidIntersectionsChanged.connect(self.snapSettingsChanged)

    def setInterface(self, iface):
        self._toleranceAction.setInterface(iface)

    # Private API

    def _refreshIcon(self):
        if (self._segmentAction.isChecked()):
            self.setIcon(self._segmentAction.icon())
        elif (self._vertexSegmentAction.isChecked()):
            self.setIcon(self._vertexSegmentAction.icon())
        else: # Snapping.Vertex or undefined
            self.setIcon(self._vertexAction.icon())

# Individual Project Snapping Widgets

class SnappingModeCombo(QComboBox):

    snappingModeChanged = pyqtSignal(int)

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
        QgsProject.instance().snapSettingsChanged.connect(self._refresh)
        # If a new project is read, update to that project's setting
        QgsProject.instance().readProject.connect(self._refresh)
        self.snappingModeChanged.connect(QgsProject.instance().snapSettingsChanged)

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
        QgsProject.instance().snapSettingsChanged.connect(self._refresh)
        # If a new project is read, update to that project's setting
        QgsProject.instance().readProject.connect(self._refresh)
        self.snappingTypeChanged.connect(QgsProject.instance().snapSettingsChanged)

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

    def __init__(self, parent=None):

        super(SnappingUnitCombo, self).__init__(parent)

        self.addItem('Pixels', Snapping.Pixels)
        self.addItem('Layer Units', Snapping.LayerUnits)
        self.addItem('Project Units', Snapping.ProjectUnits)
        self.setCurrentIndex(0)

        self._refresh()
        self.currentIndexChanged.connect(self._changed)

        # Make sure we catch changes in the main snapping dialog
        QgsProject.instance().snapSettingsChanged.connect(self._refresh)
        # If a new project is read, update to that project's setting
        QgsProject.instance().readProject.connect(self._refresh)
        self.snappingUnitChanged.connect(QgsProject.instance().snapSettingsChanged)

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

    def __init__(self, parent=None):

        super(SnappingToleranceSpinBox, self).__init__(parent)

        self.setDecimals(5)
        self.setRange(0.0, 100000000.0)

        self._refresh()
        self.valueChanged.connect(self._changed)

        # Make sure we catch changes in the main snapping dialog
        QgsProject.instance().snapSettingsChanged.connect(self._refresh)
        # If a new project is read, update to that project's setting
        QgsProject.instance().readProject.connect(self._refresh)
        self.snappingToleranceChanged.connect(QgsProject.instance().snapSettingsChanged)

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

class LayerSnappingWidget(QWidget):

    def __init__(self, layer, parent=None):
        super(LayerSnappingWidget, self).__init__(parent)

        label = QLabel(layer.name(), self)
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding, self)
        action = LayerSnappingAction(layer, self)
        tool = QToolButton(self)
        tool.setDefaultAction(action)

        layout = QHBoxLayout(self)
        layout.setObjectName(u'layout')
        layout.addWidget(label)
        layout.addWidget(spacer)
        layout.addWidget(tool)

        self.setLayout(layout)

class SnappingDock(ArkDockWidget):

    _iface = None # QgisInterface()

    def __init__(self, iface, parent=None):
        super(SnappingDock, self).__init__(parent)
        self._iface = iface

        self.setWindowTitle(u'Snapping Panel')
        self.setObjectName(u'snappingDock')

        self._listWidget = QListWidget(self)
        self._listWidget.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self._listWidget.setDropIndicatorShown(False)

        self._dockLayout = QVBoxLayout(self)
        self._dockLayout.setObjectName(u'dockLayout')
        self._dockLayout.addWidget(self._listWidget)

        self._dockContents = QWidget(self)
        self._dockContents.setObjectName(u'dockContents')
        self._dockContents.setLayout(self._dockLayout)
        self.setWidget(self._dockContents)

        # Keep up-to-date with layers added and removed
        QgsMapLayerRegistry.instance().layersAdded.connect(self._layersAdded)
        QgsMapLayerRegistry.instance().layersRemoved.connect(self._layersRemoved)

    def refresh(self):
        self._listWidget.clear()
        layers = QgsMapLayerRegistry.instance().mapLayers()
        layerIds = layers.keys()
        sorted(layerIds)
        for layerId in layerIds:
            self.addLayer(layers[layerId])

    def addLayer(self, layer):
        if (layer is None or not layer.isValid() or layer.type() != QgsMapLayer.VectorLayer):
            return
        newItem = QListWidgetItem()
        newItem.setData(Qt.UserRole, layer.id())
        newItem.setSizeHint(layerWidget.minimumSizeHint())
        self._listWidget.addItem(newItem);
        self._listWidget.setItemWidget(newItem, LayerSnappingWidget(layer, self))

    def removeLayer(self, layerId):
        for idx in range(0, self._listWidget.count() - 1):
            if self._listWidget.item(idx).data() == layerId:
                self._listWidget.takeItem(idx)
                return

    def _layersAdded(self, layers):
        for layer in layers:
            self.addLayer(layer)

    def _layersRemoved(self, layerIds):
        for idx in range(self._listWidget.count() - 1, 0):
            if self._listWidget.item(idx).data() in layerIds:
                self._listWidget.takeItem(idx)
