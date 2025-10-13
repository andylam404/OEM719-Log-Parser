# OEM719 GPS Log Parser - Python

A modular Python application for parsing OEM719 GPS receiver log files into separate CSV files by message type.

## Features

- ✅ **1MB offset** - Starts parsing from 1,000,000 bytes into the file
- ✅ **GPS lock detection** - Detects FINESTEERING status
- ✅ **1Hz frequency** - Captures data at approximately 1Hz
- ✅ **30-second duration** - Limits parsing to 30 seconds of data
- ✅ **Modular architecture** - Separate components for parsing, filtering, and writing
- ✅ **Multiple message types** - Supports BESTXYZA, TIMEA, PSRDOPA, HWMONITORA, GPGSV, and RAW data

## Requirements

- Python 3.7 or higher
- No external dependencies (uses only standard library)

## Installation

### Option 1: Run from source

```bash
# No installation needed - all dependencies are in Python standard library
cd "OEM719 Log Parser Python/src"
python main.py
```

### Option 2: Create standalone executable (for deployment)

```bash
# Install PyInstaller (only needed once)
pip install pyinstaller

# Create executable
cd "OEM719 Log Parser Python/src"
pyinstaller --onefile --name OEM719_Parser main.py

# Executable will be in: dist/OEM719_Parser.exe
```

## Usage

### Running the parser

```bash
cd src
python main.py
```

The parser will:
1. Read the OEM719 Simulated Log.txt file (from the parent directory)
2. Start parsing from 1MB offset or when GPS lock is detected
3. Generate CSV files in the `src/test_data/` directory
4. Stop after 30 seconds of data or end of file

### Output Files

The following CSV files are generated in `src/test_data/`:

- `BESTXYZ.csv` - Position and velocity solutions
- `GPS TIME.csv` - Time messages
- `GPS PSRDOP.csv` - Position dilution of precision
- `GPS HWMONITOR.csv` - Hardware monitoring data
- `GPS GPGSV.csv` - GPS satellites in view
- `GPS RAW DATA.csv` - All raw messages

## Project Structure

```
OEM719 Log Parser Python/
├── src/
│   ├── main.py                          # Entry point
│   ├── test_data/                       # Output directory for CSV files
│   └── parsers/
│       ├── __init__.py
│       ├── oem719_parser.py             # Main parser orchestrator
│       ├── message_parsers.py           # Individual message parsers
│       ├── csv_headers.py               # CSV header definitions
│       ├── csv_writer.py                # CSV file management
│       ├── log_reader.py                # Log file reading with offset
│       ├── timestamp_extractor.py       # GPS time conversion
│       ├── frequency_filter.py          # 1Hz sampling filter
│       └── duration_limiter.py          # 30-second duration control
├── requirements.txt                      # Python dependencies
└── README.md                            # This file
```

## Module Architecture

### Core Modules

1. **`message_parsers.py`** - Parser classes for each message type
   - `BestXYZParser` - BESTXYZA messages
   - `TimeAParser` - TIMEA messages
   - `PSRDOPAParser` - PSRDOPA messages
   - `HWMonitorAParser` - HWMONITORA messages
   - `GPGSVParser` - GPGSV messages (multi-line)

2. **`log_reader.py`** - File reading with context management
   - Handles 1MB offset seeking
   - GPS lock detection (FINESTEERING)
   - Line-by-line reading with generator

3. **`csv_writer.py`** - CSV output management
   - Creates all CSV files with headers
   - Manages file references
   - Tracks message counts

4. **`frequency_filter.py`** - Sampling rate control
   - Implements 1Hz filtering
   - Per-message-type tracking

5. **`duration_limiter.py`** - Time-based limiting
   - 30-second duration tracking
   - Start/elapsed/remaining time methods

6. **`timestamp_extractor.py`** - GPS time handling
   - Extracts GPS week and seconds
   - Converts to readable format

## Configuration

You can modify the parser behavior by editing `main.py`:

```python
parser = OEM719Parser(
    input_file,
    output_dir,
    offset_bytes=1000000,        # 1MB offset (default)
    max_duration_seconds=30,     # 30 seconds (default)
    frequency_hz=1.0             # 1Hz sampling (default)
)
```

## Deployment

### For distribution to another PC:

#### Option A: Source Code Distribution

1. Copy the entire `OEM719 Log Parser Python` folder
2. Ensure Python 3.7+ is installed on target PC
3. Run with: `python src/main.py`

#### Option B: Standalone Executable (Recommended)

1. Install PyInstaller: `pip install pyinstaller`
2. Build executable:
   ```bash
   cd src
   pyinstaller --onefile --name OEM719_Parser main.py
   ```
3. Distribute files:
   - `dist/OEM719_Parser.exe` (executable)
   - Input log file: `OEM719 Simulated Log.txt`
4. On target PC, place exe and log file in same directory structure

#### Option C: Packaged Distribution

Create a distribution package with:
```
OEM719_Parser_Package/
├── OEM719_Parser.exe (or main.py)
├── parsers/ (if using source)
├── OEM719 Simulated Log.txt (input file)
├── test_data/ (empty output directory)
└── README.txt (instructions)
```

## Testing

The parser has been tested with:
- OEM719 Simulated Log.txt (1.4 MB log file)
- Expected output: ~420 messages per type (except GPGSV: ~950, RAW: all)
- Validated against reference CSV outputs

## Troubleshooting

**Problem:** "Input file not found"
- **Solution:** Ensure the log file path in `main.py` is correct

**Problem:** No messages written
- **Solution:** Check that GPS lock (FINESTEERING) is detected in the log

**Problem:** Wrong number of messages
- **Solution:** Verify 1Hz filtering and 30-second duration settings

## License

Internal use only - Terran Orbital Assessment

## Author

Generated for Terran Orbital OEM719 Log Parser Assessment
