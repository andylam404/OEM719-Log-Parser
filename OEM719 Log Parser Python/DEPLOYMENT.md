# Deployment Guide - OEM719 Log Parser

This guide covers how to package and deploy the OEM719 Log Parser to another PC.

## Prerequisites

### Source PC (Development Machine)
- Python 3.7 or higher
- PyInstaller (for creating executable): `pip install pyinstaller`

### Target PC (Deployment Machine)
- **Option A (Executable):** No requirements - runs standalone
- **Option B (Source):** Python 3.7 or higher

---

## Deployment Option 1: Standalone Executable (Recommended)

This creates a single executable that can run on any Windows PC without Python installed.

### Step 1: Install PyInstaller

```bash
pip install pyinstaller
```

### Step 2: Build the Executable

```bash
cd "C:\Users\andyl\Terran_Orbital_Assessment\OEM719 Log Parser Python\src"

# Basic build (single executable)
pyinstaller --onefile --name OEM719_Parser main.py

# OR with custom options
pyinstaller --onefile ^
    --name OEM719_Parser ^
    --add-data "parsers;parsers" ^
    --console ^
    --clean ^
    main.py
```

This creates:
- `dist/OEM719_Parser.exe` - Standalone executable
- `build/` - Temporary build files (can be deleted)
- `OEM719_Parser.spec` - Build specification

### Step 3: Create Deployment Package

Create a folder with:

```
OEM719_Parser_v1.0/
├── OEM719_Parser.exe
├── README.txt
└── test_data/ (empty folder for output)
```

### Step 4: Deploy to Target PC

1. Copy the `OEM719_Parser_v1.0` folder to target PC
2. Place `OEM719 Simulated Log.txt` in the appropriate location
3. Update the file path if needed (see Configuration section)
4. Double-click `OEM719_Parser.exe` or run from command line

---

## Deployment Option 2: Source Code Distribution

Deploy the Python source code directly.

### Step 1: Prepare Distribution Package

Create a clean copy:

```bash
# Copy the entire project folder
xcopy "C:\Users\andyl\Terran_Orbital_Assessment\OEM719 Log Parser Python" ^
      "C:\Deploy\OEM719_Parser" /E /I
```

### Step 2: Clean Unnecessary Files

Remove:
- `__pycache__/` directories
- `.pyc` files
- `test_data/*.csv` (keep the folder but remove old outputs)

### Step 3: Create requirements.txt (already done)

The `requirements.txt` file lists all dependencies (none in this case).

### Step 4: Deploy to Target PC

1. Copy the entire folder to target PC
2. Install Python 3.7+ if not present
3. Navigate to `src/` directory
4. Run: `python main.py`

---

## Deployment Option 3: Python Wheel Package

Create a distributable Python package.

### Step 1: Create Package Structure

```
OEM719_Parser/
├── setup.py
├── README.md
├── LICENSE
└── oem719_parser/
    ├── __init__.py
    ├── main.py
    └── parsers/
        └── (all parser modules)
```

### Step 2: Create setup.py

```python
from setuptools import setup, find_packages

setup(
    name="oem719-parser",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'oem719-parser=oem719_parser.main:main',
        ],
    },
    python_requires='>=3.7',
    author="Your Name",
    description="OEM719 GPS Log Parser",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
)
```

### Step 3: Build and Install

```bash
# Build wheel
python setup.py bdist_wheel

# Install on target PC
pip install dist/oem719_parser-1.0.0-py3-none-any.whl

# Run
oem719-parser
```

---

## Configuration for Deployment

### Updating File Paths

If the log file location differs on the target PC, update `main.py`:

**Current (relative path):**
```python
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
input_file = os.path.join(base_dir, "LabVIEW_Python_Interview_Prompt_1",
                          "LabVIEW Python Interview Prompt", "OEM719 Simulated Log.txt")
```

**For deployment (configurable path):**
```python
# Option 1: Use command-line argument
import sys
input_file = sys.argv[1] if len(sys.argv) > 1 else "OEM719 Simulated Log.txt"

# Option 2: Use environment variable
import os
input_file = os.getenv('OEM719_LOG_FILE', 'OEM719 Simulated Log.txt')

# Option 3: Use config file
import json
with open('config.json') as f:
    config = json.load(f)
input_file = config['input_file']
```

---

## Files to Include in Deployment

### Minimum Files (Executable):
- `OEM719_Parser.exe`
- `README.txt` (usage instructions)

### Minimum Files (Source):
- `src/main.py`
- `src/parsers/*.py` (all parser modules)
- `requirements.txt`
- `README.md`

### Optional Files:
- Sample log file (for testing)
- Reference CSV outputs (for validation)
- Configuration file
- License/documentation

---

## Deployment Checklist

### Pre-Deployment:
- [ ] Test executable/source on development machine
- [ ] Verify all CSV outputs are correct
- [ ] Remove sensitive data from log files
- [ ] Update file paths for target environment
- [ ] Create user documentation
- [ ] Test on clean PC (if possible)

### Packaging:
- [ ] Build executable (if using Option 1)
- [ ] Create deployment folder structure
- [ ] Include README/instructions
- [ ] Create empty output directories
- [ ] Compress package (ZIP)

### On Target PC:
- [ ] Extract package
- [ ] Place log file in correct location
- [ ] Run executable/script
- [ ] Verify output CSV files are generated
- [ ] Check message counts match expected values

---

## Troubleshooting Deployment Issues

### Issue: "Python not found" (Source deployment)
**Solution:** Install Python 3.7+ from python.org

### Issue: "Module not found" error
**Solution:** Ensure all `.py` files in `parsers/` folder are included

### Issue: Executable won't run
**Solution:**
- Check Windows Defender/antivirus
- Run as administrator
- Ensure Visual C++ Redistributable is installed

### Issue: Wrong file paths
**Solution:** Update paths in `main.py` or use command-line arguments

### Issue: No output files generated
**Solution:**
- Check write permissions in output directory
- Verify input log file exists and is readable
- Check for error messages in console

---

## Version Control (Optional)

If using Git for version control:

```bash
# .gitignore
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.dylib
*.dll
*.exe
build/
dist/
*.egg-info/
.pytest_cache/
.coverage
test_data/*.csv
```

---

## Performance Notes

- Executable size: ~5-10 MB (with PyInstaller)
- Memory usage: ~50-100 MB during parsing
- Parse time: ~0.5 seconds for 30 seconds of data
- Output size: ~2.5 MB total (all CSV files)

---

## Support and Maintenance

For updates or issues:
1. Modify source code
2. Test changes
3. Rebuild executable
4. Re-deploy to target PCs
5. Update version number
