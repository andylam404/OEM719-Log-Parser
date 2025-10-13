# LabVIEW OEM719 Log Parser - Implementation Guide

## Current Project Structure

This LabVIEW project uses the **Queued Message Handler (QMH)** design pattern with:
- Main.vi (shell - needs implementation)
- Message Queue infrastructure (complete)
- User Event - Stop handling (complete)
- Error handling VIs (complete)
- UI Data type definition (needs configuration)
- QMH documentation included

## What Needs to Be Implemented

### Step 1: Define Type Definitions

#### 1.1 Update `controls/UI Data.ctl`
Add controls for:
- Input File Path (String/Path control)
- Output Directory (String/Path control)
- Start Offset (Numeric - default 1000000 bytes)
- Duration Limit (Numeric - default 30 seconds)
- Status Indicator (String - shows current status)
- Messages Processed (Numeric array or cluster showing counts per type)
- Start/Stop Button (Boolean)

#### 1.2 Create New Type Definitions in controls/ folder

**GPS Message Type.ctl** - Enum with values:
- BESTXYZA
- TIMEA
- PSRDOPA
- HWMONITORA
- GPGSV
- RAW

**Parsed Message Data.ctl** - Cluster containing:
- Message Type (GPS Message Type enum)
- Timestamp (String)
- Raw Data (String)
- Parsed Fields (Array of Strings)

### Step 2: Create Parsing VIs (in src/parsers/ folder)

**Read Log File.vi**
- Inputs: File Path, Offset (bytes), GPS Lock Required (Boolean)
- Outputs: File Refnum, Start Position Found (Boolean), Error
- Function: Open file, seek to offset, scan for "FINESTEERING"

**Parse BESTXYZA.vi**
- Inputs: Raw Line (String), Timestamp (String)
- Outputs: Parsed Data Array (String Array), Success (Boolean)
- Function: Parse BESTXYZA message format using regex or string functions

**Parse TIMEA.vi**
- Similar to BESTXYZA but for TIME messages

**Parse PSRDOPA.vi**
- Parse PSRDOP messages

**Parse HWMONITORA.vi**
- Parse hardware monitor messages
- Extract key-value pairs from format: count, val1, id1, val2, id2...

**Parse GPGSV.vi**
- Handle multi-line GPGSV messages
- Special: May need to buffer multiple lines

**Extract Timestamp.vi**
- Inputs: Raw Line (String)
- Outputs: Timestamp (String), Week (I32), Seconds (DBL)
- Function: Extract GPS week and seconds, convert to readable format

### Step 3: Create CSV Writer VIs (in src/file_writers/ folder)

**Initialize CSV Files.vi**
- Inputs: Output Directory (Path)
- Outputs: File Reference Array, Error
- Function: Create/open 6 CSV files, write headers, return file references

**Write CSV Row.vi**
- Inputs: File Ref, Row Data (String Array)
- Outputs: Error
- Function: Write comma-separated values to file with newline

**Close CSV Files.vi**
- Inputs: File Reference Array
- Function: Close all file references

### Step 4: Modify Main.vi Message Handler

#### Add Messages to Message Queue (in Message Cluster.ctl):
1. "Start Parsing" - Begin parsing the log file
2. "Stop Parsing" - Stop parsing operation
3. "Process Next Line" - Process next line from log
4. "Write CSV" - Write data to CSV (with message type and data)
5. "Update Progress" - Update UI with progress
6. "Parse Complete" - Parsing finished

#### Message Handling Loop Cases:

**"Start Parsing" Case:**
1. Call Read Log File.vi with offset
2. Initialize CSV files
3. Create parsing state (refnum, counters, start time)
4. Enqueue "Process Next Line" message

**"Process Next Line" Case:**
1. Read line from file
2. Identify message type (#BESTXYZA, #TIMEA, $GPGSV, etc.)
3. Call appropriate Parse VI
4. If 1Hz filter passes: Enqueue "Write CSV" message
5. Check duration limit (30 seconds)
6. If not done: Enqueue "Process Next Line" again
7. If done: Enqueue "Parse Complete"

**"Write CSV" Case:**
1. Get message type and parsed data
2. Call Write CSV Row.vi with appropriate file ref
3. Increment message counter
4. Enqueue "Update Progress"

**"Parse Complete" Case:**
1. Close all CSV files
2. Close log file
3. Update UI with final statistics
4. Display completion message

### Step 5: Event Handling Loop

Add to Main.vi's Event Handling Loop:

**Start Button Value Change Event:**
- Enqueue "Start Parsing" message with UI data

**Stop Button Value Change Event:**
- Enqueue "Stop Parsing" message

## Implementation Order

### Phase 1: File I/O Foundation
1. Create Read Log File.vi
2. Create Initialize CSV Files.vi and Write CSV Row.vi
3. Test file reading and CSV writing independently

### Phase 2: Single Message Parser
1. Start with Parse BESTXYZA.vi (simplest format)
2. Create Extract Timestamp.vi
3. Test parsing a few BESTXYZA messages to CSV

### Phase 3: All Message Parsers
1. Implement remaining parser VIs
2. Test each message type independently

### Phase 4: Main Loop Integration
1. Add message cases to Main.vi
2. Implement frequency filtering logic (1Hz)
3. Implement duration limiting (30 seconds)

### Phase 5: Testing & Polish
1. Test with full log file
2. Compare output with Python implementation (in Python folder)
3. Add error handling
4. Add progress indicators

## Key LabVIEW Techniques Needed

1. String Functions: Search/Match Pattern, Scan From String, Format Into String
2. File I/O: Open/Read/Write File, Set File Position
3. Array Functions: Build Array, Index Array, Array Size
4. Timing: Get Date/Time In Seconds, Tick Count
5. Variant Attributes: For flexible message data passing

## Testing Strategy

1. Unit Test Each Parser VI:
   - Create test data with known message formats
   - Verify output matches expected values

2. Integration Test:
   - Run on small portion of log file first
   - Compare CSV outputs with Python implementation

3. Performance Test:
   - Ensure 30-second duration limit works
   - Verify 1Hz filtering is accurate

## Expected Output

The parser should generate these CSV files:
- BESTXYZ.csv (Position and velocity data)
- GPS TIME.csv (Time messages)
- GPS PSRDOP.csv (Dilution of precision)
- GPS HWMONITOR.csv (Hardware monitoring)
- GPS GPGSV.csv (Satellites in view)
- GPS RAW DATA.csv (All raw messages)

Reference outputs are in: LabVIEW_Python_Interview_Prompt_1/LabVIEW Python Interview Prompt/GPS Logs Solution/

## Requirements

- Parse from 1MB offset OR when GPS acquires lock (FINESTEERING status)
- Capture data at 1Hz frequency
- Duration: 30 seconds
- Input file: OEM719 Simulated Log.txt
- Do not modify the input log file