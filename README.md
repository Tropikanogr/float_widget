# Float_Clock ⏰📈

A sophisticated floating desktop widget that combines real-time market clock functionality with stock data lookup capabilities.

## 🌟 Features

### 🕐 Advanced Clock Display
- **Dual Time Zones**: Greece (red) and New York (cyan) time display
- **Market Session Tracking**: Real-time NYSE market status
  - **PRE**: Pre-market (04:00-09:30 ET)
  - **RTH**: Regular trading hours (09:30-16:00 ET)
  - **AFTER**: After-hours (16:00-20:00 ET)
  - **CLOSED**: Market closed
- **Countdown Timers**: Time remaining to next market events
- **Color-coded Status Dot**: Visual indicator of current market phase

### 📊 Stock Data Lookup
- **Float Analysis**: Shares float, volume, short float, short ratio
- **52-Week Data**: High and low price ranges
- **Real-time Data**: Live data from Finviz
- **Greek Interface**: Localized Greek language support

### 🎛️ Interactive Features
- **Drag & Drop**: Move widget anywhere on screen
- **Always on Top**: Stays visible over other applications
- **Opacity Control**: Adjustable transparency (70%, 85%, 100%)
- **Compact Mode**: Toggle between compact and detailed view
- **Sound Notifications**: Audio alerts for market phase changes
- **Voice Notifications**: Text-to-speech market status updates
- **Context Menu**: Right-click for quick access to settings

## 🚀 Quick Start

### Option 1: Run Executable (Recommended)
1. Download `Float_Clock.exe`
2. Double-click to run
3. No installation required!

### Option 2: Run from Source
```bash
# Install dependencies
pip install requests beautifulsoup4 lxml pyttsx3

# Run the application
python Float_Clock.py
```

### Option 3: Build Executable
```bash
# Build with PyInstaller
pyinstaller Float_Clock.spec

# Executable will be created in dist/Float_Clock.exe
```

## 📖 Usage Guide

### Clock Interface
- **Top Section**: Shows Greece and New York times with market status
- **Status Dot**: Color indicates current market phase
  - 🟢 Green: Regular trading hours
  - 🟡 Yellow: Pre-market
  - 🔵 Blue: After-hours
  - 🟣 Purple: Market closed

### Stock Lookup
1. **Enter Ticker**: Type any stock symbol (e.g., AAPL, TSLA)
2. **Press Enter** or click "Αναζήτηση" (Search)
3. **View Data**: Float, volume, short data, 52-week ranges and company info

### Controls
- **Left Click + Drag**: Move widget around screen
- **Right Click**: Open context menu
- **Enter Key**: Search for stock data

### Context Menu Options
- **Toggle compact**: Switch between compact/detailed view
- **Opacity settings**: 70%, 85%, or 100% transparency
- **Sound/Voice toggles**: Enable/disable notifications
- **Copy times**: Copy current times to clipboard
- **Quit**: Close application

## 🛠️ Technical Details

### Requirements
- **Python 3.11+** (for source code)
- **Windows 10/11** (for executable)
- **Internet connection** (for stock data)

### Dependencies
- `tkinter`: GUI framework
- `requests`: HTTP requests for stock data
- `beautifulsoup4`: HTML parsing
- `lxml`: XML/HTML parser
- `pyttsx3`: Text-to-speech (optional)
- `winsound`: Windows sound (optional)

### Market Hours (ET)
- **Pre-market**: 04:00 - 09:30
- **Regular**: 09:30 - 16:00
- **After-hours**: 16:00 - 20:00
- **Closed**: 20:00 - 04:00 (next day)

## 📁 Project Structure

```
Float_Clock/
├── README.md              # This file
└── Float_Clock.exe    # Final executable
```

## 🎯 Perfect For

- **Day Traders**: Real-time market timing
- **Stock Analysts**: Quick float,volume and info data
- **International Traders**: Greece/NY time coordination
- **Desktop Users**: Always-visible market widget

## 🔧 Customization

### Colors
The widget uses a dark theme with color-coded elements:
- Background: `#121212` (dark gray)
- Text: `#FFFFFF` (white)
- Greece Time: `#FF6B6B` (red)
- New York Time: `#4ECDC4` (cyan)
- Market phases: Green/Yellow/Blue/Purple

### Positioning
The widget automatically positions itself in the bottom-right corner but can be dragged anywhere.

## 🐛 Troubleshooting

### Common Issues
1. **"Module not found"**: Install missing dependencies
2. **No stock data**: Check internet connection
3. **No sound**: Windows sound system required
4. **No voice**: Install `pyttsx3` for TTS features

### Error Messages
- `"Σφάλμα ανάκτησης"`: Data retrieval error (Greek)
- `"Please enter a ticker symbol"`: Empty input field

## 📝 Version History

- **v1.0.0**: Initial release with clock and stock lookup
- Combined Tropi clock with float widget functionality
- Added drag-and-drop, opacity controls, and notifications

-**v 1.1.3
-added ticker info functionality
-added self updating function from git hub

## 🤝 Contributing

This is a personal project combining two existing widgets:
- **Tropi Clock**: Advanced market timing widget
- **Float Widget**: Stock data lookup tool

## 📄 License

Personal use project - combining existing open-source components.

---

**Float_Clock** - Your ultimate trading companion! ⏰📈🚀
TropikanoGR
