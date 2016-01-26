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

from PyQt4.QtCore import Qt, QDateTime, QRegExp

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

# List/Range conversion utilities

def rangeToList(self, valueRange):
    lst = []
    for clause in valueRange.split():
        if clause.find('-') >= 0:
            valueList = clause.split('-')
            for i in range(int(valueList[0]), int(valueList[1])):
                lst.append(i)
        else:
            lst.append(int(clause))
    return sorted(lst)

def listToRange(self, valueList):
    inList = sorted(set(valueList))
    valueRange = ''
    if len(inList) == 0:
        return valueRange
    prev = inList[0]
    start = prev
    for this in inList[1:]:
        if int(this) != int(prev) + 1:
            if prev == start:
                valueRange = valueRange + ' ' + str(prev)
            else:
                valueRange = valueRange + ' ' + str(start) + '-' + str(this)
            start = this
        prev = this
    if prev == start:
        valueRange = valueRange + ' ' + str(prev)
    else:
        valueRange = valueRange + ' ' + str(start) + '-' + str(this)
    return valueRange

def listToRegExp(self, lst):
    if (len(lst) < 1):
        return QRegExp()
    exp = str(lst[0])
    if (len(lst) > 1):
        for element in lst[1:]:
            exp = exp + '|' + str(element)
    return QRegExp('\\b(' + exp + ')\\b')

# Message utilities

def showMessage(iface, text, level=QgsMessageBar.INFO, duration=0):
    iface.messageBar().pushMessage(text, level, duration)

def showCriticalMessage(iface, text, duration=0):
    iface.messageBar().pushMessage(text, QgsMessageBar.CRITICAL, duration)

def showStatusMessage(iface, text):
    iface.mainWindow().statusBar().showMessage(text)
