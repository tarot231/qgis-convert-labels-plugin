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

from qgis.PyQt.QtGui import QFont, QFontMetrics, QIcon
from qgis.PyQt.QtWidgets import *
from qgis.core import Qgis, QgsMapLayerProxyModel
from qgis.gui import QgsMapLayerComboBox


class ConvertLabelsDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fontsize = QFontMetrics(QFont()).height()

        self.radio1 = QRadioButton(
                self.tr('Point Vector Layer for Labels'))
        self.radio2 = QRadioButton(
                self.tr('Text at Point on Annotation Layer'))
        self.radios = QButtonGroup()
        self.radios.addButton(self.radio1)
        self.radios.addButton(self.radio2)
        self.radio1.setChecked(True)

        self.leditFile = QLineEdit()
        self.leditFile.setReadOnly(True)
        self.leditFile.setMinimumWidth(fontsize * 20)
        self.buttonFile = QToolButton()
        self.buttonFile.setIcon(
                QIcon(':/images/themes/default/mActionFileOpen.svg'))
        self.buttonFile.clicked.connect(self.buttonFile_clicked)
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.leditFile)
        hbox1.addWidget(self.buttonFile)

        self.leditLayer = QLineEdit()
        self.checkOverwrite = QCheckBox(self.tr('Overwrite'))
        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.leditLayer)
        hbox2.addWidget(self.checkOverwrite)

        if Qgis.QGIS_VERSION_INT >= 32200:
            self.comboLayer = QgsMapLayerComboBox()
            self.comboLayer.setFilters(QgsMapLayerProxyModel.AnnotationLayer)
            self.comboLayer.setAllowEmptyLayer(True,
                    self.tr('Main Annotation Layer'),
                    QIcon(':/images/themes/default/mIconAnnotationLayer.svg'))
        else:
            self.comboLayer = QComboBox()
            if Qgis.QGIS_VERSION_INT >= 31600:
                self.comboLayer.addItem(self.tr('Main Annotation Layer'))

        grid = QGridLayout()
        grid.addWidget(self.radio1, 0, 0, 1, -1)
        grid.addWidget(QLabel(self.tr('GeoPackage file name')), 1, 1)
        grid.addLayout(hbox1, 1, 2)
        grid.addWidget(QLabel(self.tr('GeoPackage layer name')), 2, 1)
        grid.addLayout(hbox2, 2, 2)
        grid.addWidget(self.radio2, 3, 0, 1, -1)
        self.labelAnno = QLabel(self.tr('Annotation layer'))
        grid.addWidget(self.labelAnno, 4, 1)
        grid.addWidget(self.comboLayer, 4, 2)
        grid.setColumnMinimumWidth(0, QRadioButton().sizeHint().width())

        self.checkSelected = QCheckBox(self.tr('Selected features only'))

        group = QGroupBox(self.tr('Convert To'))
        group.setLayout(grid)

        buttonBox = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        vbox = QVBoxLayout()
        vbox.addWidget(group)
        vbox.addWidget(self.checkSelected)
        vbox.addWidget(buttonBox)

        self.setLayout(vbox)
        self.setMaximumHeight(0)

        if Qgis.QGIS_VERSION_INT < 32200:  # <3.22 is not practica
            self.radio2.setEnabled(False)
            self.labelAnno.setEnabled(False)
            self.comboLayer.setEnabled(False)

    def buttonFile_clicked(self):
        res = QFileDialog.getSaveFileName(self, self.tr('Convert Labels To'),
                self.leditFile.text(), "GeoPackage (*.gpkg)")
        if res[0]:
            self.leditFile.setText(res[0])


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    ConvertLabelsDialog().exec()
