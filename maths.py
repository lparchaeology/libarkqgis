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

import math

from qgis.core import QgsPoint

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
        p = QgsPoint( p.x()-self.dx1, p.y()-self.dy1 )
        #scale
        p = QgsPoint( self.ds*p.x(), self.ds*p.y() )
        #rotation
        p = QgsPoint(math.cos(self.da) * p.x() - math.sin(self.da) * p.y(), math.sin(self.da) * p.x() + math.cos(self.da) * p.y())
        #remove to right spot (translation part 2)
        p = QgsPoint(p.x() + self.dx2, p.y() + self.dy2)

        return p
