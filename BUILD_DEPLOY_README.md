# SPED Services Tracker - Build & Deployment Guide

## Quick Start (Building Executables)

1. **Install Python** (if not already installed)
   - Download Python 3.8+ from python.org
   - During installation, CHECK "Add Python to PATH"

2. **Install Dependencies**
   ```batch
   install_requirements.bat
   ```

3. **Build All Executables**
   ```batch
   build_all.bat
   ```

4. **Find Your Executables**
   - Look in the `dist\` folder
   - You'll find three .exe files ready to deploy

## File Structure

```
ServicesTracker/
├── Python Source Files
│   ├── Services_Tracker.py         # Kiosk app source
│   ├── QR_Code_Maker_for_Services_Tracker.py  # QR maker source
│   └── Services_Aggregator.py      # Dashboard source
│
├── Build Scripts (Run These)
│   ├── install_requirements.bat    # Step 1: Install dependencies
│   ├── build_all.bat               # Step 2: Build all apps
│   ├── build_tracker.bat           # Build tracker only
│   ├── build_qr_maker.bat          # Build QR maker only
│   ├── build_aggregator.bat        # Build aggregator only
│   └── clean_build.bat             # Clean up build files
│
├── Build Configuration
│   ├── ServicesTracker.spec        # PyInstaller config for tracker
│   ├── QRCodeMaker.spec            # PyInstaller config for QR maker
│   ├── ServicesAggregator.spec     # PyInstaller config for aggregator
│   └── requirements.txt            # Python dependencies
│
└── dist/                           # Created after building
    ├── ServicesTracker.exe         # Kiosk app executable
    ├── QRCodeMaker.exe             # QR maker executable
    └── ServicesAggregator.exe      # Dashboard executable
```

## Building Individual Apps

If you only need to rebuild one app:

```batch
build_tracker.bat      # Builds Services Tracker only
build_qr_maker.bat     # Builds QR Code Maker only  
build_aggregator.bat   # Builds Services Aggregator only
```

## Deployment Instructions

### For Admin Computer (QR Maker + Aggregator)

1. Copy these files to the admin computer:
   - `QRCodeMaker.exe`
   - `ServicesAggregator.exe`

2. Create desktop shortcuts for easy access

3. First run setup:
   - **QR Code Maker**: Enter PIN when creating QR codes
   - **Services Aggregator**: Configure email settings for data collection

### For Classroom Kiosks (Services Tracker)

1. Copy `ServicesTracker.exe` to each kiosk computer

2. First run setup:
   - Set the same PIN used when creating QR codes
   - Configure SMTP email settings (Microsoft 365 or Gmail)
   - Test by scanning a QR code

3. For kiosk mode:
   - Create a shortcut to `ServicesTracker.exe`
   - Place in Windows Startup folder for auto-launch
   - Consider using Windows Kiosk Mode or assigned access

## Troubleshooting

### Antivirus Warnings

Windows Defender or antivirus may flag the executables as suspicious. This is common with PyInstaller apps.

**Solutions:**
- Add executables to antivirus whitelist
- Sign the executables with a code signing certificate
- Submit to Microsoft for reputation building

### Missing DLL Errors

If you see "DLL not found" errors:
1. Install Visual C++ Redistributables
2. Try rebuilding with `--onedir` instead of `--onefile`

### Camera Not Working (Services Tracker)

Ensure:
- Webcam drivers are installed
- Camera permissions are granted in Windows Settings
- No other app is using the camera

### Build Failures

If building fails:
1. Run `clean_build.bat` to remove old files
2. Update PyInstaller: `pip install --upgrade pyinstaller`
3. Check Python version (3.8+ required)

## Advanced Options

### Adding Icons

1. Create or obtain .ico files for each app
2. Place in project directory
3. Update spec files:
   ```python
   icon='your_icon.ico'
   ```
4. Rebuild with `build_all.bat`

### Reducing File Size

Edit spec files to enable UPX compression:
```python
upx=True,
upx_dir='C:\\path\\to\\upx',  # Download UPX separately
```

### Creating an Installer

Consider using:
- **NSIS** - Free, scriptable installer
- **Inno Setup** - Free, GUI-based installer
- **WiX Toolset** - Professional MSI creator

## Version Management

When updating the apps:
1. Update the Python source files
2. Run `build_all.bat` to create new executables
3. Test thoroughly before deployment
4. Keep old versions as backup

## Security Notes

- Executables include Python interpreter and all dependencies
- PIN encryption is built-in but uses shared secret model
- Consider code signing for enterprise deployment
- Test in isolated environment before production use

## Support

Refer to:
- `IMPLEMENTATION_BRIEF.md` - System architecture and design
- `sped_mtss_apps.md` - Original requirements
- PyInstaller docs: https://pyinstaller.org/

## Quick Commands Reference

```batch
# First time setup
install_requirements.bat

# Build everything
build_all.bat

# Clean and rebuild
clean_build.bat
build_all.bat

# Test executables
cd dist
ServicesTracker.exe
QRCodeMaker.exe
ServicesAggregator.exe
```

---

*Last Updated: [Current Date]*
*Version: 1.0*