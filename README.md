# Sudan Data Loader - QGIS Plugin

A comprehensive QGIS plugin for loading, visualizing, and analyzing Sudan administrative boundary data with AI features, modern dashboard, research tools, and integrated humanitarian data sources.

## Version 3.0.0

[![GitHub release](https://img.shields.io/github/v/release/Osman-Geomatics93/sudan_data_loader)](https://github.com/Osman-Geomatics93/sudan_data_loader/releases)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

---

## What's New in v3.0

### New Data Sources
- **OpenStreetMap/Overpass API** - Query POIs (hospitals, schools, roads, buildings)
- **Sentinel Hub Satellite Imagery** - Browse Sentinel-2 with NDVI, true/false color
- **World Bank Indicators** - GDP, population, health, education metrics
- **NASA FIRMS Fire Data** - Real-time fire/hotspot detection
- **IOM Displacement Tracking** - Internal displacement and movement data

### Modern UI
- **Dashboard Panel** - KPI cards with stats and activity log
- **Interactive Charts** - Bar, pie, line charts with matplotlib
- **Dark Mode** - Automatic theme detection with toggle
- **Toast Notifications** - Modern non-blocking alerts
- **Advanced Search** - Fuzzy matching for Arabic transliteration

### AI/Smart Features
- **Natural Language Query** - "Show all localities in Khartoum"
- **Smart Reports** - AI-generated insights and summaries
- **Anomaly Detection** - Z-score and IQR outlier detection
- **Predictive Analytics** - Conflict trend forecasting
- **Data Recommendations** - Smart suggestions based on context

### Research Tools
- **Citation Generator** - APA, BibTeX, Chicago, Harvard, MLA
- **Data Provenance** - Track data lineage and transformations
- **Spatial Statistics** - Moran's I, Getis-Ord Gi*, Nearest Neighbor
- **Publication Export** - Journal templates (Nature, PLOS, Elsevier, etc.)
- **Project Templates** - Pre-configured analysis workflows

### QGIS Deep Integration
- **Processing Provider** - 4 algorithms in QGIS Toolbox
- **Custom Expressions** - 8 Sudan-specific functions
- **Async Operations** - Non-blocking downloads
- **Credential Manager** - Secure API key storage

---

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
- **Dashboard Panel**: KPI cards, quick actions, activity log
- **Charts Panel**: Interactive visualizations with export
- **Search Panel**: Find features by name (English/Arabic) with autocomplete
- **Advanced Search Panel**: Faceted search with fuzzy matching
- **Bookmarks Panel**: Quick navigation to all 18 states + custom bookmarks
- **Statistics Panel**: Area calculations, feature counts, export to CSV
- **Data Info Panel**: Layer information, CRS, extent

### Analysis Tools
- **Query Builder**: Visual attribute query interface
- **AI Natural Language Query**: Query data in plain English
- **Spatial Statistics**: Moran's I autocorrelation analysis
- **Processing Tools**: Clip by State, Buffer, Dissolve, Statistics, Join
- **Data Validation**: Geometry, topology, and attribute checks
- **Anomaly Detection**: Identify outliers and unusual patterns

### Reports & Export
- **Report Generation**: HTML/PDF reports with insights
- **Export Features**: GeoPackage, Shapefile, GeoJSON, KML, CSV, DXF
- **Publication Export**: High-resolution maps for journals
- **Citation Generator**: Academic citation formats

### External Data Sources
- **HDX Integration**: Browse and download humanitarian datasets
  - Health facilities, education, roads, conflict data
  - Direct layer loading to QGIS

- **ACLED Integration**: Armed Conflict Location & Event Data
  - Real-time conflict tracking for Sudan
  - Filter by date, event type, region
  - Color-coded visualization by event type

- **OpenStreetMap**: Query POIs via Overpass API
  - Hospitals, schools, roads, buildings
  - Custom queries for Sudan

- **Sentinel Hub**: Satellite imagery
  - Sentinel-2 imagery browser
  - NDVI, true color, false color composites
  - Cloud cover filtering

- **World Bank**: Development indicators
  - Socio-economic data for Sudan
  - Time series visualization

- **NASA FIRMS**: Fire data
  - Active fire/hotspot detection
  - Last 24h, 48h, 7 days options

- **IOM DTM**: Displacement tracking
  - Internal displacement data
  - Population movement flows

### Drawing Tools
- **Sketching Toolbar**: Draw points, lines, polygons, text annotations

---

## Custom Expression Functions

Use these in Field Calculator, labeling, or styling:

| Function | Description | Example |
|----------|-------------|---------|
| `sudan_state_name(pcode)` | Get state name from P-Code | `sudan_state_name('SD06')` → 'Khartoum' |
| `sudan_state_name_ar(pcode)` | Get Arabic state name | `sudan_state_name_ar('SD06')` → 'الخرطوم' |
| `sudan_state_capital(pcode)` | Get state capital | `sudan_state_capital('SD06')` → 'Khartoum' |
| `sudan_locality_count(state)` | Count localities in state | `sudan_locality_count('Khartoum')` → 7 |
| `sudan_area_km2()` | Calculate area in km² | `sudan_area_km2()` → 22142.5 |
| `sudan_perimeter_km()` | Calculate perimeter in km | `sudan_perimeter_km()` → 850.3 |
| `sudan_is_darfur(state)` | Check if in Darfur region | `sudan_is_darfur('North Darfur')` → True |
| `sudan_region(state)` | Get region name | `sudan_region('Khartoum')` → 'Central' |

---

## Processing Algorithms

Available in **Processing Toolbox** under "Sudan Data":

| Algorithm | Description |
|-----------|-------------|
| **Clip by State** | Clip any layer to a Sudan state boundary |
| **Buffer Analysis** | Create buffers with distance options |
| **Statistics Calculator** | Calculate zonal statistics for Sudan areas |
| **Join Attributes** | Join attributes by location or field |

---

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

---

## Usage

### Menu Location
All features are under: **Sudan Data Loader** menu

```
Sudan Data Loader
├── Load Sudan Data...
├── Load All Layers
├── Download/Update Data
├── ─────────────────
├── Quick Labels →
├── Style Presets →
├── Basemaps →
├── Panels →
│   ├── Dashboard Panel
│   ├── Charts Panel
│   ├── Data Info Panel
│   ├── Search Panel
│   ├── Advanced Search Panel
│   ├── Bookmarks Panel
│   └── Statistics Panel
├── ─────────────────
├── Analysis Tools →
│   ├── Query Builder...
│   ├── Processing Tools...
│   ├── AI Natural Language Query...
│   └── Spatial Statistics...
├── Reports & Export →
│   ├── Generate Report...
│   ├── Export Features...
│   ├── Publication Export...
│   └── Generate Citations...
├── Data Validation...
├── Sketching Toolbar
├── ─────────────────
├── External Data Sources →
│   ├── HDX Humanitarian Data...
│   ├── ACLED Conflict Data...
│   ├── OpenStreetMap Data...
│   ├── Sentinel Satellite Imagery...
│   ├── World Bank Indicators...
│   ├── NASA FIRMS Fire Data...
│   └── IOM Displacement Data...
├── ─────────────────
├── Welcome Wizard...
├── Toggle Dark Mode
└── Settings...
```

### Loading Data
1. **Sudan Data Loader** > **Load Sudan Data...** (select layers)
2. Or **Load All Layers** to load everything

### Natural Language Query
1. **Analysis Tools** > **AI Natural Language Query...**
2. Type queries like:
   - "Show all localities in Khartoum"
   - "Find states with population > 1000000"
   - "Count localities in Darfur"
   - "Zoom to North Darfur"
   - "Select Kassala"

### Settings
**Sudan Data Loader** > **Settings...**
- General: Server URL, auto-update
- Layers: Default layers to load
- Appearance: Style preset, panel visibility
- API Keys: ACLED, Sentinel Hub, NASA FIRMS credentials

---

## Data Layers

| Layer | Description |
|-------|-------------|
| Sudan Admin 0 - Country | National boundary |
| Sudan Admin 1 - States | 18 state boundaries |
| Sudan Admin 2 - Localities | Locality boundaries |
| Sudan Admin Lines | Boundary lines |
| Sudan Admin Points | Administrative points |

---

## Requirements

- QGIS 3.0 or higher
- Internet connection (for download/update, external data sources)
- Optional: matplotlib for charts
- Optional API accounts:
  - ACLED (free registration) for conflict data
  - Sentinel Hub for satellite imagery
  - NASA FIRMS for fire data

---

## Changelog

### v3.0.0 - Major Feature Release
**New Data Sources:**
- OpenStreetMap/Overpass API for POI queries
- Sentinel Hub satellite imagery browser
- World Bank development indicators
- NASA FIRMS fire/hotspot data
- IOM displacement tracking data

**Modern UI:**
- Dashboard panel with KPI cards and activity log
- Interactive charts panel with matplotlib
- Dark mode support with theme detection
- Toast-style notifications
- Advanced search with fuzzy matching

**QGIS Integration:**
- Processing Provider with 4 algorithms
- Async operations via QgsTask
- Secure credential storage
- Layer tree context menus
- 8 custom expression functions

**AI Features:**
- Natural language query parser
- Smart report generator
- Anomaly detection
- Predictive analytics
- Data recommendations

**Research Tools:**
- Citation generator (5 formats)
- Data provenance tracking
- Spatial statistics (Moran's I, Gi*)
- Publication export with journal templates
- Project workflow templates

### v2.3.5 - Bug Fixes
- Fix Processing Tools import issue
- Fix ACLED date filtering
- Fix area calculations

### v2.3.0 - ACLED Integration
- ACLED browser dialog
- Filter by date, event type, region
- Color-coded conflict visualization

### v2.2.0 - Welcome Wizard
- Welcome wizard for first-time users
- HDX category filtering

### v2.1.0 - HDX Integration
- HDX humanitarian data browser
- Featured Sudan datasets

### v2.0.0 - Major Feature Release
- Complete plugin redesign
- Settings, search, bookmarks, statistics panels
- Query builder, export, processing tools
- Report generation, sketching toolbar

### v1.0.0 - Initial Release
- Load Sudan administrative boundaries
- Automatic styling

---

## Contributing

Contributions welcome! Please submit a Pull Request.

## Issues

Report bugs at [Issues](https://github.com/Osman-Geomatics93/sudan_data_loader/issues)

## License

GNU General Public License v3.0 - see [LICENSE](LICENSE)

## Author

**Osman Ibrahim**
- GitHub: [@Osman-Geomatics93](https://github.com/Osman-Geomatics93)
- Email: osmangeomatics93@gmail.com

---

Made with ❤️ for the Sudan GIS community
