# -*- coding: utf-8 -*-
"""
Sudan Data Downloader - Main Plugin Class

This module contains the main plugin class that handles loading
Sudan administrative boundary data from GeoPackages and applying styles.
"""

import os
import json
import zipfile
import hashlib
import tempfile
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QProgressDialog
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QStandardPaths, QUrl, QEventLoop, Qt
from qgis.core import QgsProject, QgsVectorLayer, QgsNetworkAccessManager, QgsBlockingNetworkRequest
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply


class SudanDataLoader:
    """QGIS Plugin for loading Sudan administrative boundary data."""

    def __init__(self, iface):
        """
        Initialize the plugin.

        :param iface: A QGIS interface instance.
        :type iface: QgsInterface
        """
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        # Bundled data directories (fallback)
        self.bundled_data_dir = os.path.join(self.plugin_dir, 'Data')
        self.bundled_styles_dir = os.path.join(self.plugin_dir, 'styles')

        # Cache directories (user-writable location for downloaded data)
        self.VERSION_URL = "https://example.com/sudan-data/version.json"  # User configurable
        self.cache_dir = os.path.join(
            QStandardPaths.writableLocation(QStandardPaths.AppDataLocation),
            'sudan_data_loader'
        )
        self.cache_data_dir = os.path.join(self.cache_dir, 'Data')
        self.cache_styles_dir = os.path.join(self.cache_dir, 'styles')
        self.local_version_file = os.path.join(self.cache_dir, 'version.json')

        # Active data directories (resolved at runtime)
        self.data_dir = None
        self.styles_dir = None

        self.action = None
        self.download_action = None

        # Define layers to load (order: first = bottom, last = top)
        self.layers_config = [
            {'gpkg': 'admin0.gpkg', 'style': 'admin0.qml', 'name': 'Sudan Admin 0 - Country'},
            {'gpkg': 'admin1.gpkg', 'style': 'admin1.qml', 'name': 'Sudan Admin 1 - States'},
            {'gpkg': 'admin2.gpkg', 'style': 'admin2.qml', 'name': 'Sudan Admin 2 - Localities'},
            {'gpkg': 'admin_lines.gpkg', 'style': None, 'name': 'Sudan Admin Lines'},
            {'gpkg': 'admin_points.gpkg', 'style': None, 'name': 'Sudan Admin Points'},
        ]

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        # Action to load Sudan admin data
        self.action = QAction(
            QIcon(),
            'Load Sudan Admin Data',
            self.iface.mainWindow()
        )
        self.action.triggered.connect(self.run)
        self.action.setWhatsThis('Load Sudan administrative boundary data')

        # Action to download/update Sudan data
        self.download_action = QAction(
            QIcon(),
            'Download/Update Sudan Data',
            self.iface.mainWindow()
        )
        self.download_action.triggered.connect(self.download_update)
        self.download_action.setWhatsThis('Download or update Sudan data from remote server')

        # Add toolbar buttons and menu items
        self.iface.addToolBarIcon(self.action)
        self.iface.addToolBarIcon(self.download_action)
        self.iface.addPluginToVectorMenu('&Sudan Data Downloader', self.action)
        self.iface.addPluginToVectorMenu('&Sudan Data Downloader', self.download_action)

    def unload(self):
        """Remove the plugin menu items and icons from QGIS GUI."""
        self.iface.removePluginVectorMenu('&Sudan Data Downloader', self.action)
        self.iface.removePluginVectorMenu('&Sudan Data Downloader', self.download_action)
        self.iface.removeToolBarIcon(self.action)
        self.iface.removeToolBarIcon(self.download_action)

    def _get_data_directories(self):
        """
        Resolve which data directories to use.

        Checks if cache directories exist and have files.
        If cache is valid, returns cache paths. Otherwise returns bundled plugin paths.

        :returns: Tuple of (data_dir, styles_dir)
        """
        # Check if cache directories exist and have data files
        cache_valid = (
            os.path.isdir(self.cache_data_dir) and
            os.path.isdir(self.cache_styles_dir) and
            any(f.endswith('.gpkg') for f in os.listdir(self.cache_data_dir) if os.path.isfile(os.path.join(self.cache_data_dir, f)))
        )

        if cache_valid:
            return self.cache_data_dir, self.cache_styles_dir
        else:
            return self.bundled_data_dir, self.bundled_styles_dir

    def run(self):
        """Main method to load all Sudan admin layers."""
        # Resolve which data directories to use
        self.data_dir, self.styles_dir = self._get_data_directories()

        # Validate directories exist
        if not self._validate_directories():
            return

        # Check for missing files
        missing_files = self._check_missing_files()
        if missing_files:
            self._show_error(
                'Missing Files',
                'The following required files are missing:\n\n' + '\n'.join(missing_files)
            )
            return

        # Load layers
        loaded_layers = []
        for config in self.layers_config:
            layer = self._load_gpkg_layer(config['gpkg'], config['name'])
            if layer:
                # Apply style if specified
                if config['style']:
                    self._apply_style(layer, config['style'])

                # Add layer to project
                QgsProject.instance().addMapLayer(layer)
                loaded_layers.append(layer.name())

        if loaded_layers:
            # Zoom to the extent of the first layer (admin0 - country boundary)
            first_layer = QgsProject.instance().mapLayersByName(self.layers_config[0]['name'])
            if first_layer:
                self.iface.mapCanvas().setExtent(first_layer[0].extent())
                self.iface.mapCanvas().refresh()

            self._show_info(
                'Success',
                f'Successfully loaded {len(loaded_layers)} layers:\n\n' + '\n'.join(loaded_layers)
            )
        else:
            self._show_warning('Warning', 'No layers were loaded.')

    def _load_gpkg_layer(self, gpkg_filename, layer_name):
        """
        Load a layer from a GeoPackage file using auto-detection.

        :param gpkg_filename: Name of the GeoPackage file
        :param layer_name: Display name for the layer
        :returns: QgsVectorLayer or None if loading failed
        """
        gpkg_path = os.path.join(self.data_dir, gpkg_filename)

        # Use ogr to open and auto-detect layer name
        uri = gpkg_path
        layer = QgsVectorLayer(uri, layer_name, 'ogr')

        if not layer.isValid():
            self._show_warning(
                'Layer Load Failed',
                f'Failed to load layer from: {gpkg_filename}\n\n'
                'The file may be corrupted or in an unsupported format.'
            )
            return None

        return layer

    def _apply_style(self, layer, style_filename):
        """
        Apply a QML style to a layer.

        :param layer: QgsVectorLayer to style
        :param style_filename: Name of the QML style file
        """
        style_path = os.path.join(self.styles_dir, style_filename)

        if os.path.exists(style_path):
            result = layer.loadNamedStyle(style_path)
            if not result[1]:  # result is tuple (success_message, success_bool)
                self._show_warning(
                    'Style Load Warning',
                    f'Could not apply style {style_filename} to layer {layer.name()}'
                )
        else:
            self._show_warning(
                'Style Not Found',
                f'Style file not found: {style_filename}'
            )

    def _validate_directories(self):
        """
        Check that Data and styles directories exist.

        :returns: True if directories exist, False otherwise
        """
        if not os.path.isdir(self.data_dir):
            self._show_error(
                'Data Directory Missing',
                f'The Data directory was not found at:\n{self.data_dir}\n\n'
                'Please ensure the plugin is installed correctly.'
            )
            return False

        if not os.path.isdir(self.styles_dir):
            self._show_error(
                'Styles Directory Missing',
                f'The styles directory was not found at:\n{self.styles_dir}\n\n'
                'Please ensure the plugin is installed correctly.'
            )
            return False

        return True

    def _check_missing_files(self):
        """
        Check for missing GeoPackage and style files.

        :returns: List of missing file paths
        """
        missing = []

        for config in self.layers_config:
            gpkg_path = os.path.join(self.data_dir, config['gpkg'])
            if not os.path.exists(gpkg_path):
                missing.append(f"Data/{config['gpkg']}")

            if config['style']:
                style_path = os.path.join(self.styles_dir, config['style'])
                if not os.path.exists(style_path):
                    missing.append(f"styles/{config['style']}")

        return missing

    # ============ Download/Update Methods ============

    def download_update(self):
        """
        Main method to download or update Sudan data from remote server.

        Orchestrates the download process:
        1. Fetch version.json from server
        2. Compare with local cached version
        3. If update needed, download ZIP bundle
        4. Extract safely to cache directory
        5. Save version.json locally
        """
        # Fetch remote version info
        version_info = self._fetch_version_info()
        if version_info is None:
            return

        remote_version = version_info.get('version')
        bundle_url = version_info.get('bundle_url')
        sha256 = version_info.get('sha256')

        if not remote_version or not bundle_url:
            self._show_error(
                'Invalid Version Info',
                'The version information from the server is incomplete.\n'
                'Missing version or bundle_url.'
            )
            return

        # Check local version
        local_version = self._get_local_version()

        if local_version and local_version == remote_version:
            self._show_info(
                'Up to Date',
                f'Data is already up to date (v{local_version})'
            )
            return

        # Download the bundle
        zip_data = self._download_bundle(bundle_url, sha256)
        if zip_data is None:
            return  # Download cancelled or failed

        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)

        # Extract ZIP safely
        if not self._extract_zip_safely(zip_data, self.cache_dir):
            return  # Extraction failed

        # Save version info locally
        self._save_local_version(version_info)

        self._show_info(
            'Download Complete',
            f'Successfully downloaded Sudan Data v{remote_version}'
        )

    def _fetch_version_info(self):
        """
        Fetch version.json from the remote server.

        :returns: dict with version info or None on failure
        """
        request = QgsBlockingNetworkRequest()
        err = request.get(QNetworkRequest(QUrl(self.VERSION_URL)))

        if err != QgsBlockingNetworkRequest.NoError:
            error_msg = request.errorMessage()
            self._show_error(
                'Network Error',
                f'Failed to fetch version info from server:\n{error_msg}'
            )
            return None

        reply = request.reply()
        content = reply.content().data()

        try:
            version_info = json.loads(content.decode('utf-8'))
            return version_info
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            self._show_error(
                'Parse Error',
                f'Failed to parse version info:\n{str(e)}'
            )
            return None

    def _get_local_version(self):
        """
        Read local version.json from cache directory if it exists.

        :returns: Version string or None if not found
        """
        if not os.path.exists(self.local_version_file):
            return None

        try:
            with open(self.local_version_file, 'r', encoding='utf-8') as f:
                version_info = json.load(f)
                return version_info.get('version')
        except (json.JSONDecodeError, IOError):
            return None

    def _download_bundle(self, url, sha256=None):
        """
        Download the data bundle from the given URL.

        :param url: URL to download from
        :param sha256: Optional SHA256 hash to verify download
        :returns: Downloaded bytes or None on cancel/error
        """
        # Create progress dialog
        progress = QProgressDialog(
            'Downloading Sudan Data...',
            'Cancel',
            0, 100,
            self.iface.mainWindow()
        )
        progress.setWindowTitle('Download Progress')
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)

        # Use QgsNetworkAccessManager for the download
        manager = QgsNetworkAccessManager.instance()
        request = QNetworkRequest(QUrl(url))
        reply = manager.get(request)

        # Track downloaded data
        downloaded_data = bytearray()
        cancelled = False

        def on_download_progress(received, total):
            nonlocal cancelled
            if progress.wasCanceled():
                cancelled = True
                reply.abort()
                return
            if total > 0:
                progress.setValue(int(received * 100 / total))

        def on_ready_read():
            downloaded_data.extend(reply.readAll().data())

        def on_finished():
            loop.quit()

        reply.downloadProgress.connect(on_download_progress)
        reply.readyRead.connect(on_ready_read)
        reply.finished.connect(on_finished)

        # Run event loop until download completes
        loop = QEventLoop()
        loop.exec_()

        progress.close()

        if cancelled:
            self._show_info('Cancelled', 'Download cancelled.')
            return None

        if reply.error() != QNetworkReply.NoError:
            self._show_error(
                'Download Error',
                f'Failed to download data bundle:\n{reply.errorString()}'
            )
            reply.deleteLater()
            return None

        reply.deleteLater()
        data = bytes(downloaded_data)

        # Verify SHA256 if provided
        if sha256:
            calculated_hash = hashlib.sha256(data).hexdigest()
            if calculated_hash.lower() != sha256.lower():
                self._show_error(
                    'Verification Failed',
                    'Downloaded file hash does not match expected hash.\n'
                    'The download may be corrupted.'
                )
                return None

        return data

    def _extract_zip_safely(self, zip_data, target_dir):
        """
        Extract ZIP data safely to the target directory.

        Implements zip-slip protection to prevent path traversal attacks.

        :param zip_data: Bytes of the ZIP file
        :param target_dir: Directory to extract to
        :returns: True on success, False on failure
        """
        # Write to temporary file
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as f:
                temp_file = f.name
                f.write(zip_data)

            # Open and extract ZIP
            with zipfile.ZipFile(temp_file, 'r') as zf:
                for member in zf.namelist():
                    # Check for safe path (zip-slip prevention)
                    if not self._is_safe_path(target_dir, member):
                        self._show_error(
                            'Security Error',
                            f'Unsafe path detected in ZIP: {member}\n'
                            'Extraction aborted for security.'
                        )
                        return False

                    # Extract the member
                    target_path = os.path.join(target_dir, member)

                    # Create directories if needed
                    if member.endswith('/'):
                        os.makedirs(target_path, exist_ok=True)
                    else:
                        # Ensure parent directory exists
                        parent_dir = os.path.dirname(target_path)
                        os.makedirs(parent_dir, exist_ok=True)

                        # Extract file
                        with zf.open(member) as source, open(target_path, 'wb') as dest:
                            dest.write(source.read())

            return True

        except zipfile.BadZipFile:
            self._show_error(
                'Extraction Error',
                'The downloaded file is not a valid ZIP archive.'
            )
            return False
        except IOError as e:
            self._show_error(
                'Extraction Error',
                f'Failed to extract files:\n{str(e)}'
            )
            return False
        finally:
            # Clean up temp file
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError:
                    pass

    def _is_safe_path(self, base_dir, file_path):
        """
        Check if a file path is safe (within the base directory).

        Prevents zip-slip attacks by ensuring extracted paths stay within target.

        :param base_dir: Base directory that files should be within
        :param file_path: Path to check
        :returns: True if safe, False if potential path traversal
        """
        # Normalize and resolve the full path
        full_path = os.path.normpath(os.path.join(base_dir, file_path))
        base_path = os.path.normpath(base_dir)

        # Check for path traversal attempts
        if '..' in file_path:
            return False

        # Check for absolute paths
        if os.path.isabs(file_path):
            return False

        # Ensure the resolved path is within the base directory
        return full_path.startswith(base_path + os.sep) or full_path == base_path

    def _save_local_version(self, version_info):
        """
        Save version info to local cache directory.

        :param version_info: Dict with version information to save
        """
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            with open(self.local_version_file, 'w', encoding='utf-8') as f:
                json.dump(version_info, f, indent=2)
        except IOError as e:
            self._show_warning(
                'Version Save Warning',
                f'Could not save version info:\n{str(e)}'
            )

    # ============ Helper Methods ============

    def _show_error(self, title, message):
        """Show an error message dialog."""
        QMessageBox.critical(self.iface.mainWindow(), title, message)

    def _show_warning(self, title, message):
        """Show a warning message dialog."""
        QMessageBox.warning(self.iface.mainWindow(), title, message)

    def _show_info(self, title, message):
        """Show an information message dialog."""
        QMessageBox.information(self.iface.mainWindow(), title, message)
