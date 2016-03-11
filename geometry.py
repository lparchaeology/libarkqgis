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
        copyright            : 2014, 2015, 2016 by L-P : Heritage LLP
        email                : ark@lparchaeology.com
        copyright            : 2014, 2015, 2016 by John Layt
        email                : john@layt.net
        copyright            : 2014 by Olivier Dalang
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
import math

from qgis.core import QGis, QgsFeature, QgsGeometry, QgsPointV2

from shapely.ops import polygonize, unary_union
from shapely.geometry import LineString, MultiLineString, Point

# Based on LinearTransformer code from VectorBender plugin
# (C) 2014 by Olivier Dalang
class LinearTransformer():

    def __init__(self, a1, b1, a2, b2):
        #scale
        self.ds = math.sqrt((b2.x() - b1.x()) ** 2.0 + (b2.y() - b1.y()) ** 2.0) / math.sqrt((a2.x() - a1.x()) ** 2.0 + (a2.y() - a1.y()) ** 2.0)
        #rotation
        self.da =  math.atan2(b2.y() - b1.y(), b2.x() - b1.x()) - math.atan2(a2.y() - a1.y(), a2.x() - a1.x() )
        #translation
        self.dx1 = a1.x()
        self.dy1 = a1.y()
        self.dx2 = b1.x()
        self.dy2 = b1.y()

    def map(self, p):
        #move to origin (translation part 1)
        p = QgsPointV2( p.x()-self.dx1, p.y()-self.dy1 )
        #scale
        p = QgsPointV2( self.ds*p.x(), self.ds*p.y() )
        #rotation
        p = QgsPointV2(math.cos(self.da) * p.x() - math.sin(self.da) * p.y(), math.sin(self.da) * p.x() + math.cos(self.da) * p.y())
        #remove to right spot (translation part 2)
        p = QgsPointV2(p.x() + self.dx2, p.y() + self.dy2)

        return p

# Adapted from QGIS Processing plugin Polygonize by Piotr Pociask
def polygonizeFeatures(features, fields=None):
    lineList = []
    for inFeat in features:
        inGeom = inFeat.geometry()
        if inGeom is None:
            pass
        elif inGeom.isMultipart():
            lineList.extend(inGeom.asMultiPolyline())
        else:
            lineList.append(inGeom.asPolyline())
    allLines = MultiLineString(lineList)
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

# Returns a point on the given line that is perpendicular to the given point
def perpendicularPoint(lineGeometry, point):
    # In 2.14 use QgsGeometry.nearestPoint()
    # In 2.10 use QgsGeometry.isEmpty()
    if lineGeometry is None or lineGeometry.isGeosEmpty() or point is None:
        return QgsPointV2()
    line = toMultiLineString(lineGeometry)
    perp = line.interpolate(line.project(Point(point)))
    return QgsPointV2(perp.x, perp.y)

# Returns a line cliipped to the extent of two given points
# Assumes pt1, pt2 lie on line
def clipLine(lineGeometry, pt1, pt2):
    if lineGeometry is None or lineGeometry.isGeosEmpty() or pt1 is None or pt2 is None:
        return QgsGeometry()
    line = LineString(lineGeometry.asPolyline())
    d1 = line.project(Point(pt1))
    d2 = line.project(Point(pt2))
    if d1 < d2:
        start = pt1
        ds = d1
        end = pt2
        de = d2
    else:
        start = pt2
        ds = d2
        end = pt1
        de = d1
    clip = []
    clip.append(start)
    for coord in line.coords:
        pt = Point(coord)
        dp = line.project(pt)
        if dp > ds and dp < de:
            clip.append(QgsPointV2(pt.x, pt.y))
    clip.append(end)
    return QgsGeometry.fromPolyline(clip)

def toMultiLineString(lineGeometry):
    lineList = []
    if lineGeometry.isMultipart():
        lineList.extend(lineGeometry.asMultiPolyline())
    else:
        lineList.append(lineGeometry.asPolyline())
    return MultiLineString(lineList)
