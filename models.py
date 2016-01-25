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

import csv

from PyQt4.QtCore import Qt, QAbstractTableModel, QModelIndex

class TableModel(QAbstractTableModel):

    _table = []
    _fields = []
    _nullRecord = {}

    def __init__(self, fields=[], nullRecord={}, parent=None):
        super(QAbstractTableModel, self).__init__(parent)
        self._fields = fields
        self._nullRecord = nullRecord
        self._table = []

    def rowCount(self):
        return len(self._table)

    def columnCount(self):
        return len(self._fields)

    def data(self, index, role):
        if (role != Qt.DisplayRole):
            return None
        if (not index.isValid() or index.row() < 0 or index.row() > len(self._table)):
            return self._nullRecord[self._fields[index.column()]]
        record = self._table[index.row()]
        data = record[self._fields[index.column()]]
        return data

    def headerData(self, section, orientation, role):
        if (role != Qt.DisplayRole):
            return None
        if (orientation == Qt.Horizontal):
            return self._fields[section]
        return ''

    def insertRows(self, position, rows, parent=QModelIndex()):
        beginInsertRows(QModelIndex(), position, position + rows - 1)
        for row in range(0, rows - 1):
            self._table.insert(position, self._nullRecord)
        endInsertRows()
        return True

    def removeRows(self, position, rows, parent=QModelIndex()):
        beginRemoveRows(QModelIndex(), position, position + rows - 1)
        for row in range(position + rows - 1, position):
            del self._table[row]
        endRemoveRows()
        return true

    def setData(self, index, value, role=Qt.EditRole):
        if (not index.isValid() or role != Qt.EditRole):
            return False
        record = self._table[index.row()]
        record[self._fields[index.column()]] = value
        return True

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return super(QAbstractTableModel, self).flags(index) | Qt.ItemIsEditable

    def getList(self):
        return self._table

    def getRecord(self, key, value):
        for record in self._table:
            if record[key] == value:
                return record

    def getRecords(self, key, value):
        results = []
        for record in self._table:
            if record[key] == value:
                results.append(record)
        return results

    def deleteRecords(self, key, value):
        for record in self._table:
            if record[key] == value:
                self._table.remove(record)

    def clear(self):
        self._table = []


class ParentChildModel(TableModel):

    def __init__(self, parent=None):
        super(TableModel, self).__init__(parent)
        self._fields = ['parent', 'child']
        self._nullRecord = {'parent' : None, 'child' : None}

    def addChild(self, parent, child):
        self.deleteRecords('child', child)
        record = {'parent' : parent, 'child' : child}
        self._table.append(record)

    def getChildren(self, parent):
        children = []
        for record in self._table:
            if record['parent'] == parent:
                children.append(record['child'])
        return children

    def getParent(self, child):
        for record in self._table:
            if record['child'] == child:
                return record['parent']
        return None
