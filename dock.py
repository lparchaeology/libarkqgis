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

from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QDockWidget

class ArkDockWidget(QDockWidget):

    toggled = pyqtSignal(bool)

    _iface = None  # QgisInterface
    _menuAction = None  # QAction
    _dockLocation = None  # Qt.DockWidgetArea

    def __init__(self, parent=None):
        super(ArkDockWidget, self).__init__(parent)

    def initGui(self, iface, location, menuAction):
        self._iface = iface
        self._dockLocation = location

        self._menuAction = menuAction
        self._menuAction.toggled.connect(self._toggle)
        self._menuAction.toggled.connect(self.toggled)

        self.visibilityChanged.connect(self._menuAction.setChecked)
        self.dockLocationChanged.connect(self._updateDockLocation)

    def unloadGui(self):
        self._iface.removeToolBarIcon(self._menuAction)
        self._iface.removeDockWidget(self)
        self.deleteLater()

    def menuAction(self):
        return self._menuAction

    def dockLocation(self):
        return self._dockLocation

    def _updateDockLocation(self, location):
        self._dockLocation = location

    def _toggle(self, checked):
        if checked:
            self._iface.addDockWidget(self._dockLocation, self)
        else:
            self._iface.removeDockWidget(self)
