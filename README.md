# Sudan Data Loader - QGIS Plugin

A QGIS plugin for loading Sudan administrative boundary data with automatic updates from GitHub releases.

## Features

- **Load Administrative Boundaries**: Country (Admin 0), States (Admin 1), Localities (Admin 2)
- **Additional Layers**: Administrative lines and points
- **Automatic Styling**: QML styles applied automatically to each layer
- **Download/Update**: Fetch latest data from GitHub releases
- **Secure Downloads**: SHA256 hash verification for data integrity
- **Offline Support**: Bundled data included for offline use

## Installation

### From QGIS Plugin Manager (Recommended)
1. Open QGIS
2. Go to **Plugins** > **Manage and Install Plugins**
3. Search for "Sudan Data Loader"
4. Click **Install**

### Manual Installation
1. Download the latest release from [Releases](https://github.com/Osman-Geomatics93/sudan_data_loader/releases)
2. Extract to your QGIS plugins folder:
   - **Windows**: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
   - **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
   - **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
3. Restart QGIS
4. Enable the plugin in **Plugins** > **Manage and Install Plugins**

## Usage

### Loading Data
1. Click the **"Load Sudan Admin Data"** button in the toolbar
2. Or go to **Vector** > **Sudan Data Downloader** > **Load Sudan Admin Data**
3. All layers will be loaded and styled automatically

### Updating Data
1. Click the **"Download/Update Sudan Data"** button in the toolbar
2. The plugin will check for updates from GitHub
3. If an update is available, it will download and extract automatically
4. Downloaded data is cached locally for future use

## Data Layers

| Layer | Description | Style |
|-------|-------------|-------|
| Sudan Admin 0 - Country | National boundary | Yes |
| Sudan Admin 1 - States | State boundaries | Yes |
| Sudan Admin 2 - Localities | Locality boundaries | Yes |
| Sudan Admin Lines | Administrative boundary lines | No |
| Sudan Admin Points | Administrative points | No |

## Data Storage

- **Bundled Data**: Included with plugin installation
- **Cached Data**: Downloaded to user's application data folder
  - Windows: `%APPDATA%\<QGIS>\sudan_data_loader\`
  - Linux: `~/.local/share/QGIS/QGIS3/sudan_data_loader/`
  - macOS: `~/Library/Application Support/QGIS/QGIS3/sudan_data_loader/`

## Requirements

- QGIS 3.0 or higher
- Internet connection (for download/update feature only)

## Technical Details

### Version Checking
The plugin fetches version information from:
```
https://raw.githubusercontent.com/Osman-Geomatics93/sudan_data_loader/master/version.json
```

### Data Format
- **Vector Data**: GeoPackage (.gpkg)
- **Styles**: QGIS QML format (.qml)

### Security Features
- SHA256 hash verification for downloaded files
- Zip-slip protection to prevent path traversal attacks

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Issues

Report bugs or request features at [Issues](https://github.com/Osman-Geomatics93/sudan_data_loader/issues)

## License

This project is open source. See the repository for license details.

## Author

**Osman Ibrahim**
- GitHub: [@Osman-Geomatics93](https://github.com/Osman-Geomatics93)
- Email: osmangeomatics93@gmail.com

## Changelog

### v1.0.0 (Initial Release)
- Load Sudan administrative boundaries from GeoPackages
- Apply QML styles automatically
- Download/Update feature with GitHub releases integration
- SHA256 hash verification
- Zip-slip protection for secure extraction

---

Made with support from the Sudan GIS community
