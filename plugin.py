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

import os.path

from PyQt4.QtCore import Qt, QObject, QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon

from qgis.core import QGis, QgsProject, QgsMessageLog
from qgis.gui import QgsMessageBar

from project import Project

# Initialize Qt resources from file resources.py
import resources

class Plugin(QObject):
    """QGIS Plugin Base Class."""

    # InterfaceGroup enum
    OwnGroup = 0
    PluginsGroup = 1
    DatabaseGroup = 2
    RasterGroup = 3
    VectorGroup = 4
    WebGroup = 5

    # Public variables
    iface = None  # QgsInteface()
    pluginAction = None # QAction()
    pluginName = ''
    pluginPath = ''
    pluginIconPath = ''
    displayName = ''

    # Private variables
    _actions = []
    _checkable = False
    _menuGroup = 0  # MenuType
    _menu = None # QMenu()
    _toolbarGroup = 0  # MenuType
    _toolbar = None  # QToolBar()

    def __init__(self, iface, pluginName, pluginIconPath, pluginPath,
                 menuGroup=PluginsGroup, toolbarGroup=PluginsGroup, checkable=False, parent=None):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface

        :param pluginName: Untranslated name of the plugin.
        :type pluginName: str

        :param pluginPath: The plugin directory.
        :type pluginPath: str

        :param pluginIconPath: Plugin icon path, either file or resource.
        :type pluginIconPath: str

        :param menuGroup: The menu group to add the plugin to.
        :type menuGroup: int

        :param toolbarGroup: The toolbar group to add the plugin to.
        :type toolbarGroup: int

        :param checkable: If the plugin action is checkable, set to True for a dock or map tool, set to False for a dialog or single-shot function.
        :type checkable: bool
        """
        super(Plugin, self).__init__(parent)
        self.iface = iface
        self.pluginName = pluginName
        self.pluginPath = pluginPath
        self.pluginIconPath = pluginIconPath
        self._menuGroup = menuGroup
        self._toolbarGroup = toolbarGroup
        self._checkable = checkable

        # initialize translation
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(self.pluginPath, 'i18n', self.pluginName + '_{}.qm'.format(locale))
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

    def setDisplayName(self, name):
        """Set the translated display to be used in the menu and elsewhere
        :param name: Translated plugin name.
        :type name: str
        """
        self.displayName = name

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        # Reimplement and call in inplementation

        # Unload in case plugin crash durign reload left remnants behind
        Plugin.unload(self)

        if self._menuGroup == Plugin.OwnGroup:
            self._menu = self.iface.mainWindow().menuBar().addMenu(self.pluginName)
            self._menu.setObjectName(self.pluginName)
        if self._toolbarGroup == Plugin.OwnGroup:
            self._toolbar = self.iface.addToolBar(self.pluginName)
            self._toolbar.setObjectName(self.pluginName)

        self.pluginAction = self.addNewAction(self.pluginIconPath, self.displayName, callback=self.run, checkable=self._checkable)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        # Reimplement and call in inplementation
        for action in self._actions:

            if self._menuGroup == Plugin.OwnGroup or self._menuGroup == Plugin.PluginsGroup:
                self.iface.removePluginMenu(self.displayName, action)
            elif self._menuGroup == Plugin.DatabaseMenu:
                self.iface.removePluginDatabaseMenu(self.displayName, action)
            elif self._menuGroup == Plugin.RasterMenu:
                self.iface.removePluginRasterMenu(self.displayName, action)
            elif self._menuGroup == Plugin.VectorMenu:
                self.iface.removePluginVectorMenu(self.displayName, action)
            elif self._menuGroup == Plugin.WebMenu:
                self.iface.removePluginWebMenu(self.displayName, action)

            if self._toolbarGroup == Plugin.OwnGroup:
                self._toolbar.removeAction(action)
            elif self._toolbarGroup == Plugin.PluginsGroup:
                self.iface.removeToolBarIcon(action)
            elif self._toolbarGroup == Plugin.DatabaseMenu:
                self.iface.removeDatabaseToolBarIcon(action)
            elif self._toolbarGroup == Plugin.RasterMenu:
                self.iface.removeRasterToolBarIcon(action)
            elif self._toolbarGroup == Plugin.VectorMenu:
                self.iface.removeVectorToolBarIcon(action)
            elif self._toolbarGroup == Plugin.WebMenu:
                self.iface.removeWebToolBarIcon(action)

        # remove the menu
        if self._menu:
            del self._menu
        # remove the toolbar
        if self._toolbar:
            del self._toolbar

    def run(self):
        """Run method that performs all the real work"""
        # Reimplement in inplementation
        pass

    def addNewAction(
        self,
        iconPath,
        text,
        callback=None,
        enabled=True,
        checkable=False,
        addToMenu=True,
        addToToolbar=True,
        tip=None,
        whatsThis=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param iconPath: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type iconPath: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled: bool

        :param checkable: A flag indicating if the action should be checkable
            by default. Defaults to False.
        :type chenckable: bool

        :param addToMenu: Flag indicating whether the action should also
            be added to the plugin menu. Defaults to True.
        :type addToMenu: bool

        :param addToToolbar: Flag indicating whether the action should also
            be added to the plugin toolbar. Defaults to True.
        :type addToToolbar: bool

        :param tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type tip: str

        :param whatsThis: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :returns: The action that was created. Note that the action is also
            added to self._actions list.
        :rtype: QAction
        """

        if parent is None:
            parent = self.iface.mainWindow()
        action = QAction(QIcon(iconPath), text, parent)
        if tip is not None:
            action.setStatusTip(tip)
        if whatsThis is not None:
            action.setWhatsThis(whatsThis)

        if callback is not None:
            action.triggered.connect(callback)
        action.setEnabled(enabled)
        action.setCheckable(checkable)

        self.addAction(action, addToMenu, addToToolbar)
        return action

    def addAction(self, action, addToMenu=True, addToToolbar=True):
        """Add an action to the menu and/or toolbar.
           Note that the action is also added to self._actions list.

        :param action: QAction that should be added
        :type text: QAction

        :param addToMenu: Flag indicating whether the action should also
            be added to the plugin menu. Defaults to True.
        :type addToMenu: bool

        :param addToToolbar: Flag indicating whether the action should also
            be added to the plugin toolbar. Defaults to True.
        :type addToToolbar: bool

        :returns: The action that was created.
        :rtype: QAction
        """

        if addToToolbar:
            if self._toolbarGroup == Plugin.OwnGroup:
                self._toolbar.addAction(action)
            elif self._toolbarGroup == Plugin.PluginsGroup:
                self.iface.addToolBarIcon(action)
            elif self._toolbarGroup == Plugin.DatabaseMenu:
                self.iface.addDatabaseToolBarIcon(action)
            elif self._toolbarGroup == Plugin.RasterMenu:
                self.iface.addRasterToolBarIcon(action)
            elif self._toolbarGroup == Plugin.VectorMenu:
                self.iface.addVectorToolBarIcon(action)
            elif self._toolbarGroup == Plugin.WebMenu:
                self.iface.addWebToolBarIcon(action)

        if addToMenu:
            if self._menuGroup == Plugin.OwnGroup:
                self._menu.addAction(action)
            elif self._menuGroup == Plugin.PluginsGroup:
                self.iface.addPluginToMenu(self.displayName, action)
            elif self._menuGroup == Plugin.DatabaseMenu:
                self.iface.addPluginToDatabaseMenu(self.displayName, action)
            elif self._menuGroup == Plugin.RasterMenu:
                self.iface.addPluginToRasterMenu(self.displayName, action)
            elif self._menuGroup == Plugin.VectorMenu:
                self.iface.addPluginToVectorMenu(self.displayName, action)
            elif self._menuGroup == Plugin.WebMenu:
                self.iface.addPluginToWebMenu(self.displayName, action)

        self._actions.append(action)

    # Convenience logging functions

    def logCriticalMessage(self, text):
        self.logMessage(text, QgsMessageLog.CRITICAL)

    def logWarningMessage(self, text):
        self.logMessage(text, QgsMessageLog.WARNING)

    def logInfoMessage(self, text):
        self.logMessage(text, QgsMessageLog.INFO)

    def logMessage(self, text, level=QgsMessageLog.INFO):
        QgsMessageLog.logMessage(text, self.pluginName, level)

    def showCriticalMessage(self, text, duration=5):
        self.showMessage(text, QgsMessageBar.CRITICAL, duration)

    def showWarningMessage(self, text, duration=5):
        self.showMessage(text, QgsMessageBar.WARNING, duration)

    def showInfoMessage(self, text, duration=5):
        self.showMessage(text, QgsMessageBar.INFO, duration)

    def showMessage(self, text, level=QgsMessageBar.INFO, duration=5):
        self.iface.messageBar().pushMessage(text, level, duration)

    def showStatusMessage(self, text):
        utils.showStatusMessage(self.iface, text)

    # Project utilities

    def projectCrs(self):
        return Project.crs(self.iface)

    # Settings utilities

    def setEntry(self, key, value, default=None):
        return Project.setEntry(self.pluginName, key, value, default)

    def removeEntry(self, key):
        return Project.removeEntry(self.pluginName, key)

    def writeEntry(self, key, value):
        return Project.writeEntry(self.pluginName, key, value)

    def readEntry(self, key, default=''):
        return Project.readEntry(self.pluginName, key, default)

    def readNumEntry(self, key, default=0):
        return Project.readNumEntry(self.pluginName, key, default)

    def readDoubleEntry(self, key, default=0.0):
        return Project.readDoubleEntry(self.pluginName, key, default)

    def readBoolEntry(self, key, default=False):
        return Project.readBoolEntry(self.pluginName, key, default)

    def readListEntry(self, key, default=[]):
        return Project.readListEntry(self.pluginName, key, default)

    # QgsInterface utilities

    def mapCanvas(self):
        return self.iface.mapCanvas()

    def legendInterface(self):
        return self.iface.legendInterface()

# Template implementation classes, copy one of these into your main plugin file

class MyPlugin(Plugin):
    """QGIS Plugin Implementation for dialog or single-shot process."""

    def __init__(self, iface):
        super(MyPlugin, self).__init__(iface, u'MyPlugin', ':/plugins/MyPlugin/icon.png', os.path.dirname(__file__),
                                       Plugin.PluginsGroup, Plugin.PluginsGroup)
        # Set display / menu name now we have tr() set up
        self.setDisplayName(self.tr(u'&MyPlugin'))

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        super(MyPlugin, self).initGui()

        # Connect a simple button and menu item to your main action

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        # Destroy/disable any plugin objects here
        super(MyPlugin, self).unload()

    def run(self):
        """Run method when plugin action triggered"""
        pass


class MyDockPlugin(Plugin):
    """QGIS Plugin Implementation for dock."""

    def __init__(self, iface):
        super(MyPlugin, self).__init__(iface, u'MyDockPlugin', ':/plugins/MyPlugin/icon.png', os.path.dirname(__file__),
                                       Plugin.PluginsGroup, Plugin.PluginsGroup, checkable=True)
        # Set display / menu name now we have tr() set up
        self.setDisplayName(self.tr(u'&MyPlugin'))

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        super(MyPlugin, self).initGui()

        self.dock = MyDock()  # Your dock implementation derived from ArkDockWidget
        self.dock.load(self.iface, Qt.LeftDockWidgetArea, self.pluginAction)
        self.dock.someSignal.connect(self.someMethod)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        # Destroy/disable any plugin objects here
        self.dock.unload()
        super(MyPlugin, self).unload()

    def run(self, checked):
        """Run method when dock toggled"""
        if checked:
            pass
