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

from qgis.core import QGis, QgsProject

# Project setting utilities

class Project:

    @staticmethod
    def crs(iface):
        if QGis.QGIS_VERSION_INT >= 20400:
            return iface.mapCanvas().mapSettings().destinationCrs()
        else:
            return iface.mapCanvas().mapRenderer().destinationCrs()

    @staticmethod
    def setEntry(scope, key, value, default=None):
        if (value == None or value == '' or value == default):
            return QgsProject.instance().removeEntry(scope, key)
        else:
            return QgsProject.instance().writeEntry(scope, key, value)

    @staticmethod
    def removeEntry(scope, key):
        return QgsProject.instance().removeEntry(scope, key)

    @staticmethod
    def writeEntry(scope, key, value):
        return QgsProject.instance().writeEntry(scope, key, value)

    @staticmethod
    def readEntry(scope, key, default=''):
        ret = QgsProject.instance().readEntry(scope, key, default)
        if ret is None or not ret[1]:
            return default
        else:
            return ret[0]

    @staticmethod
    def readNumEntry(scope, key, default=0):
        ret = QgsProject.instance().readNumEntry(scope, key, default)
        if ret is None or not ret[1]:
            return default
        else:
            return ret[0]

    @staticmethod
    def readDoubleEntry(scope, key, default=0.0):
        ret = QgsProject.instance().readDoubleEntry(scope, key, default)
        if ret is None or not ret[1]:
            return default
        else:
            return ret[0]

    @staticmethod
    def readBoolEntry(scope, key, default=False):
        ret = QgsProject.instance().readBoolEntry(scope, key, default)
        if ret is None or not ret[1]:
            return default
        else:
            return ret[0]

    @staticmethod
    def readListEntry(scope, key, default=[]):
        return QgsProject.instance().readListEntry(scope, key, default)
