# -*- coding: utf-8 -*-
"""
ACLED Client for Sudan Data Loader.

Provides access to Armed Conflict Location & Event Data (ACLED) for Sudan.
"""

import json
import os
from datetime import datetime, timedelta
from urllib.parse import urlencode

from qgis.PyQt.QtCore import QUrl, QObject, pyqtSignal
from qgis.core import QgsBlockingNetworkRequest
from qgis.PyQt.QtNetwork import QNetworkRequest


class ACLEDClient(QObject):
    """Client for accessing ACLED API."""

    # ACLED API endpoint (public read access for recent data)
    API_URL = "https://api.acleddata.com/acled/read"

    # Export endpoint (for downloading without API key)
    EXPORT_URL = "https://acleddata.com/download"

    # Sudan ISO code
    SUDAN_ISO = 729
    SUDAN_COUNTRY = "Sudan"

    # Event types with colors for visualization
    EVENT_TYPES = {
        'Battles': {
            'color': '#e74c3c',
            'icon': 'circle',
            'description': 'Armed clashes between organized groups'
        },
        'Violence against civilians': {
            'color': '#9b59b6',
            'icon': 'circle',
            'description': 'Attacks on unarmed civilians'
        },
        'Explosions/Remote violence': {
            'color': '#e67e22',
            'icon': 'triangle',
            'description': 'Bombs, IEDs, shelling, airstrikes'
        },
        'Riots': {
            'color': '#f39c12',
            'icon': 'square',
            'description': 'Violent demonstrations and mobs'
        },
        'Protests': {
            'color': '#3498db',
            'icon': 'diamond',
            'description': 'Non-violent demonstrations'
        },
        'Strategic developments': {
            'color': '#1abc9c',
            'icon': 'star',
            'description': 'Strategic military/political events'
        }
    }

    # Actor types
    ACTOR_TYPES = [
        'Military Forces of Sudan',
        'RSF: Rapid Support Forces',
        'Police Forces of Sudan',
        'Rebel Groups',
        'Political Militias',
        'Civilians',
        'Protesters'
    ]

    # Signals
    data_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, api_key=None, email=None):
        """
        Initialize the ACLED client.

        :param api_key: ACLED API key (optional for limited access)
        :param email: Email associated with API key
        """
        super().__init__()
        self.api_key = api_key
        self.email = email

    def set_credentials(self, api_key, email):
        """Set API credentials."""
        self.api_key = api_key
        self.email = email

    def get_event_types(self):
        """Get list of event types."""
        return list(self.EVENT_TYPES.keys())

    def get_event_color(self, event_type):
        """Get color for an event type."""
        return self.EVENT_TYPES.get(event_type, {}).get('color', '#95a5a6')

    def get_event_info(self, event_type):
        """Get info for an event type."""
        return self.EVENT_TYPES.get(event_type, {})

    def fetch_events(self, start_date=None, end_date=None, event_types=None,
                     admin1=None, limit=5000):
        """
        Fetch conflict events from ACLED API.

        :param start_date: Start date (YYYY-MM-DD)
        :param end_date: End date (YYYY-MM-DD)
        :param event_types: List of event types to filter
        :param admin1: Admin1 region to filter
        :param limit: Maximum number of events
        :returns: List of event dictionaries
        """
        # Build query parameters
        params = {
            'country': self.SUDAN_COUNTRY,
            'limit': limit
        }

        # Add API credentials if available
        if self.api_key and self.email:
            params['key'] = self.api_key
            params['email'] = self.email

        # Date filtering
        if start_date:
            params['event_date'] = start_date
            params['event_date_where'] = '>='

        if end_date:
            if 'event_date' in params:
                # Need to use different approach for date range
                params['event_date'] = f"{start_date}|{end_date}"
                params['event_date_where'] = 'BETWEEN'
            else:
                params['event_date'] = end_date
                params['event_date_where'] = '<='

        # Event type filtering
        if event_types and len(event_types) > 0:
            params['event_type'] = '|'.join(event_types)

        # Admin1 filtering
        if admin1:
            params['admin1'] = admin1

        # Make API request
        url = f"{self.API_URL}?{urlencode(params)}"

        request = QNetworkRequest(QUrl(url))
        request.setHeader(QNetworkRequest.ContentTypeHeader, 'application/json')

        blocking = QgsBlockingNetworkRequest()
        error = blocking.get(request)

        if error != QgsBlockingNetworkRequest.NoError:
            self.error_occurred.emit(f"API request failed: {blocking.errorMessage()}")
            return []

        try:
            response = json.loads(bytes(blocking.reply().content()))

            if response.get('success', False):
                events = response.get('data', [])
                self.data_loaded.emit(events)
                return events
            else:
                error_msg = response.get('error', {}).get('message', 'Unknown error')
                self.error_occurred.emit(f"ACLED API error: {error_msg}")
                return []

        except json.JSONDecodeError as e:
            self.error_occurred.emit(f"Failed to parse API response: {str(e)}")
            return []

    def fetch_recent_events(self, days=30, event_types=None):
        """
        Fetch recent conflict events.

        :param days: Number of days to look back
        :param event_types: Event types to filter
        :returns: List of events
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        return self.fetch_events(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            event_types=event_types
        )

    def fetch_events_by_year(self, year, event_types=None):
        """
        Fetch conflict events for a specific year.

        :param year: Year to fetch
        :param event_types: Event types to filter
        :returns: List of events
        """
        return self.fetch_events(
            start_date=f"{year}-01-01",
            end_date=f"{year}-12-31",
            event_types=event_types
        )

    def events_to_geojson(self, events):
        """
        Convert events to GeoJSON format.

        :param events: List of event dictionaries
        :returns: GeoJSON dictionary
        """
        features = []

        for event in events:
            try:
                lat = float(event.get('latitude', 0))
                lon = float(event.get('longitude', 0))

                if lat == 0 and lon == 0:
                    continue

                feature = {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [lon, lat]
                    },
                    'properties': {
                        'event_id': event.get('event_id_cnty', ''),
                        'event_date': event.get('event_date', ''),
                        'year': event.get('year', ''),
                        'event_type': event.get('event_type', ''),
                        'sub_event_type': event.get('sub_event_type', ''),
                        'actor1': event.get('actor1', ''),
                        'actor2': event.get('actor2', ''),
                        'admin1': event.get('admin1', ''),
                        'admin2': event.get('admin2', ''),
                        'admin3': event.get('admin3', ''),
                        'location': event.get('location', ''),
                        'fatalities': int(event.get('fatalities', 0)),
                        'notes': event.get('notes', ''),
                        'source': event.get('source', ''),
                        'source_scale': event.get('source_scale', '')
                    }
                }
                features.append(feature)

            except (ValueError, TypeError):
                continue

        return {
            'type': 'FeatureCollection',
            'features': features
        }

    def get_statistics(self, events):
        """
        Calculate statistics from events.

        :param events: List of events
        :returns: Statistics dictionary
        """
        if not events:
            return {}

        stats = {
            'total_events': len(events),
            'total_fatalities': sum(int(e.get('fatalities', 0)) for e in events),
            'by_event_type': {},
            'by_admin1': {},
            'by_actor': {},
            'date_range': {
                'start': min(e.get('event_date', '') for e in events),
                'end': max(e.get('event_date', '') for e in events)
            }
        }

        # Count by event type
        for event in events:
            event_type = event.get('event_type', 'Unknown')
            if event_type not in stats['by_event_type']:
                stats['by_event_type'][event_type] = {'count': 0, 'fatalities': 0}
            stats['by_event_type'][event_type]['count'] += 1
            stats['by_event_type'][event_type]['fatalities'] += int(event.get('fatalities', 0))

        # Count by admin1
        for event in events:
            admin1 = event.get('admin1', 'Unknown')
            if admin1 not in stats['by_admin1']:
                stats['by_admin1'][admin1] = {'count': 0, 'fatalities': 0}
            stats['by_admin1'][admin1]['count'] += 1
            stats['by_admin1'][admin1]['fatalities'] += int(event.get('fatalities', 0))

        # Count by actor
        for event in events:
            for actor_field in ['actor1', 'actor2']:
                actor = event.get(actor_field, '')
                if actor:
                    if actor not in stats['by_actor']:
                        stats['by_actor'][actor] = 0
                    stats['by_actor'][actor] += 1

        return stats

    def get_sudan_admin1_regions(self):
        """Get list of Sudan admin1 regions from ACLED."""
        # Sudan's 18 states
        return [
            'Blue Nile',
            'Central Darfur',
            'East Darfur',
            'Gedaref',
            'Gezira',
            'Kassala',
            'Khartoum',
            'North Darfur',
            'North Kordofan',
            'Northern',
            'Red Sea',
            'River Nile',
            'Sennar',
            'South Darfur',
            'South Kordofan',
            'West Darfur',
            'West Kordofan',
            'White Nile'
        ]
