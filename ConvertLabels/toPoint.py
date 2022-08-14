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
from osgeo import gdal
from qgis.core import (QgsProject, QgsVectorLayer, QgsVectorFileWriter,
                       Qgis, QgsDataProvider, QgsPalLayerSettings,
                       QgsNullSymbolRenderer)

try:
    OverPoint = Qgis.LabelPlacement.OverPoint  # QGIS 3.26
except:
    OverPoint = QgsPalLayerSettings.Placement.OverPoint
try:
    AboveRight = Qgis.LabelQuadrantPosition.AboveRight  # QGIS 3.26
except:
    AboveRight = QgsPalLayerSettings.QuadrantPosition.QuadrantAboveRight


def convertToPoint(self):
    prj = QgsProject.instance()
    src = self.iface.activeLayer()
    dst = QgsVectorLayer('Point', '', 'memory')
    dst.setCrs(src.crs())

    dst.startEditing()

    for field in src.fields():
        dst.addAttribute(field)
    settings = src.labeling().settings()

    if self.dialog.checkSelected.isChecked():
        feats = src.getSelectedFeatures()    
    else:
        feats = src.getFeatures()

    for feat in feats:
        for geom in feat.geometry().asGeometryCollection():
            if settings.centroidInside:
                p = geom.pointOnSurface()
            else:
                p = geom.centroid()
            feat.setGeometry(p)
            dst.addFeature(feat)
            if not settings.labelPerPart:
                break

    # Delete 'fid' field if exists
    fid_idx = dst.fields().lookupField('fid')
    if fid_idx >= 0:
        dst.deleteAttribute(fid_idx)

    dst.commitChanges()

    filename = self.dialog.leditFile.text()
    layername = self.dialog.leditLayer.text()
    tc = prj.transformContext()
    options = QgsVectorFileWriter.SaveVectorOptions()
    options.layerName = layername
    if os.path.exists(filename):
        ds = gdal.OpenEx(filename)
        lyr_names = [ds.GetLayer(i).GetName() for i in range(ds.GetLayerCount())]
        ds = None
        if (layername in lyr_names
                and not self.dialog.checkOverwrite.isChecked()):
            flag = QgsVectorFileWriter.AppendToLayerNoNewFields
        else:
            flag = QgsVectorFileWriter.CreateOrOverwriteLayer
        options.actionOnExistingFile = flag
    if Qgis.QGIS_VERSION_INT >= 32000:
        _write = QgsVectorFileWriter.writeAsVectorFormatV3
    else:
        _write = QgsVectorFileWriter.writeAsVectorFormatV2  # QGIS 3.10.3
    err = _write(dst, filename, tc, options)
    if err[0]:
        if err[1]:
            msg = err[1]
        else:
            msg = 'QgsVectorFileWriter::WriterError: %d' % err[0]
        self.iface.messageBar().pushCritical(self.plugin_name, msg)
        return

    options = QgsDataProvider.ProviderOptions()
    options.transformContext = tc
    dst.setDataSource('|'.join((filename, 'layername=%s' % layername)),
            layername, 'ogr', options)

    labeling = src.labeling().clone()
    settings = labeling.settings()
    settings.displayAll = True
    if settings.placement != OverPoint:
        settings.placement = OverPoint
        settings.quadOffset = AboveRight
        settings.xOffset = 0
        settings.yOffset = 0
    labeling.setSettings(settings)
    dst.setLabeling(labeling)
    dst.setLabelsEnabled(True)
    dst.setRenderer(QgsNullSymbolRenderer())
    dst.saveStyleToDatabase(layername, '', True, '')

    src.setLabelsEnabled(False)
    prj.addMapLayer(dst)
