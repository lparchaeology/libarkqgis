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

from PyQt4.QtCore import Qt, QDateTime

from qgis.core import QGis, QgsProject
from qgis.gui import QgsMessageBar

# Datetime utilities

def timestamp():
    return QDateTime.currentDateTimeUtc().toString(Qt.ISODate)

# String utilities

def quote(string):
    return "'" + string + "'"

def doublequote(string):
    return '"' + string + '"'

# Message utilities

def showMessage(iface, text, level=QgsMessageBar.INFO, duration=0):
    iface.messageBar().pushMessage(text, level, duration)

def showCriticalMessage(iface, text, duration=0):
    iface.messageBar().pushMessage(text, QgsMessageBar.CRITICAL, duration)

def showStatusMessage(iface, text):
    iface.mainWindow().statusBar().showMessage(text)
