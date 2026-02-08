import os
import shutil
import json
import argparse
from pathlib import Path
from datetime import datetime


# Default file categories
DEFAULT_CATEGORIES = {
    'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'],
    'Documents': ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls', '.pptx', '.ppt', '.odt', '.rtf'],
    'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.webm', '.m4v'],
    'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
    'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'],
    'Code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.json', '.xml', '.yaml', '.yml'],
    'Executables': ['.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm', '.app'],
    'Books': ['.epub', '.mobi', '.azw', '.azw3'],
}


class FileOrganizer:
    def __init__(self, directory, recursive=False, dry_run=False, config_path=None):
        self.directory = Path(directory).resolve()
        self.recursive = recursive
        self.dry_run = dry_run
        self.log_file = self.directory / '.organizer_log.json'
        self.ignore_file = self.directory / '.organizerignore'
        
        # Load categories (custom or default)
        self.categories = self.load_categories(config_path)
        
        # Load ignore patterns
        self.ignore_patterns = self.load_ignore_patterns()
        
        # Track operations for undo
        self.operations = []
    
    def load_categories(self, config_path):
        """Load custom categories from config file or use defaults"""
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    custom_categories = json.load(f)
                print(f"✓ Loaded custom categories from {config_path}")
                return custom_categories
            except Exception as e:
                print(f"⚠️  Warning: Could not load config file: {e}")
                print("   Using default categories")
        
        return DEFAULT_CATEGORIES
    
    def load_ignore_patterns(self):
        """Load patterns from .organizerignore file"""
        patterns = ['.organizer_log.json', '.organizerignore']  # Always ignore these
        
        if self.ignore_file.exists():
            try:
                with open(self.ignore_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        # Skip empty lines and comments
                        if line and not line.startswith('#'):
                            patterns.append(line)
                print(f"✓ Loaded {len(patterns) - 2} ignore pattern(s)")
            except Exception as e:
                print(f"⚠️  Warning: Could not load .organizerignore: {e}")
        
        return patterns
    
    def should_ignore(self, file_path):
        """Check if file should be ignored based on patterns"""
        file_name = file_path.name
        
        for pattern in self.ignore_patterns:
            # Simple wildcard matching
            if pattern.startswith('*'):
                if file_name.endswith(pattern[1:]):
                    return True
            elif pattern.endswith('*'):
                if file_name.startswith(pattern[:-1]):
                    return True
            elif pattern in file_name:
                return True
        
        return False
    
    def get_category(self, file_extension):
        """Determine category based on file extension"""
        for category, extensions in self.categories.items():
            if file_extension.lower() in extensions:
                return category
        return 'Others'
    
    def organize_directory(self, current_dir=None):
        """Organize files in directory (and subdirectories if recursive)"""
        if current_dir is None:
            current_dir = self.directory
        
        files_processed = 0
        
        # Get all items in current directory
        try:
            items = list(current_dir.iterdir())
        except PermissionError:
            print(f"❌ Permission denied: {current_dir}")
            return files_processed
        
        for item in items:
            # Handle directories
            if item.is_dir():
                # Skip category folders we created
                if item.parent == self.directory and item.name in self.categories.keys():
                    continue
                
                # Recurse into subdirectories if enabled
                if self.recursive and item.parent == self.directory:
                    print(f"\n📁 Entering subdirectory: {item.name}")
                    files_processed += self.organize_directory(item)
                continue
            
            # Skip ignored files
            if self.should_ignore(item):
                continue
            
            # Process file
            if self.organize_file(item):
                files_processed += 1
        
        return files_processed
    
    def organize_file(self, file_path):
        """Organize a single file"""
        file_extension = file_path.suffix
        category = self.get_category(file_extension)
        
        # Create category folder
        category_path = self.directory / category
        
        if not self.dry_run:
            category_path.mkdir(exist_ok=True)
        
        # Build new file path
        new_file_path = category_path / file_path.name
        
        # Handle duplicate filenames
        counter = 1
        original_stem = file_path.stem
        while new_file_path.exists():
            new_filename = f"{original_stem}_{counter}{file_extension}"
            new_file_path = category_path / new_filename
            counter += 1
        
        # Get relative paths for cleaner output
        try:
            old_rel = file_path.relative_to(self.directory)
            new_rel = new_file_path.relative_to(self.directory)
        except ValueError:
            old_rel = file_path
            new_rel = new_file_path
        
        # Move file or show dry run
        if self.dry_run:
            print(f"[DRY RUN] {old_rel} → {new_rel}")
        else:
            try:
                shutil.move(str(file_path), str(new_file_path))
                print(f"✓ {old_rel} → {new_rel}")
                
                # Record operation for undo
                self.operations.append({
                    'old_path': str(file_path),
                    'new_path': str(new_file_path),
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                print(f"❌ Error moving {file_path.name}: {e}")
                return False
        
        return True
    
    def save_log(self):
        """Save operations log for undo functionality"""
        if self.dry_run or not self.operations:
            return
        
        try:
            with open(self.log_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'operations': self.operations
                }, f, indent=2)
            print(f"\n💾 Log saved to {self.log_file.name} ({len(self.operations)} operations)")
        except Exception as e:
            print(f"⚠️  Warning: Could not save log: {e}")
    
    def run(self):
        """Main execution"""
        # Validate directory
        if not self.directory.exists():
            print(f"❌ Error: Directory '{self.directory}' does not exist")
            return
        
        if not self.directory.is_dir():
            print(f"❌ Error: '{self.directory}' is not a directory")
            return
        
        print(f"📂 Organizing: {self.directory}")
        print(f"   Recursive: {'Yes' if self.recursive else 'No'}")
        print(f"   Dry Run: {'Yes' if self.dry_run else 'No'}")
        print(f"   Categories: {len(self.categories)}")
        print()
        
        # Organize files
        files_processed = self.organize_directory()
        
        # Save log
        if not self.dry_run:
            self.save_log()
        
        # Summary
        if files_processed == 0:
            print("\nℹ️  No files to organize")
        else:
            action = "Would organize" if self.dry_run else "Organized"
            print(f"\n✅ {action} {files_processed} file(s)")


def undo_organization(directory):
    """Undo the last organization by reading the log file"""
    directory = Path(directory).resolve()
    log_file = directory / '.organizer_log.json'
    
    if not log_file.exists():
        print("❌ No log file found. Nothing to undo.")
        return
    
    try:
        with open(log_file, 'r') as f:
            log_data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading log file: {e}")
        return
    
    operations = log_data.get('operations', [])
    if not operations:
        print("ℹ️  Log file is empty. Nothing to undo.")
        return
    
    print(f"🔄 Undoing {len(operations)} operation(s)...")
    print(f"   From: {log_data.get('timestamp', 'unknown time')}\n")
    
    success_count = 0
    
    # Reverse the operations
    for op in reversed(operations):
        old_path = Path(op['old_path'])
        new_path = Path(op['new_path'])
        
        if not new_path.exists():
            print(f"⚠️  Skipped: {new_path.name} (file not found)")
            continue
        
        try:
            # Recreate original directory structure if needed
            old_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move file back
            shutil.move(str(new_path), str(old_path))
            print(f"✓ Restored: {new_path.name} → {old_path}")
            success_count += 1
        except Exception as e:
            print(f"❌ Error restoring {new_path.name}: {e}")
    
    # Delete empty category folders
    for item in directory.iterdir():
        if item.is_dir() and not any(item.iterdir()):
            try:
                item.rmdir()
                print(f"🗑️  Removed empty folder: {item.name}")
            except:
                pass
    
    # Remove log file
    try:
        log_file.unlink()
        print(f"\n✅ Undo complete! Restored {success_count} file(s)")
    except Exception as e:
        print(f"⚠️  Warning: Could not delete log file: {e}")


def create_sample_config(output_path='config.json'):
    """Create a sample config file"""
    sample_config = {
        "Images": [".jpg", ".png", ".gif"],
        "Documents": [".pdf", ".docx", ".txt"],
        "Videos": [".mp4", ".mkv"],
        "MyCustomCategory": [".custom", ".special"]
    }
    
    try:
        with open(output_path, 'w') as f:
            json.dump(sample_config, f, indent=2)
        print(f"✅ Created sample config: {output_path}")
        print("   Edit this file to customize your categories")
    except Exception as e:
        print(f"❌ Error creating config: {e}")


def create_sample_ignore(output_path='.organizerignore'):
    """Create a sample ignore file"""
    sample_ignore = """# File Organizer Ignore Patterns
# Lines starting with # are comments

# Ignore specific files
important_file.txt
*.tmp

# Ignore files starting with certain text
draft_*

# Ignore files containing certain text
*backup*

# Ignore all files with certain extensions
*.log
*.cache
"""
    
    try:
        with open(output_path, 'w') as f:
            f.write(sample_ignore)
        print(f"✅ Created sample ignore file: {output_path}")
        print("   Edit this file to customize what files to skip")
    except Exception as e:
        print(f"❌ Error creating ignore file: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Organize files in a directory by type with undo support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python organizer.py ~/Downloads
  
  # Preview what would happen (dry run)
  python organizer.py ~/Downloads --dry-run
  
  # Organize including subdirectories
  python organizer.py ~/Downloads --recursive
  
  # Use custom categories
  python organizer.py ~/Downloads --config my_categories.json
  
  # Undo last organization
  python organizer.py ~/Downloads --undo
  
  # Create sample config files
  python organizer.py --create-config
  python organizer.py --create-ignore
        """
    )
    
    parser.add_argument(
        'directory',
        nargs='?',
        help='Path to the directory to organize'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would happen without actually moving files'
    )
    
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='Organize files in subdirectories too'
    )
    
    parser.add_argument(
        '--config', '-c',
        help='Path to custom categories config file (JSON)'
    )
    
    parser.add_argument(
        '--undo',
        action='store_true',
        help='Undo the last organization'
    )
    
    parser.add_argument(
        '--create-config',
        action='store_true',
        help='Create a sample config.json file'
    )
    
    parser.add_argument(
        '--create-ignore',
        action='store_true',
        help='Create a sample .organizerignore file'
    )
    
    args = parser.parse_args()
    
    # Handle helper commands
    if args.create_config:
        create_sample_config()
        return
    
    if args.create_ignore:
        create_sample_ignore()
        return
    
    # Require directory for main operations
    if not args.directory:
        parser.print_help()
        return
    
    # Handle undo
    if args.undo:
        undo_organization(args.directory)
        return
    
    # Run organizer
    organizer = FileOrganizer(
        directory=args.directory,
        recursive=args.recursive,
        dry_run=args.dry_run,
        config_path=args.config
    )
    
    organizer.run()


if __name__ == '__main__':
    main()