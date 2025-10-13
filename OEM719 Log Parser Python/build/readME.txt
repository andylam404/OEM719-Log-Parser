# OEM719 GPS Log Parser - Executable

## Quick Start

1. Place the OEM719 Simulated Log.txt file in the same directory as this executable
2. Double-click OEM719_Parser.exe to run
3. CSV output files will be created in a "test_data" folder

## What This Does

This executable parses OEM719 GPS receiver log files and creates separate CSV files for each message type:
- BESTXYZ.csv - Position and velocity solutions
- GPS TIME.csv - Time messages
- GPS PSRDOP.csv - Position dilution of precision
- GPS HWMONITOR.csv - Hardware monitoring data
- GPS GPGSV.csv - GPS satellites in view
- GPS RAW DATA.csv - All raw messages

## Requirements

- Windows PC (no Python installation needed)
- OEM719 Simulated Log.txt file
- ~10 MB free disk space for output files

## Configuration

The parser automatically:
- Starts from 1MB offset OR when GPS lock is detected (FINESTEERING status)
- Captures data at 1Hz frequency
- Stops after 30 seconds of data

## File Structure

Expected directory structure:
OEM719_Parser.exe
OEM719 Simulated Log.txt (input file)
test_data/ (output folder - created automatically)
  BESTXYZ.csv
  GPS TIME.csv
  GPS PSRDOP.csv
  GPS HWMONITOR.csv
  GPS GPGSV.csv
  GPS RAW DATA.csv

## Troubleshooting

Problem: "File not found" error
Solution: Ensure OEM719 Simulated Log.txt is in the correct location

Problem: Executable won't run
Solution:
- Check Windows Defender/antivirus settings
- Right-click > Properties > Unblock if file is blocked
- Run as administrator if needed

Problem: No CSV files generated
Solution: Check that you have write permissions in the current directory

## Technical Details

- Built with Python 3.10 and PyInstaller 6.16.0
- Standalone executable (no external dependencies)
- Console application - shows progress during parsing
- Executable size: ~3 MB

## Support

For issues or questions, refer to the full documentation in:
- README.md (detailed user guide)
- DEPLOYMENT.md (deployment guide)
- Source code in src/ folder

## Version

Version: 1.0
Build Date: October 11, 2025