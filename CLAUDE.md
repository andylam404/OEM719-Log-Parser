# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains solutions for parsing OEM719 GPS receiver log files. The project includes two parallel implementations:
- **LabVIEW Implementation**: `OEM719 Log Parser LabVIEW/`
- **Python Implementation**: `OEM719 Log Parser Python/`

Both parsers process the same input format (OEM719 Simulated Log.txt) and extract different GPS message types into separate CSV files.

## Input/Output Structure

**Input**: Raw OEM719 GPS log files containing mixed message types:
- Messages prefixed with `#` (e.g., `#BESTXYZA`, `#TIMEA`, `#PSRDOPA`, `#HWMONITORA`)
- Messages prefixed with `$` (e.g., `$GPGSV`)
- Raw data entries

**Expected Output**: Separate CSV files for each message type:
- `BESTXYZ.csv` - Position and velocity solutions
- `GPS TIME.csv` - Time messages
- `GPS PSRDOP.csv` - Position dilution of precision
- `GPS HWMONITOR.csv` - Hardware monitoring data
- `GPS GPGSV.csv` - GPS satellites in view
- `GPS RAW DATA.csv` - Raw measurement data

Reference solutions are in `LabVIEW_Python_Interview_Prompt_1/LabVIEW Python Interview Prompt/GPS Logs Solution/`

## Python Implementation

### Architecture
- Entry point: `OEM719 Log Parser Python/src/main.py`
- Imports parser module from `parsers.oem719_parser` (not yet implemented)
- Output directory: `output/` (auto-created if missing)

### Running the Python Parser
```bash
cd "OEM719 Log Parser Python/src"
python main.py
```

Note: The Python implementation references `parsers/oem719_parser.py` which needs to be created. The structure expects:
```python
def parse_oem719_log(input_file: str, output_dir: str):
    # Parse log and generate CSV files
    pass
```

## LabVIEW Implementation

### Architecture
The LabVIEW implementation uses the Queued Message Handler (QMH) design pattern:
- **Main VI**: `OEM719 Log Parser LabVIEW/src/Main.vi`
- **Project File**: `OEM719 Log Parser LabVIEW/src/OEM719 Log Parser.lvproj`

#### Key Components:
1. **Message Queue System** (`src/support/Message Queue/`)
   - `Message Queue.lvlib` - Message queue library
   - `Message Cluster.ctl` - Defines message structure
   - `Create All Message Queues.vi` - Initialize message queues
   - `Enqueue Message.vi` / `Dequeue Message.vi` - Queue operations

2. **User Events** (`src/support/User Event - Stop/`)
   - Stop event handling for clean shutdown

3. **Error Handlers** (`src/support/`)
   - `Error Handler - Event Handling Loop.vi`
   - `Error Handler - Message Handling Loop.vi`
   - `Check Loop Error.vi`

4. **Controls** (`src/controls/`)
   - `UI Data.ctl` - UI state data cluster

### Opening the LabVIEW Project
Open `OEM719 Log Parser LabVIEW/src/OEM719 Log Parser.lvproj` in LabVIEW, then run `Main.vi`.

## Message Format Details

The parser must handle multiple message formats with different field structures:

**BESTXYZA Format** (Position/Velocity):
- Header: Message name, port, sequence, idle time, time status, week, seconds
- Position: X, Y, Z coordinates with standard deviations
- Velocity: X, Y, Z velocity with standard deviations
- Additional: Station ID, latency, satellite counts

**TIMEA Format** (Time):
- Time status, clock offset, offset standard deviation

**HWMONITORA Format** (Hardware):
- Temperature and voltage readings for multiple components
- Format: count followed by value/identifier pairs

## Development Notes

- Input file path is currently hardcoded as `"OEM719 Simulated Log.txt"` in the Python implementation
- The LabVIEW implementation follows National Instruments QMH template pattern
- Both implementations should produce identical output when given the same input
- CSV output should include proper headers matching the reference solution format
