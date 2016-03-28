# -*- coding: utf-8 -*-
"""
/***************************************************************************
                                ARK QGIS
                        A QGIS utilities library.
        Part of the Archaeological Recording Kit by L-P : Archaeology
                        http://ark.lparchaeology.com
                              -------------------
        begin                : 2016-03-26
        git sha              : $Format:%H$
        copyright            : 2014, 2015 by L-P : Heritage LLP
        email                : ark@lparchaeology.com
        copyright            : 2014, 2015 by John Layt
        email                : john@layt.net
        copyright            : 2011 by Jürgen E. Fischer
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

from PyQt4.QtCore import Qt, QSize
from PyQt4.QtGui import QPolygonF, QBrush, QColor, QPen, QPainter, QPainterPath, QImage, qAlpha, qGreen

from qgis.core import QGis, QgsPoint, QgsRectangle, QgsFeature, QgsGeometry, QgsRenderContext, QgsSymbolV2, QgsSimpleMarkerSymbolLayerV2
from qgis.gui import QgsMapCanvasItem

import utils
from project import Project

# Code ported from QGIS QgsHighlight

class FeatureHighlight(QgsMapCanvasItem):

    _mapCanvas = None  # QgsMapCanvas
    _brush = QBrush()
    _pen = QPen()
    _feature = None  # QgsFeature()
    _layer = None  # QgsMapLayer()
    _buffer = 0.0
    _minWidth = 0.0

    def __init__(self, mapCanvas, feature, layer):
        super(FeatureHighlight, self).__init__(mapCanvas)
        if not layer or not feature or not isinstance(feature, QgsFeature) or not feature.geometry() or feature.geometry().isEmpty() or not feature.geometry().isGeosValid():
            return
        self._mapCanvas = mapCanvas
        self._feature = QgsFeature(feature) # Force deep copy
        self._layer = layer
        self.setLineColor(Project.highlightLineColor())
        self.setFillColor(Project.highlightFillColor())
        self._minWidth = Project.highlightMinimumWidth()
        self._buffer = Project.highlightBuffer()
        if self._mapCanvas.mapSettings().hasCrsTransformEnabled():
            ct = self._mapCanvas.mapSettings().layerTransform(self._layer)
            self._feature.geometry().transform(ct)
        self.updateRect()
        self.update()

    def remove(self):
        self._mapCanvas.scene().removeItem(self)

    def setLineWidth(self, width):
        self._pen.setWidth(width)

    def setLineColor(self, color):
        self._pen.setColor(color)

    def setFillColor(self, fillColor):
        self._brush.setColor(fillColor)
        self._brush.setStyle(Qt.SolidPattern)

    def setBuffer(self, buff):
        self._buffer = buff

    def setMinWidth(self, width):
        self._minWidth = width

    def layer(self):
        return self._layer

    def updatePosition(self):
        pass

    # protected:
    def paint(self, painter, option=None, widget=None): # Override
        if not self._feature:
            return

        mapSettings = self._mapCanvas.mapSettings()
        context = QgsRenderContext.fromMapSettings(mapSettings)
        renderer = self._getRenderer(context, self._pen.color(), self._brush.color())

        if renderer:
            context.setPainter(painter)
            renderer.startRender(context, self._layer.fields())
            renderer.renderFeature(self._feature, context)
            renderer.stopRender(context)

    def updateRect(self):
        if self._feature and self._feature.constGeometry():
            m2p = self._mapCanvas.mapSettings().mapToPixel()
            topLeft = m2p.toMapPoint(0, 0)
            res = m2p.mapUnitsPerPixel()
            imageSize = self._mapCanvas.mapSettings().outputSize()
            rect = QgsRectangle(topLeft.x(), topLeft.y(),topLeft.x() + imageSize.width()*res, topLeft.y() - imageSize.height()*res)
            self.setRect(rect)
            self.setVisible(True)
        else:
            self.setRect(QgsRectangle())

    # private:
    def _setSymbol(self, symbol, context, color, fillColor):
        if  not symbol:
            return

        for symbolLayer in reversed(symbol.symbolLayers()):
            if symbolLayer:
                if symbolLayer.subSymbol():
                    self._setSymbol(symbolLayer.subSymbol(), context, color, fillColor)
                else:
                    symbolLayer.setColor(color)
                    symbolLayer.setOutlineColor(color)
                    symbolLayer.setFillColor(fillColor)
                    if isinstance(symbolLayer, QgsSimpleMarkerSymbolLayerV2):
                        symbolLayer.setOutlineWidth(self._getSymbolWidth(context, symbolLayer.outlineWidth(), symbolLayer.outlineWidthUnit()))
                    if symbolLayer.type() == QgsSymbolV2.Line:
                        symbolLayer.setWidth(self._getSymbolWidth(context, symbolLayer.width(), symbolLayer.widthUnit()))
                    if symbolLayer.type() == QgsSymbolV2.Fill:
                        symbolLayer.setBorderWidth(self._getSymbolWidth(context, symbolLayer.borderWidth(), symbolLayer.outputUnit()))
                    symbolLayer.removeDataDefinedProperty('color')
                    symbolLayer.removeDataDefinedProperty('color_border')

    def _getSymbolWidth(self, context, width, unit):
        scale = 1.0
        if unit == QgsSymbolV2.MapUnit:
            scale = QgsSymbolLayerV2Utils.lineWidthScaleFactor(context, QgsSymbolV2.MM) / QgsSymbolLayerV2Utils.lineWidthScaleFactor(context, QgsSymbolV2.MapUnit)
        width =  max(width + 2 * self._buffer * scale, self._minWidth * scale)
        return width

    def _getRenderer(self, context, color, fillColor):
        renderer = None
        if self._layer and self._layer.rendererV2():
            renderer = self._layer.rendererV2().clone()
        if renderer:
            for symbol in renderer.symbols2(context):
                self._setSymbol(symbol, context, color, fillColor)
        return renderer


class GeometryHighlight(QgsMapCanvasItem):

    _mapCanvas = None  # QgsMapCanvas
    _geometry = None  # QgsGeometry()
    _brush = QBrush()
    _pen = QPen()

    def __init__(self, mapCanvas, geometry, layer):
        super(GeometryHighlight, self).__init__(mapCanvas)
        self._mapCanvas = mapCanvas
        if not geometry or not isinstance(geometry, QgsGeometry) or geometry.isEmpty() or not geometry.isGeosValid():
            return
        self._geometry = QgsGeometry(geometry) # Force deep copy
        self.setLineColor(Project.highlightLineColor())
        self.setFillColor(Project.highlightFillColor())
        if (layer and self._mapCanvas.mapSettings().hasCrsTransformEnabled()):
            ct = self._mapCanvas.mapSettings().layerTransform(layer)
            if ct:
                self._geometry.transform(ct)
        self.updateRect()
        self.update()

    def remove(self):
        self._mapCanvas.scene().removeItem(self)

    def setLineWidth(self, width):
        self._pen.setWidth(width)

    def setLineColor(self, color):
        lineColor = QColor(color)
        lineColor.setAlpha(255)
        self._pen.setColor(lineColor)

    def setFillColor(self, fillColor):
        self._brush.setColor(fillColor)
        self._brush.setStyle(Qt.SolidPattern)

    def updatePosition(self):
        pass

    # protected:
    def paint(self, painter, option=None, widget=None): # Override
        if not self._geometry:
            return

        painter.setPen(self._pen)
        painter.setBrush(self._brush)

        wkbType = self._geometry.wkbType()
        if wkbType == QGis.WKBPoint or wkbType == QGis.WKBPoint25D:
            self._paintPoint(painter, self._geometry.asPoint())
        elif wkbType == QGis.WKBMultiPoint or wkbType == QGis.WKBMultiPoint25D:
            for point in self._geometry.asMultiPoint():
                self._paintPoint(painter, point)
        elif wkbType == QGis.WKBLineString or wkbType == QGis.WKBLineString25D:
            self._paintLine(painter, self._geometry.asPolyline())
        elif wkbType == QGis.WKBMultiLineString or wkbType == QGis.WKBMultiLineString25D:
            for line in self._geometry.asMultiPolyline():
                self._paintLine(painter, line)
        elif wkbType == QGis.WKBPolygon or wkbType == QGis.WKBPolygon25D:
            self._paintPolygon(painter, self._geometry.asPolygon())
        elif wkbType == QGis.WKBMultiPolygon or wkbType == QGis.WKBMultiPolygon25D:
            for polygon in self._geometry.asMultiPolygon():
                self._paintPolygon(painter, polygon)

    def updateRect(self):
        if self._geometry:
            r = self._geometry.boundingBox()
            if r.isEmpty():
                d = self._mapCanvas.extent().width() * 0.005
                r.setXMinimum(r.xMinimum() - d)
                r.setYMinimum(r.yMinimum() - d)
                r.setXMaximum(r.xMaximum() + d)
                r.setYMaximum(r.yMaximum() + d)
            self.setRect(r)
            self.setVisible(True)
        else:
            self.setRect(QgsRectangle())

    # private:

    def _paintPoint(self, painter, point):
        painter.drawEllipse(self.toCanvasCoordinates(point) - self.pos(), 2, 2)

    def _paintLine(self, painter, line):
        polyline = QPolygonF()
        for point in line:
            polyline.append(self.toCanvasCoordinates(point) - self.pos())
        painter.drawPolyline(polyline)

    def _paintPolygon(self, painter, polygon):
        path = QPainterPath()
        for line in polygon:
            ring = QPolygonF()
            for point in line:
                cur = self.toCanvasCoordinates(point) - self.pos()
                ring.append(cur)
            ring.append(ring[0])
            path.addPolygon(ring)
        painter.drawPath(path)
