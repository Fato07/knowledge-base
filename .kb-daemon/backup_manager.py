#!/usr/bin/env python3
"""
KB Backup Manager - Intelligent backup rotation
"""

import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import json

class BackupManager:
    """Manages backups with rotation policy"""
    
    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path.home() / "DEV" / "knowledge-base" / ".kb-daemon"
        self.backup_dir = self.base_path / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Backup retention policy
        self.policy = {
            'daily_keep': 7,      # Keep daily backups for 7 days
            'weekly_keep': 4,     # Keep weekly backups for 4 weeks
            'monthly_keep': 3,    # Keep monthly backups for 3 months
            'max_size_mb': 100,   # Max total backup size in MB
        }
        
    def create_backup(self, files_to_backup: list, reason: str = "manual") -> Path:
        """Create a new backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{reason}_{timestamp}"
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Copy files
        backed_up = []
        for file in files_to_backup:
            if Path(file).exists():
                try:
                    if Path(file).is_file():
                        shutil.copy2(file, backup_path)
                    else:
                        shutil.copytree(file, backup_path / Path(file).name)
                    backed_up.append(file)
                except Exception as e:
                    print(f"  ⚠️  Could not backup {file}: {e}")
        
        # Create backup metadata
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'reason': reason,
            'files_count': len(backed_up),
            'files': backed_up,
            'size_bytes': sum(f.stat().st_size for f in backup_path.rglob('*') if f.is_file())
        }
        
        with open(backup_path / 'backup_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Backup created: {backup_path}")
        print(f"   Files backed up: {len(backed_up)}")
        
        return backup_path
    
    def rotate_backups(self):
        """Rotate backups according to retention policy"""
        now = datetime.now()
        all_backups = sorted([d for d in self.backup_dir.iterdir() if d.is_dir()])
        
        if not all_backups:
            print("No backups to rotate")
            return
        
        keep_backups = set()
        
        # Keep daily backups for last N days
        for days_ago in range(self.policy['daily_keep']):
            date = now - timedelta(days=days_ago)
            daily = self._find_backup_for_date(all_backups, date)
            if daily:
                keep_backups.add(daily)
        
        # Keep weekly backups for last N weeks
        for weeks_ago in range(self.policy['weekly_keep']):
            date = now - timedelta(weeks=weeks_ago)
            # Get the Monday of that week
            monday = date - timedelta(days=date.weekday())
            weekly = self._find_backup_for_date(all_backups, monday)
            if weekly:
                keep_backups.add(weekly)
        
        # Keep monthly backups for last N months
        for months_ago in range(self.policy['monthly_keep']):
            # Approximate month calculation
            date = now - timedelta(days=30 * months_ago)
            monthly = self._find_backup_for_date(all_backups, date, prefer_first=True)
            if monthly:
                keep_backups.add(monthly)
        
        # Delete old backups
        deleted_count = 0
        freed_space = 0
        
        for backup in all_backups:
            if backup not in keep_backups:
                # Calculate size before deletion
                size = sum(f.stat().st_size for f in backup.rglob('*') if f.is_file())
                freed_space += size
                
                # Delete
                shutil.rmtree(backup)
                deleted_count += 1
                print(f"  🗑️  Deleted old backup: {backup.name}")
        
        if deleted_count > 0:
            print(f"\n📊 Backup Rotation Summary:")
            print(f"  Deleted: {deleted_count} old backups")
            print(f"  Freed: {freed_space / 1024 / 1024:.1f} MB")
            print(f"  Kept: {len(keep_backups)} backups")
        else:
            print("✅ All backups within retention policy")
        
        # Check total size
        self._check_size_limit()
    
    def _find_backup_for_date(self, backups: list, target_date: datetime, prefer_first: bool = False) -> Path:
        """Find a backup closest to target date"""
        target_str = target_date.strftime("%Y%m%d")
        
        candidates = []
        for backup in backups:
            # Extract date from backup name (format: backup_reason_YYYYMMDD_HHMMSS)
            parts = backup.name.split('_')
            if len(parts) >= 3:
                backup_date = parts[2]  # YYYYMMDD part
                if backup_date == target_str:
                    candidates.append(backup)
                elif backup_date[:6] == target_str[:6] and prefer_first:  # Same month
                    candidates.append(backup)
        
        if candidates:
            return candidates[0] if prefer_first else candidates[-1]
        return None
    
    def _check_size_limit(self):
        """Check if backups exceed size limit"""
        total_size = 0
        all_backups = sorted([d for d in self.backup_dir.iterdir() if d.is_dir()])
        
        for backup in all_backups:
            size = sum(f.stat().st_size for f in backup.rglob('*') if f.is_file())
            total_size += size
        
        total_mb = total_size / 1024 / 1024
        
        if total_mb > self.policy['max_size_mb']:
            print(f"\n⚠️  Warning: Backups using {total_mb:.1f} MB (limit: {self.policy['max_size_mb']} MB)")
            print("   Consider adjusting retention policy or cleaning old backups")
        else:
            print(f"\n💾 Backup storage: {total_mb:.1f} MB / {self.policy['max_size_mb']} MB")
    
    def list_backups(self):
        """List all backups with details"""
        all_backups = sorted([d for d in self.backup_dir.iterdir() if d.is_dir()])
        
        if not all_backups:
            print("No backups found")
            return
        
        print("\n📦 Current Backups:")
        print("-" * 60)
        
        total_size = 0
        for backup in all_backups:
            # Read metadata if exists
            metadata_file = backup / 'backup_metadata.json'
            if metadata_file.exists():
                with open(metadata_file) as f:
                    metadata = json.load(f)
                size = metadata.get('size_bytes', 0)
                reason = metadata.get('reason', 'unknown')
                files = metadata.get('files_count', 0)
            else:
                # Calculate size manually
                size = sum(f.stat().st_size for f in backup.rglob('*') if f.is_file())
                reason = 'unknown'
                files = len(list(backup.rglob('*')))
            
            total_size += size
            
            # Parse date from name
            parts = backup.name.split('_')
            if len(parts) >= 3:
                date_str = f"{parts[2][:4]}-{parts[2][4:6]}-{parts[2][6:8]}"
                time_str = f"{parts[3][:2]}:{parts[3][2:4]}" if len(parts) > 3 else ""
            else:
                date_str = "unknown"
                time_str = ""
            
            print(f"📁 {backup.name}")
            print(f"   Date: {date_str} {time_str}")
            print(f"   Reason: {reason}")
            print(f"   Files: {files}")
            print(f"   Size: {size / 1024:.1f} KB")
            print()
        
        print("-" * 60)
        print(f"Total: {len(all_backups)} backups, {total_size / 1024 / 1024:.1f} MB")
    
    def restore_backup(self, backup_name: str, target_dir: Path = None):
        """Restore a specific backup"""
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            print(f"❌ Backup not found: {backup_name}")
            return False
        
        target = target_dir or Path.cwd()
        
        print(f"🔄 Restoring backup: {backup_name}")
        print(f"   To: {target}")
        
        # Copy files back
        for item in backup_path.iterdir():
            if item.name != 'backup_metadata.json':
                if item.is_file():
                    shutil.copy2(item, target / item.name)
                else:
                    shutil.copytree(item, target / item.name, dirs_exist_ok=True)
                print(f"   ✓ Restored: {item.name}")
        
        print("✅ Backup restored successfully")
        return True


def main():
    """Main CLI for backup management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="KB Backup Manager")
    parser.add_argument('command', choices=['list', 'rotate', 'clean', 'restore'],
                       help='Command to execute')
    parser.add_argument('--backup', help='Backup name for restore')
    
    args = parser.parse_args()
    
    manager = BackupManager()
    
    if args.command == 'list':
        manager.list_backups()
    elif args.command == 'rotate':
        print("🔄 Rotating backups...")
        manager.rotate_backups()
    elif args.command == 'clean':
        print("🧹 Cleaning old backups...")
        manager.rotate_backups()
    elif args.command == 'restore':
        if args.backup:
            manager.restore_backup(args.backup)
        else:
            print("❌ Please specify backup name with --backup")
    

if __name__ == "__main__":
    main()
