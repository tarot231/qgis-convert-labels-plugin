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

from qgis.PyQt.QtCore import QVariant
from qgis.core import (QgsProject, QgsCoordinateTransform,
                       QgsTextFormat, QgsExpression, QgsExpressionContext,
                       QgsAnnotationPointTextItem)


def convertToAnnotation(self):
    prj = QgsProject.instance()
    src = self.iface.activeLayer()
    dst = None
    try:
        dst = self.dialog.comboLayer.currentLayer()
    except AttributeError:
        pass
    if dst is None:
        dst = prj.mainAnnotationLayer()

    if dst.crs() != src.crs():
        ct = QgsCoordinateTransform(src.crs(), dst.crs(), prj)
    else:
        ct = None

    settings = src.labeling().settings()
    format = QgsTextFormat(settings.format())

    # https://gis.stackexchange.com/q/325009
    expression = QgsExpression(settings.fieldName)
    context = QgsExpressionContext()

    if self.dialog.checkSelected.isChecked():
        feats = src.getSelectedFeatures()
    else:
        feats = src.getFeatures()

    for feat in feats:
        context.setFeature(feat)
        expression.prepare(context)
        value = expression.evaluate(context)
        if value is None or (isinstance(value, QVariant) and value.isNull()):
            continue

        for geom in feat.geometry().asGeometryCollection():
            if settings.centroidInside:
                p = geom.pointOnSurface()
            else:
                p = geom.centroid()
            if ct:
                p.transform(ct)
            item = QgsAnnotationPointTextItem(str(value), p.asPoint())
            item.setFormat(format)
            dst.addItem(item)
            if not settings.labelPerPart:
                break

    src.setLabelsEnabled(False)
