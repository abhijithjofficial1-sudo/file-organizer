# File Organizer CLI

A powerful command-line tool to organize messy folders automatically with undo support.

## Features

✅ Organizes files by type (Images, Documents, Videos, etc.)  
✅ Recursive mode (organize subdirectories)  
✅ Undo functionality (reverse any organization)  
✅ Custom categories (define your own file groups)  
✅ Ignore patterns (skip certain files)  
✅ Dry run mode (preview before organizing)  
✅ No external dependencies

## Quick Start
```bash
# Preview what would happen
python organizer.py ~/Downloads --dry-run

# Actually organize files
python organizer.py ~/Downloads

# Organize including subfolders
python organizer.py ~/Downloads --recursive

# Undo last organization
python organizer.py ~/Downloads --undo
```

## Installation
```bash
# Clone or download this project
git clone <your-repo-url>
cd file-organizer

# No dependencies to install!
```

## Usage

### Basic Commands
```bash
# Organize a folder
python organizer.py <directory>

# Preview without moving files
python organizer.py <directory> --dry-run

# Organize subdirectories too
python organizer.py <directory> --recursive

# Undo the last organization
python organizer.py <directory> --undo
```

### Custom Categories
```bash
# Create sample config
python organizer.py --create-config

# Edit config.json with your categories
# Then use it:
python organizer.py ~/Downloads --config config.json
```

### Ignore Files
```bash
# Create sample ignore file
python organizer.py --create-ignore

# Edit .organizerignore to skip certain files
# Place it in the directory you want to organize
```

## How It Works

1. Scans directory for files
2. Groups files by extension
3. Creates category folders
4. Moves files into appropriate folders
5. Handles duplicate names automatically
6. Saves operation log for undo

## Examples
```bash
# Organize Downloads folder
python organizer.py ~/Downloads

# Organize Desktop with custom categories
python organizer.py ~/Desktop --config my_categories.json

# Organize project folder recursively (preview)
python organizer.py ./project --recursive --dry-run

# Made a mistake? Undo it
python organizer.py ~/Downloads --undo
```

## Requirements

- Python 3.6 or higher
- No external libraries needed

## Safety Features

- Dry run mode to preview changes
- Undo functionality with detailed logs
- Never overwrites files (adds numbers for duplicates)
- Ignore patterns to protect important files

## License

MIT
```

---

## 📄 **File 5: requirements.txt**
```
# No external dependencies required
# Python 3.6+ standard library only"# file-organizer" 
