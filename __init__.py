# -*- coding: utf-8 -*-
"""
Sudan Data Downloader - QGIS 3 Plugin

This plugin loads Sudan administrative boundary data from GeoPackages
and applies QML styles.
"""


def classFactory(iface):
    """
    Load the SudanDataLoader class from the plugin.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    :returns: SudanDataLoader instance
    """
    from .sudan_data_loader import SudanDataLoader
    return SudanDataLoader(iface)
