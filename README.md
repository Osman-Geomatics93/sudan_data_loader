# Sudan Data Loader - QGIS Plugin

A comprehensive QGIS plugin for loading, visualizing, and analyzing Sudan administrative boundary data with integrated humanitarian and conflict data sources.

## Version 2.3.4

## Features

### Data Loading
- **Administrative Boundaries**: Country (Admin 0), States (Admin 1), Localities (Admin 2)
- **Additional Layers**: Administrative lines and points
- **Automatic Styling**: QML styles applied automatically
- **Download/Update**: Fetch latest data from GitHub releases
- **Layer Selection**: Choose which layers to load

### Quick Tools
- **Quick Labels**: One-click labeling (English, Arabic, P-Codes)
- **Style Presets**: Default, Satellite-Friendly, Grayscale, Humanitarian themes
- **Basemaps**: OpenStreetMap, ESRI Satellite, Humanitarian OSM, CartoDB

### Panels
- **Search Panel**: Find features by name (English/Arabic) with autocomplete
- **Bookmarks Panel**: Quick navigation to all 18 states + custom bookmarks
- **Statistics Panel**: Area calculations, feature counts, export to CSV
- **Data Info Panel**: Layer information, CRS, extent

### Analysis Tools
- **Query Builder**: Visual attribute query interface
- **Export Features**: GeoPackage, Shapefile, GeoJSON, KML, CSV, DXF
- **Processing Tools**: Clip by State, Buffer, Dissolve, Intersection
- **Data Validation**: Geometry, topology, and attribute checks
- **Report Generation**: HTML/PDF reports

### Drawing Tools
- **Sketching Toolbar**: Draw points, lines, polygons, text annotations

### External Data Sources
- **HDX Integration**: Browse and download humanitarian datasets from HDX
  - Health facilities, education, roads, conflict data
  - Direct layer loading to QGIS

- **ACLED Integration**: Armed Conflict Location & Event Data
  - Real-time conflict tracking for Sudan
  - Filter by date, event type, region
  - Color-coded visualization by event type
  - Statistics and event details
  - *Note: Free accounts access data older than 12 months*

## Installation

### From QGIS Plugin Manager (Recommended)
1. Open QGIS
2. Go to **Plugins** > **Manage and Install Plugins**
3. Search for "Sudan Data Loader"
4. Click **Install**

### Manual Installation
1. Download the latest release from [Releases](https://github.com/Osman-Geomatics93/sudan_data_loader/releases)
2. In QGIS: **Plugins** > **Manage and Install Plugins** > **Install from ZIP**
3. Select the downloaded zip file

## Usage

### Menu Location
All features are under: **Sudan Data Loader** menu

### Loading Data
1. **Sudan Data Loader** > **Load Sudan Data...** (select layers)
2. Or **Load All Layers** to load everything

### Settings
**Sudan Data Loader** > **Settings...**
- General: Server URL, auto-update
- Layers: Default layers to load
- Appearance: Style preset, panel visibility
- API Keys: ACLED credentials

### ACLED Conflict Data
1. Register free at https://acleddata.com/
2. Go to **Settings** > **API Keys** tab
3. Enter your email and password
4. Open **External Data Sources** > **ACLED Conflict Data...**
5. Select date range (data older than 12 months for free accounts)
6. Click **Fetch Conflict Data**
7. Click **Add to Map**

### HDX Humanitarian Data
1. **External Data Sources** > **HDX Humanitarian Data...**
2. Browse featured datasets or search
3. Click **Download** then **Add to Map**

## Data Layers

| Layer | Description |
|-------|-------------|
| Sudan Admin 0 - Country | National boundary |
| Sudan Admin 1 - States | 18 state boundaries |
| Sudan Admin 2 - Localities | Locality boundaries |
| Sudan Admin Lines | Boundary lines |
| Sudan Admin Points | Administrative points |

## Requirements

- QGIS 3.0 or higher
- Internet connection (for download/update, HDX, ACLED)
- ACLED account for conflict data (free registration)

## Changelog

### v2.3.4 - ACLED API Working
- Fix ACLED API endpoint URL
- OAuth authentication working correctly
- Debug logging for troubleshooting

### v2.3.3 - ACLED Credentials Clarification
- Clarify ACLED uses account email/password

### v2.3.2 - ACLED API Fix
- Update to new OAuth-based API endpoint

### v2.3.1 - ACLED API Key Settings
- Add API Keys tab to Settings dialog

### v2.3.0 - ACLED Conflict Data Integration
- ACLED browser dialog
- Filter by date, event type, region
- Color-coded conflict visualization

### v2.2.0 - Welcome Wizard & UX
- Welcome wizard for first-time users
- HDX category filtering
- Real-time search filtering

### v2.1.0 - HDX Integration
- HDX humanitarian data browser
- Featured Sudan datasets

### v2.0.0 - Major Feature Release
- Settings dialog
- Layer selection
- Quick labels (English/Arabic/P-Codes)
- Style presets (4 themes)
- Search panel with autocomplete
- Bookmarks panel (18 states + custom)
- Statistics panel
- Query builder
- Basemap integration (7 options)
- Report generation (HTML/PDF)
- Export dialog (6 formats)
- Sketching toolbar
- Processing tools
- Data validation

### v1.0.0 - Initial Release
- Load Sudan administrative boundaries
- Automatic styling
- Download/Update from GitHub

## Contributing

Contributions welcome! Submit a Pull Request.

## Issues

Report bugs at [Issues](https://github.com/Osman-Geomatics93/sudan_data_loader/issues)

## License

GNU General Public License v3.0 - see [LICENSE](LICENSE)

## Author

**Osman Ibrahim**
- GitHub: [@Osman-Geomatics93](https://github.com/Osman-Geomatics93)
- Email: osmangeomatics93@gmail.com

---

Made with support from the Sudan GIS community
