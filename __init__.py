# -*- coding: utf-8 -*-
"""
/***************************************************************************
 inputprep
                                 A QGIS plugin
 This plugin prepares vector and raster datasets for us in the beaver dam tools location generator and water storage estimators
                             -------------------
        begin                : 2017-07-04
        copyright            : (C) 2017 by Konrad Hafen
        email                : k.hafen@aggiemail.usu.edu
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
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load inputprep class from file inputprep.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .inputprep import inputprep
    return inputprep(iface)
