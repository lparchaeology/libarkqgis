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

from PyQt4.QtCore import Qt, QDateTime

from qgis.core import QGis, QgsProject
from qgis.gui import QgsMessageBar

# Datetime utilities

def timestamp():
    return QDateTime.currentDateTimeUtc().toString(Qt.ISODate)

# String utilities

def quote(val):
    return "'" + str(val) + "'"

def doublequote(val):
    return '"' + str(val) + '"'

def eqClause(field, value):
    return doublequote(field) + ' = ' + quote(value)

def neClause(field, value):
    return doublequote(field) + ' != ' + quote(value)

# Message utilities

def showMessage(iface, text, level=QgsMessageBar.INFO, duration=0):
    iface.messageBar().pushMessage(text, level, duration)

def showCriticalMessage(iface, text, duration=0):
    iface.messageBar().pushMessage(text, QgsMessageBar.CRITICAL, duration)

def showStatusMessage(iface, text):
    iface.mainWindow().statusBar().showMessage(text)
