# -*- coding: utf-8 -*-
"""
IOM Browser Dialog for Sudan Data Loader.

Provides a UI for browsing IOM Displacement Tracking Matrix data for Sudan.
"""

import os
from datetime import datetime

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QGroupBox, QLabel, QComboBox, QPushButton,
    QProgressBar, QMessageBox, QListWidget, QListWidgetItem,
    QFormLayout, QTextEdit, QSplitter, QLineEdit
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor, QDesktopServices
from qgis.core import QgsVectorLayer, QgsProject

from .iom_client import IOMClient


class IOMBrowserDialog(QDialog):
    """Dialog for browsing IOM DTM displacement data for Sudan."""

    def __init__(self, iface, parent=None):
        """
        Initialize the IOM browser dialog.

        :param iface: QGIS interface instance
        :param parent: Parent widget
        """
        super().__init__(parent)
        self.iface = iface
        self.client = IOMClient()
        self.current_datasets = []
        self.current_resources = []
        self.pending_layers = []

        self.setWindowTitle('IOM Displacement Tracking - Sudan')
        self.setMinimumSize(900, 700)
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel('IOM Displacement Tracking Matrix (DTM)')
        header.setStyleSheet('font-size: 16px; font-weight: bold; padding: 10px;')
        layout.addWidget(header)

        # Info text
        info_text = QLabel(
            'Access displacement data from the International Organization for Migration (IOM).\n'
            'Data includes IDP populations, camp locations, and mobility tracking.'
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet('color: gray; padding: 5px;')
        layout.addWidget(info_text)

        # Tab widget
        tabs = QTabWidget()
        tabs.addTab(self._create_featured_tab(), 'Featured Datasets')
        tabs.addTab(self._create_search_tab(), 'Search Datasets')
        tabs.addTab(self._create_about_tab(), 'About DTM')
        layout.addWidget(tabs)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel('Ready')
        self.status_label.setStyleSheet('color: gray;')
        layout.addWidget(self.status_label)

        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton('Close')
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def _create_featured_tab(self):
        """Create the featured datasets tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Splitter
        splitter = QSplitter(Qt.Horizontal)

        # Left panel - Dataset list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Category filter
        filter_group = QGroupBox('Filter by Category')
        filter_layout = QHBoxLayout(filter_group)

        self.category_combo = QComboBox()
        self.category_combo.addItem('All Categories', None)
        for category in self.client.get_categories():
            self.category_combo.addItem(category, category)
        self.category_combo.currentIndexChanged.connect(self._filter_featured)
        filter_layout.addWidget(self.category_combo)

        left_layout.addWidget(filter_group)

        # Dataset list
        datasets_group = QGroupBox('Available Datasets')
        datasets_layout = QVBoxLayout(datasets_group)

        self.featured_list = QListWidget()
        self.featured_list.currentItemChanged.connect(self._on_featured_selected)
        datasets_layout.addWidget(self.featured_list)

        # Refresh button
        refresh_btn = QPushButton('Refresh from HDX')
        refresh_btn.clicked.connect(self._refresh_featured)
        datasets_layout.addWidget(refresh_btn)

        left_layout.addWidget(datasets_group)
        splitter.addWidget(left_widget)

        # Right panel - Details and resources
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Dataset info
        info_group = QGroupBox('Dataset Information')
        info_layout = QVBoxLayout(info_group)

        self.featured_info_label = QLabel('Select a dataset to see details')
        self.featured_info_label.setWordWrap(True)
        info_layout.addWidget(self.featured_info_label)

        right_layout.addWidget(info_group)

        # Resources
        resources_group = QGroupBox('Available Resources')
        resources_layout = QVBoxLayout(resources_group)

        self.resources_list = QListWidget()
        self.resources_list.itemDoubleClicked.connect(self._download_resource)
        resources_layout.addWidget(self.resources_list)

        # Resource actions
        res_btn_layout = QHBoxLayout()

        self.download_btn = QPushButton('Download Selected')
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self._download_resource)
        res_btn_layout.addWidget(self.download_btn)

        self.add_map_btn = QPushButton('Download && Add to Map')
        self.add_map_btn.setEnabled(False)
        self.add_map_btn.clicked.connect(lambda: self._download_resource(add_to_map=True))
        res_btn_layout.addWidget(self.add_map_btn)

        resources_layout.addLayout(res_btn_layout)
        right_layout.addWidget(resources_group)

        splitter.addWidget(right_widget)
        splitter.setSizes([350, 500])

        layout.addWidget(splitter)

        # Populate featured datasets
        self._populate_featured()

        return widget

    def _create_search_tab(self):
        """Create the search tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Search box
        search_group = QGroupBox('Search HDX for Displacement Data')
        search_layout = QHBoxLayout(search_group)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Enter search terms (e.g., "IDP camps", "refugees")')
        self.search_input.returnPressed.connect(self._search_datasets)
        search_layout.addWidget(self.search_input)

        search_btn = QPushButton('Search')
        search_btn.clicked.connect(self._search_datasets)
        search_layout.addWidget(search_btn)

        layout.addWidget(search_group)

        # Search results
        results_group = QGroupBox('Search Results')
        results_layout = QVBoxLayout(results_group)

        self.search_results_list = QListWidget()
        self.search_results_list.itemDoubleClicked.connect(self._on_search_result_clicked)
        results_layout.addWidget(self.search_results_list)

        # Result info
        self.search_info_label = QLabel('Enter search terms and click Search')
        self.search_info_label.setWordWrap(True)
        self.search_info_label.setStyleSheet('color: gray;')
        results_layout.addWidget(self.search_info_label)

        layout.addWidget(results_group)

        return widget

    def _create_about_tab(self):
        """Create the about tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setHtml("""
        <h2>About the Displacement Tracking Matrix (DTM)</h2>

        <p>The Displacement Tracking Matrix (DTM) is a system to track and monitor
        population displacement and mobility. It is designed to regularly and
        systematically capture, process and disseminate information to provide
        a better understanding of the movements and evolving needs of displaced
        populations.</p>

        <h3>Data Components</h3>
        <ul>
            <li><b>Baseline Assessment:</b> Comprehensive assessment of displacement
                sites including population counts, demographics, and needs.</li>
            <li><b>Mobility Tracking:</b> Monitoring of population movements and
                flow patterns.</li>
            <li><b>Event Tracking:</b> Documentation of displacement events and
                emergency situations.</li>
            <li><b>Multi-sectoral Location Assessment:</b> Detailed assessment of
                conditions and services at displacement sites.</li>
        </ul>

        <h3>Sudan Context</h3>
        <p>Sudan has experienced significant internal displacement due to conflict,
        particularly in Darfur, Kordofan, Blue Nile, and more recently Khartoum
        and other areas. DTM data helps humanitarian organizations understand
        displacement patterns and plan response activities.</p>

        <h3>Data Sources</h3>
        <p>Data is sourced from:</p>
        <ul>
            <li>IOM DTM Sudan operations</li>
            <li>UNHCR refugee data</li>
            <li>OCHA humanitarian datasets</li>
            <li>Partner organization assessments</li>
        </ul>

        <h3>Links</h3>
        <p>
        <a href="https://dtm.iom.int/sudan">DTM Sudan Portal</a><br>
        <a href="https://data.humdata.org/organization/iom">IOM on HDX</a><br>
        <a href="https://displacement.iom.int">Global Displacement Data</a>
        </p>
        """)
        layout.addWidget(about_text)

        # Quick links
        links_layout = QHBoxLayout()

        dtm_btn = QPushButton('Open DTM Sudan Portal')
        dtm_btn.clicked.connect(lambda: QDesktopServices.openUrl(
            Qt.QUrl('https://dtm.iom.int/sudan')))
        links_layout.addWidget(dtm_btn)

        hdx_btn = QPushButton('Browse IOM on HDX')
        hdx_btn.clicked.connect(lambda: QDesktopServices.openUrl(
            Qt.QUrl('https://data.humdata.org/organization/iom')))
        links_layout.addWidget(hdx_btn)

        layout.addLayout(links_layout)

        return widget

    def connect_signals(self):
        """Connect client signals."""
        self.client.data_loaded.connect(self._on_data_loaded)
        self.client.datasets_loaded.connect(self._on_datasets_loaded)
        self.client.error_occurred.connect(self._on_error)
        self.client.progress_update.connect(self._on_progress)

    def _populate_featured(self):
        """Populate featured datasets list."""
        self.featured_list.clear()

        for dataset in self.client.get_featured_datasets():
            item = QListWidgetItem(dataset['name'])
            item.setData(Qt.UserRole, dataset)
            item.setToolTip(dataset.get('description', ''))

            # Color by category
            color = self.client.get_category_color(dataset.get('category', ''))
            item.setForeground(QColor(color))

            self.featured_list.addItem(item)

    def _filter_featured(self):
        """Filter featured datasets by category."""
        category = self.category_combo.currentData()

        for i in range(self.featured_list.count()):
            item = self.featured_list.item(i)
            dataset = item.data(Qt.UserRole)

            if category is None or dataset.get('category') == category:
                item.setHidden(False)
            else:
                item.setHidden(True)

    def _refresh_featured(self):
        """Refresh featured datasets from HDX."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.status_label.setText('Searching HDX for displacement datasets...')

        self.client.search_dtm_datasets('displacement IDP')

    def _on_featured_selected(self, current, previous):
        """Handle featured dataset selection."""
        if current:
            dataset = current.data(Qt.UserRole)
            self.featured_info_label.setText(
                f"<b>{dataset['name']}</b><br><br>"
                f"<b>Category:</b> {dataset.get('category', 'N/A')}<br><br>"
                f"<b>Description:</b> {dataset.get('description', 'N/A')}<br><br>"
                f"<b>HDX ID:</b> {dataset.get('id', 'N/A')}"
            )

            # Fetch resources
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            self.client.get_dataset_details(dataset.get('id', ''))

    def _on_data_loaded(self, data):
        """Handle data loaded signal."""
        self.progress_bar.setVisible(False)

        # Update resources list
        self.resources_list.clear()
        self.current_resources = data.get('resources', [])

        for res in self.current_resources:
            item = QListWidgetItem(f"{res['name']} ({res['format']})")
            item.setData(Qt.UserRole, res)
            self.resources_list.addItem(item)

        if self.current_resources:
            self.download_btn.setEnabled(True)
            self.add_map_btn.setEnabled(True)
            self.status_label.setText(f"Found {len(self.current_resources)} resources")
        else:
            self.download_btn.setEnabled(False)
            self.add_map_btn.setEnabled(False)
            self.status_label.setText("No GIS resources found")

    def _on_datasets_loaded(self, datasets):
        """Handle datasets loaded signal."""
        self.progress_bar.setVisible(False)
        self.current_datasets = datasets

        # Update search results
        self.search_results_list.clear()
        for dataset in datasets:
            item = QListWidgetItem(dataset['title'])
            item.setData(Qt.UserRole, dataset)
            item.setToolTip(dataset.get('description', '')[:200])
            self.search_results_list.addItem(item)

        self.status_label.setText(f"Found {len(datasets)} datasets")

    def _on_error(self, error):
        """Handle error signal."""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Error: {error}")
        QMessageBox.warning(self, 'Error', error)

    def _on_progress(self, message):
        """Handle progress update."""
        self.status_label.setText(message)

    def _search_datasets(self):
        """Search for datasets."""
        query = self.search_input.text().strip()
        if not query:
            query = 'displacement'

        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.client.search_dtm_datasets(query)

    def _on_search_result_clicked(self, item):
        """Handle search result double-click."""
        dataset = item.data(Qt.UserRole)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.client.get_dataset_details(dataset.get('id', ''))

        self.search_info_label.setText(
            f"<b>{dataset['title']}</b><br><br>"
            f"<b>Organization:</b> {dataset.get('organization', 'N/A')}<br>"
            f"<b>Last Modified:</b> {dataset.get('last_modified', 'N/A')[:10]}"
        )

    def _download_resource(self, add_to_map=False):
        """Download selected resource."""
        current = self.resources_list.currentItem()
        if not current:
            if self.resources_list.count() > 0:
                current = self.resources_list.item(0)
            else:
                QMessageBox.warning(self, 'No Resource', 'Please select a resource to download.')
                return

        resource = current.data(Qt.UserRole)
        url = resource.get('url', '')

        if not url:
            QMessageBox.warning(self, 'No URL', 'Resource URL not available.')
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        filepath = self.client.download_resource(url)

        self.progress_bar.setVisible(False)

        if filepath:
            self.status_label.setText(f"Downloaded: {os.path.basename(filepath)}")

            if add_to_map:
                self.pending_layers.append({
                    'file_path': filepath,
                    'resource': resource
                })
        else:
            self.status_label.setText("Download failed")

    def get_pending_layers(self):
        """Get pending layers to add."""
        return self.pending_layers

    def add_layer_to_map(self, file_path, resource):
        """
        Add downloaded resource to map.

        :returns: Tuple of (success, layer_name or error)
        """
        try:
            layer_name = f"IOM - {resource.get('name', 'Displacement Data')}"
            layer = QgsVectorLayer(file_path, layer_name, 'ogr')

            if not layer.isValid():
                return False, f"Failed to load: {file_path}"

            QgsProject.instance().addMapLayer(layer)
            return True, layer_name

        except Exception as e:
            return False, str(e)
