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
        copyright            : 2013 by Piotr Pociask
        copyright            : 2013 by Victor Olaya
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
from qgis.core import QgsFeature, QgsGeometry

from shapely.ops import polygonize, unary_union
from shapely.geometry import MultiLineString

# Adapted from QGIS Processing plugin Polygonize by Piotr Pociask
def polygonizeFeatures(features, fields=None):
    allLinesList = []
    for inFeat in features:
        inGeom = inFeat.geometry()
        if inGeom is None:
            pass
        elif inGeom.isMultipart():
            allLinesList.extend(inGeom.asMultiPolyline())
        else:
            allLinesList.append(inGeom.asPolyline())
    allLines = MultiLineString(allLinesList)
    allLines = unary_union(allLines)
    polygons = list(polygonize([allLines]))
    outList = []
    for polygon in polygons:
        outFeat = QgsFeature(fields)
        outFeat.setGeometry(QgsGeometry.fromWkt(polygon.wkt))
        outList.append(outFeat)
    return outList

# Adapted from QGIS Processing plugin Dissolve by Victor Olaya
def dissolveFeatures(features, fields=None, attributes=None):
    outFeat = QgsFeature(fields)
    first = True
    for inFeat in features:
        if first:
            tmpInGeom = QgsGeometry(inFeat.geometry())
            outFeat.setGeometry(tmpInGeom)
            first = False
        else:
            tmpInGeom = QgsGeometry(inFeat.geometry())
            tmpOutGeom = QgsGeometry(outFeat.geometry())
            try:
                tmpOutGeom = QgsGeometry(tmpOutGeom.combine(tmpInGeom))
                outFeat.setGeometry(tmpOutGeom)
            except:
                pass
    if attributes is not None:
        outFeat.setAttributes(attributes)
    return outFeat
