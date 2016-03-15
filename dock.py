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
A QDockWidget for use in a QGIS Plugin
"""

import os

from PyQt4.QtCore import pyqtSignal, QSize
from PyQt4.QtGui import QDockWidget, QWidget, QVBoxLayout, QToolBar, QSizePolicy

class ArkDockWidget(QDockWidget):

    _iface = None  # QgisInterface
    _dockLocation = None  # Qt.DockWidgetArea
    _action = None  # QAction

    def __init__(self, parent=None):
        super(ArkDockWidget, self).__init__(parent)

    def initGui(self, iface, location, menuAction):
        self._iface = iface
        self._dockLocation = location
        self._action = menuAction

        self._action.toggled.connect(self._toggle)
        self.visibilityChanged.connect(self._action.setChecked)
        self.dockLocationChanged.connect(self._updateDockLocation)

    def unloadGui(self):
        self._iface.removeDockWidget(self)

    def menuAction(self):
        return self._action

    def dockLocation(self):
        return self._dockLocation

    def _updateDockLocation(self, location):
        self._dockLocation = location

    def _toggle(self, checked):
        if checked:
            self._iface.addDockWidget(self._dockLocation, self)
        else:
            self._iface.removeDockWidget(self)

class ToolDockWidget(ArkDockWidget):

    toolbar = None  # QToolBar()
    widget = None  # QWidget()

    _spacer = None  # QSpacerItem()
    _contents = None  # QWidget()

    def __init__(self, widget, parent=None):
        super(ToolDockWidget, self).__init__(parent)

        self.toolbar = QToolBar(self)
        self.toolbar.setObjectName(u'toolbar')
        self.toolbar.setIconSize(QSize(22, 22))

        self.toolbar2 = QToolBar(self)
        self.toolbar2.setObjectName(u'toolbar')
        self.toolbar2.setIconSize(QSize(22, 22))
        self.toolbar2.setVisible(False)

        widget.setParent(self)
        self.widget = widget

        self._layout = QVBoxLayout(self)
        self._layout.setObjectName(u'layout')
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self.toolbar)
        self._layout.addWidget(self.toolbar2)
        self._layout.addWidget(self.widget)

        self._contents = QWidget(self)
        self._contents.setObjectName(u'contents')
        self._contents.setLayout(self._layout)
        self.setWidget(self._contents)

    def initGui(self, iface, location, menuAction):
        super(ToolDockWidget, self).initGui(iface, location, menuAction)

    def unloadGui(self):
        super(ToolDockWidget, self).unloadGui()
