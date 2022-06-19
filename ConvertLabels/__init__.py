# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Convert Labels
                                 A QGIS plugin
 Converts labels to layers for annotation
                             -------------------
        begin                : 2022-05-25
        copyright            : (C) 2022 by Tarot Osuji
        email                : tarot@sdf.org
        git sha              : $Format:%H$
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

import os
from qgis.PyQt.QtCore import QObject, QTranslator, QLocale
from qgis.PyQt.QtWidgets import qApp, QAction
from qgis.core import Qgis, QgsApplication, QgsMapLayer, QgsProject
from .ui import ConvertLabelsDialog
from .toPoint import convertToPoint
if Qgis.QGIS_VERSION_INT >= 31600:
    from .toAnnotation import convertToAnnotation


class ConvertLabels(QObject):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.translator = QTranslator()
        if self.translator.load(QLocale(QgsApplication.locale()),
                '', '', os.path.join(os.path.dirname(__file__), 'i18n')):
            qApp.installTranslator(self.translator)

    def initGui(self):
        self.plugin_name = self.tr('Convert Labels')
        self.plugin_act = QAction(self.plugin_name + self.tr('…'))
        self.plugin_act.triggered.connect(self.run)
        self.iface.addCustomActionForLayerType(self.plugin_act, None,
                QgsMapLayer.VectorLayer, True)

        self.dialog = ConvertLabelsDialog(parent=self.iface.mainWindow())
        self.dialog.setWindowTitle(self.plugin_name)
        self.iface.newProjectCreated.connect(self.slot_projectRead)
        self.iface.projectRead.connect(self.slot_projectRead)
        self.slot_projectRead()

    def unload(self):
        self.iface.removeCustomActionForLayerType(self.plugin_act)

    def slot_projectRead(self):
        prjpath = QgsProject.instance().fileName()
        self.dialog.leditFile.setText(
                os.path.splitext(prjpath)[0] + '_Label.gpkg')

    def run(self):
        current_layer = self.iface.activeLayer()
        if not current_layer.labelsEnabled():
            self.iface.messageBar().pushInfo(self.plugin_name,
                    self.tr('Labels are not enabled'))
            return

        self.dialog.leditLayer.setText(current_layer.name() + '_Label')
        is_selected = bool(current_layer.selectedFeatureCount())
        self.dialog.checkSelected.setEnabled(is_selected)
        self.dialog.checkSelected.setChecked(is_selected)

        if not self.dialog.exec():
            return

        if self.dialog.radio1.isChecked():
            convertToPoint(self)
        else:
            convertToAnnotation(self)


def classFactory(iface):
    return ConvertLabels(iface)
