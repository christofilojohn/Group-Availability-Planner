# Group Availability Planner

The perfect companion app to find an optimal meeting time in your groupchat.
Send your schedule, receive theirs, and that's it !
Simple, local scheduling - No cloud, no logging, everything is free!
Just share your .tsv s in as groupchat and let the app do the rest. 

[![Download](https://img.shields.io/github/v/release/christofilojohn/Group-Availability-Planner?label=Download&color=blueviolet)](https://github.com/christofilojohn/Group-Availability-Planner/releases/latest)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20|%20macOS%20|%20Linux-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

![My Project Screenshot](images/app.png)

## Features

**Create Schedules**
- Drag to select availability (9 AM – 7 PM, Mon–Sun)
- Export as shareable TSV files

**Find Overlaps**
- Load multiple schedules at once
- Color-coded heatmap shows availability
- Click any slot to see who's free

**Smart Analytics**
- Best meeting times ranked by availability
- Per-person breakdown
- Day/hour pattern analysis

**Export to Calendar (Coming Soon)**
- Select final meeting times
- Export as iCal (.ics) with weekly recurrence
- Works with Apple Calendar, Google Calendar, Outlook

## Quick Start

```bash
python3 planner.py
```

**Requirements:** Python 3.8+ with tkinter (included on macOS/Windows; Linux: `sudo apt install python3-tk`)

## Workflow

1. **Each participant** creates their schedule → exports TSV
2. **Organizer** loads all TSV files → views overlaps
3. **Right-click** to select meeting times → export to iCal

## Why This?

| | Group Availability Planner | Online Tools |
|---|---|---|
| Privacy | 100% local | Cloud-based |
| Accounts | None needed | Required |
| Offline | ✓ | ✗ |
| Calendar Export | Native iCal | Limited |
| Cost | Free | Often freemium |
| Ease of Use | Medium | ✓ |

## PyInstaller app distribution guide:

### Windows:
pyinstaller --noconfirm --onefile --windowed --icon "images/app.ico" --name "GroupAvailabilityPlanner" "planner.py"

### MacOS:
pyinstaller --noconfirm --onedir --windowed --icon "images/app.icns" --name "GroupAvailabilityPlanner" "planner.py"

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
