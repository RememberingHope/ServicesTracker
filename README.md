# SPED Services Tracking Suite

A comprehensive suite of applications for tracking Special Education (SPED) and Multi-Tiered System of Supports (MTSS) services in educational settings.

## 🎯 Overview

This suite consists of four interconnected applications designed to streamline service tracking, data collection, and reporting:

1. **QR Code Maker** - Creates encrypted QR codes for quick service entry
2. **Services Tracker** - Touchscreen kiosk app for logging services via QR scanning
3. **Services Aggregator** - Collects service data from multiple sources via email
4. **Analytics Dashboard** - Interactive data visualization with pivot tables and charts

## 🚀 Quick Start - Building Windows Executables

### Step 1: Install Python

**Recommended: WinPython (Portable, No Admin Rights Required)**
- Download WinPython from: https://winpython.github.io/
- Choose version 3.10 or 3.11 (64-bit)
- Extract to a folder (e.g., `C:\WinPython`)
- No installation needed - fully portable!

**Alternative: Standard Python**
- Download from: https://www.python.org/downloads/
- Version 3.8 or higher required
- ✅ **Important**: Check "Add Python to PATH" during installation

### Step 2: Download This Project

```bash
git clone https://github.com/RememberingHope/ServicesTracker.git
cd ServicesTracker
```

Or download as ZIP from: https://github.com/RememberingHope/ServicesTracker/archive/refs/heads/main.zip

### Step 3: Build the Executables

1. **Install dependencies** (first time only):
   ```batch
   install_requirements.bat
   ```

2. **Build all applications**:
   ```batch
   build_all.bat
   ```

3. **Find your executables** in the `dist\` folder:
   - `ServicesTracker.exe` - Deploy to classroom kiosks
   - `QRCodeMaker.exe` - For administrators
   - `ServicesAggregator.exe` - For data collection
   - Run `run_dashboard.bat` for analytics (requires Python)

## 📁 Project Structure

```
ServicesTracker/
├── Source Code (Python)
│   ├── Services_Tracker.py         # Kiosk application
│   ├── QR_Code_Maker_for_Services_Tracker.py  # QR generator
│   ├── Services_Aggregator.py      # Data collection
│   └── Services_Dashboard.py       # Analytics dashboard
│
├── Build Scripts (Windows)
│   ├── install_requirements.bat    # Install Python packages
│   ├── build_all.bat              # Build all executables
│   ├── build_tracker.bat          # Build tracker only
│   ├── build_qr_maker.bat         # Build QR maker only
│   └── build_aggregator.bat       # Build aggregator only
│
├── Documentation
│   ├── IMPLEMENTATION_BRIEF.md     # Technical documentation
│   ├── BUILD_DEPLOY_README.md     # Detailed build instructions
│   └── DASHBOARD_GUIDE.md         # Dashboard user guide
│
└── Configuration
    ├── requirements.txt            # Python dependencies
    └── *.spec files               # PyInstaller configurations
```

## 🖥️ Deployment Guide

### Classroom Kiosk Setup
1. Copy `ServicesTracker.exe` to kiosk computer
2. Configure on first run:
   - Set PIN (must match QR codes)
   - Configure email settings (SMTP)
3. Create desktop shortcut
4. Optional: Set to auto-start with Windows

### Administrator Setup
1. Copy `QRCodeMaker.exe` and `ServicesAggregator.exe` to admin computer
2. Use QR Code Maker to create service cards
3. Use Services Aggregator to collect data from emails
4. Run `run_dashboard.bat` for analytics

## 🔒 Security Features

- **PIN-based encryption** for QR codes (prevents unauthorized scanning)
- **Local data storage** before transmission
- **Secure credential storage** using Windows Credential Manager
- **Duplicate detection** to prevent data redundancy
- **PBKDF2 key derivation** for enhanced security

## 📊 Analytics Dashboard

The Streamlit-based dashboard provides:
- Interactive pivot tables
- Student progress tracking
- Service delivery heatmaps
- Goal achievement metrics
- Compliance reporting
- Data export capabilities

To run the dashboard:
```batch
run_dashboard.bat
```
Then open http://localhost:8501 in your browser

## 🛠️ Building Individual Components

If you only need to rebuild specific applications:

```batch
build_tracker.bat      # Services Tracker only
build_qr_maker.bat     # QR Code Maker only
build_aggregator.bat   # Services Aggregator only
```

## 📋 System Requirements

### For Running Executables
- Windows 10 or later
- Webcam (for Services Tracker QR scanning)
- Internet connection (for email features)

### For Building from Source
- Python 3.8 or higher
- 500MB free disk space
- Administrator rights NOT required with WinPython

## 🐛 Troubleshooting

### Antivirus Warnings
Windows Defender may flag the executables. This is common with PyInstaller apps.
- Add to Windows Defender exclusions
- Or build from source yourself for trust

### Camera Not Working
- Check camera permissions in Windows Settings
- Ensure no other app is using the camera
- Try unplugging and reconnecting USB camera

### Build Failures
1. Run `clean_build.bat` to remove old files
2. Update PyInstaller: `pip install --upgrade pyinstaller`
3. Ensure all dependencies installed: `pip install -r requirements.txt`

## 📚 Documentation

- [Implementation Brief](IMPLEMENTATION_BRIEF.md) - System architecture and design
- [Build & Deploy Guide](BUILD_DEPLOY_README.md) - Detailed build instructions
- [Dashboard Guide](DASHBOARD_GUIDE.md) - Analytics dashboard documentation
- [Original Requirements](sped_mtss_apps.md) - Initial project specifications

## 🤝 Contributing

This is a public repository. Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is open source and available for educational use. Please respect student privacy and comply with FERPA/COPPA regulations when deploying.

## 🙏 Acknowledgments

Developed to support special education professionals in tracking and improving student services. Built with Python, Tkinter, Streamlit, and various open-source libraries.

---

**Need Help?** Open an issue on GitHub: https://github.com/RememberingHope/ServicesTracker/issues