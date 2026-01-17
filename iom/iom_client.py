# -*- coding: utf-8 -*-
"""
IOM Client for Sudan Data Loader.

Provides access to IOM Displacement Tracking Matrix (DTM) data for Sudan.
"""

import json
import os
import tempfile
from datetime import datetime

from qgis.PyQt.QtCore import QUrl, QObject, pyqtSignal
from qgis.core import QgsBlockingNetworkRequest, QgsMessageLog, Qgis
from qgis.PyQt.QtNetwork import QNetworkRequest


class IOMClient(QObject):
    """Client for accessing IOM Displacement Tracking Matrix data."""

    # IOM DTM API endpoints
    # Note: IOM DTM data is often accessed through HDX or direct reports
    # This uses available public endpoints
    HDX_API = "https://data.humdata.org/api/3/action"

    # Sudan-specific datasets on HDX related to IOM/DTM
    DTM_DATASETS = {
        'dtm-sudan-idp': {
            'id': 'iom-dtm-sudan-baseline-assessment',
            'name': 'DTM Sudan - IDP Populations',
            'description': 'Internally Displaced Persons baseline assessment data',
            'category': 'Displacement'
        },
        'dtm-sudan-mobility': {
            'id': 'iom-dtm-sudan-mobility-tracking',
            'name': 'DTM Sudan - Mobility Tracking',
            'description': 'Population mobility and movement tracking',
            'category': 'Mobility'
        },
        'dtm-sudan-camps': {
            'id': 'sudan-idp-camps',
            'name': 'IDP Camp Locations',
            'description': 'Locations and populations of IDP camps',
            'category': 'Camps'
        },
        'unhcr-refugees': {
            'id': 'unhcr-refugee-camps',
            'name': 'UNHCR Refugee Sites',
            'description': 'Refugee camp and settlement locations',
            'category': 'Refugees'
        },
        'displacement-sites': {
            'id': 'sudan-displacement-sites',
            'name': 'Displacement Sites',
            'description': 'All displacement site locations',
            'category': 'Sites'
        }
    }

    # Sudan states for filtering
    SUDAN_STATES = [
        'Blue Nile', 'Central Darfur', 'East Darfur', 'Gedaref',
        'Gezira', 'Kassala', 'Khartoum', 'North Darfur',
        'North Kordofan', 'Northern', 'Red Sea', 'River Nile',
        'Sennar', 'South Darfur', 'South Kordofan', 'West Darfur',
        'West Kordofan', 'White Nile'
    ]

    # Categories
    CATEGORIES = {
        'Displacement': '#e74c3c',
        'Mobility': '#3498db',
        'Camps': '#9b59b6',
        'Refugees': '#e67e22',
        'Sites': '#27ae60'
    }

    # Signals
    data_loaded = pyqtSignal(dict)
    datasets_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    progress_update = pyqtSignal(str)

    def __init__(self):
        """Initialize the IOM client."""
        super().__init__()
        self.cache_dir = os.path.join(tempfile.gettempdir(), 'sudan_iom_cache')
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_datasets(self):
        """Get list of available DTM datasets."""
        return list(self.DTM_DATASETS.values())

    def get_categories(self):
        """Get list of categories."""
        return list(self.CATEGORIES.keys())

    def get_category_color(self, category):
        """Get color for a category."""
        return self.CATEGORIES.get(category, '#95a5a6')

    def get_states(self):
        """Get list of Sudan states."""
        return self.SUDAN_STATES

    def search_dtm_datasets(self, query='displacement'):
        """
        Search for DTM-related datasets on HDX.

        :param query: Search query
        :returns: List of dataset dictionaries
        """
        self.progress_update.emit(f"Searching for '{query}' datasets...")

        url = f"{self.HDX_API}/package_search?q=sudan+{query}&fq=groups:sdn&rows=50"

        request = QNetworkRequest(QUrl(url))
        blocking = QgsBlockingNetworkRequest()
        error = blocking.get(request)

        if error != QgsBlockingNetworkRequest.NoError:
            self.error_occurred.emit(f"Search failed: {blocking.errorMessage()}")
            return []

        try:
            content = bytes(blocking.reply().content())
            response = json.loads(content)

            if response.get('success'):
                datasets = []
                for pkg in response['result']['results']:
                    # Filter for relevant datasets
                    tags = [t['name'].lower() for t in pkg.get('tags', [])]
                    name_lower = pkg.get('title', '').lower()

                    is_relevant = any(term in name_lower or term in tags for term in
                                      ['idp', 'displacement', 'refugee', 'dtm', 'mobility', 'camp', 'iom'])

                    if is_relevant:
                        datasets.append({
                            'id': pkg.get('name', ''),
                            'title': pkg.get('title', ''),
                            'description': pkg.get('notes', '')[:300] if pkg.get('notes') else '',
                            'organization': pkg.get('organization', {}).get('title', 'Unknown'),
                            'last_modified': pkg.get('metadata_modified', ''),
                            'resources': self._filter_gis_resources(pkg.get('resources', []))
                        })

                self.datasets_loaded.emit(datasets)
                return datasets

        except (json.JSONDecodeError, KeyError) as e:
            self.error_occurred.emit(f"Failed to parse response: {str(e)}")

        return []

    def _filter_gis_resources(self, resources):
        """Filter for GIS-compatible resources."""
        gis_formats = ['GEOJSON', 'SHP', 'GPKG', 'KML', 'GEOPACKAGE', 'SHAPEFILE', 'CSV']
        filtered = []

        for res in resources:
            format_type = res.get('format', '').upper()
            if format_type in gis_formats:
                filtered.append({
                    'id': res.get('id', ''),
                    'name': res.get('name', res.get('description', 'Unnamed')),
                    'format': format_type,
                    'url': res.get('url', ''),
                    'size': res.get('size', 0)
                })

        # Sort by format preference
        format_order = {'GEOJSON': 0, 'GPKG': 1, 'GEOPACKAGE': 1, 'SHP': 2, 'SHAPEFILE': 2, 'KML': 3, 'CSV': 4}
        filtered.sort(key=lambda x: format_order.get(x['format'], 5))

        return filtered

    def get_dataset_details(self, dataset_id):
        """
        Get detailed information about a dataset.

        :param dataset_id: HDX dataset ID
        :returns: Dataset details dictionary
        """
        self.progress_update.emit(f"Fetching dataset details: {dataset_id}")

        url = f"{self.HDX_API}/package_show?id={dataset_id}"

        request = QNetworkRequest(QUrl(url))
        blocking = QgsBlockingNetworkRequest()
        error = blocking.get(request)

        if error != QgsBlockingNetworkRequest.NoError:
            self.error_occurred.emit(f"Failed to fetch details: {blocking.errorMessage()}")
            return None

        try:
            content = bytes(blocking.reply().content())
            response = json.loads(content)

            if response.get('success'):
                pkg = response['result']
                details = {
                    'id': pkg.get('name', ''),
                    'title': pkg.get('title', ''),
                    'description': pkg.get('notes', ''),
                    'organization': pkg.get('organization', {}).get('title', 'Unknown'),
                    'maintainer': pkg.get('maintainer', ''),
                    'last_modified': pkg.get('metadata_modified', ''),
                    'methodology': pkg.get('methodology', ''),
                    'caveats': pkg.get('caveats', ''),
                    'resources': self._filter_gis_resources(pkg.get('resources', [])),
                    'url': f"https://data.humdata.org/dataset/{dataset_id}"
                }
                self.data_loaded.emit(details)
                return details

        except (json.JSONDecodeError, KeyError) as e:
            self.error_occurred.emit(f"Failed to parse details: {str(e)}")

        return None

    def download_resource(self, resource_url, filename=None):
        """
        Download a resource file.

        :param resource_url: URL of the resource
        :param filename: Output filename (optional)
        :returns: Local file path or None
        """
        if not filename:
            filename = resource_url.split('/')[-1].split('?')[0]

        self.progress_update.emit(f"Downloading {filename}...")

        local_path = os.path.join(self.cache_dir, filename)

        request = QNetworkRequest(QUrl(resource_url))
        request.setAttribute(
            QNetworkRequest.RedirectPolicyAttribute,
            QNetworkRequest.NoLessSafeRedirectPolicy
        )

        blocking = QgsBlockingNetworkRequest()
        error = blocking.get(request, forceRefresh=True)

        if error != QgsBlockingNetworkRequest.NoError:
            self.error_occurred.emit(f"Download failed: {blocking.errorMessage()}")
            return None

        data = bytes(blocking.reply().content())

        if len(data) == 0:
            self.error_occurred.emit("Downloaded file is empty")
            return None

        try:
            with open(local_path, 'wb') as f:
                f.write(data)
            return local_path
        except IOError as e:
            self.error_occurred.emit(f"Failed to save file: {str(e)}")
            return None

    def get_featured_datasets(self):
        """Get pre-defined featured DTM datasets."""
        return list(self.DTM_DATASETS.values())

    def fetch_latest_dtm_report(self):
        """
        Fetch the latest DTM report summary.

        :returns: Report summary dictionary
        """
        # Search for latest DTM baseline assessment
        datasets = self.search_dtm_datasets('dtm baseline')

        if datasets:
            # Get the most recent one
            datasets.sort(key=lambda x: x.get('last_modified', ''), reverse=True)
            return datasets[0] if datasets else None

        return None

    def create_displacement_summary(self, data_list):
        """
        Create a summary of displacement data.

        :param data_list: List of displacement records
        :returns: Summary dictionary
        """
        if not data_list:
            return {}

        total_idps = 0
        by_state = {}
        by_cause = {}

        for record in data_list:
            # Adjust field names based on actual data structure
            idp_count = record.get('idp_count', record.get('num_idps', record.get('population', 0)))
            state = record.get('state', record.get('admin1', 'Unknown'))
            cause = record.get('cause', record.get('displacement_cause', 'Unknown'))

            try:
                idp_count = int(idp_count)
            except (ValueError, TypeError):
                idp_count = 0

            total_idps += idp_count

            if state:
                by_state[state] = by_state.get(state, 0) + idp_count

            if cause:
                by_cause[cause] = by_cause.get(cause, 0) + idp_count

        return {
            'total_idps': total_idps,
            'by_state': by_state,
            'by_cause': by_cause,
            'record_count': len(data_list)
        }

    def clear_cache(self):
        """Clear cache directory."""
        import shutil
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)
            os.makedirs(self.cache_dir, exist_ok=True)
