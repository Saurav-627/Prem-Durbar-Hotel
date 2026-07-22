import os
import shutil
import glob
import subprocess
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = "Creates a backup of the configured database (SQLite or PostgreSQL) and cleans up old backups."

    def add_arguments(self, parser):
        parser.add_argument(
            "--keep",
            type=int,
            default=10,
            help="Number of recent backups to keep (default: 10). Older backups will be deleted.",
        )
        parser.add_argument(
            "--backup-dir",
            type=str,
            default="backups",
            help="Directory to save the database backup files (default: 'backups' in project root)",
        )

    def handle(self, *args, **options):
        keep_count = options["keep"]
        backup_dir = os.path.join(settings.BASE_DIR, options["backup_dir"])
        
        # Ensure backup directory exists
        os.makedirs(backup_dir, exist_ok=True)
        
        db_config = settings.DATABASES.get("default", {})
        db_engine = db_config.get("ENGINE", "")
        db_name = db_config.get("NAME", "")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.stdout.write(self.style.NOTICE(f"Starting backup at {timestamp}..."))

        if "sqlite3" in db_engine:
            # SQLite Backup
            if not os.path.exists(db_name):
                self.stderr.write(self.style.ERROR(f"SQLite database file not found: {db_name}"))
                return
            
            backup_filename = f"db_backup_{timestamp}.sqlite3"
            backup_path = os.path.join(backup_dir, backup_filename)
            try:
                shutil.copy2(db_name, backup_path)
                self.stdout.write(self.style.SUCCESS(f"Successfully backed up SQLite database to: {backup_path}"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Failed to copy SQLite database: {e}"))
                return

        elif "postgresql" in db_engine:
            # PostgreSQL Backup using pg_dump
            db_user = db_config.get("USER", "")
            db_password = db_config.get("PASSWORD", "")
            db_host = db_config.get("HOST", "localhost")
            db_port = db_config.get("PORT", "5432")
            
            backup_filename = f"db_backup_{timestamp}.sql"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            env = os.environ.copy()
            if db_password:
                env["PGPASSWORD"] = db_password
                
            cmd = [
                "pg_dump",
                "-h", db_host,
                "-p", str(db_port),
                "-U", db_user,
                "-F", "c",  # Custom format (compressed)
                "-b",       # Include large objects
                "-v",       # Verbose
                "-f", backup_path,
                db_name
            ]
            
            try:
                subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
                self.stdout.write(self.style.SUCCESS(f"Successfully backed up PostgreSQL database to: {backup_path}"))
            except subprocess.CalledProcessError as e:
                self.stderr.write(self.style.ERROR(f"pg_dump failed: {e.stderr}"))
                return
            except FileNotFoundError:
                self.stderr.write(self.style.ERROR("pg_dump utility not found. Please ensure PostgreSQL client tools are installed."))
                return

        else:
            self.stderr.write(self.style.ERROR(f"Unsupported database engine: {db_engine}"))
            return

        # Cleanup older backups
        self.stdout.write(self.style.NOTICE("Checking for old backups to clean up..."))
        
        # Get all backup files (sqlite3 or sql) in the directory
        wildcard = os.path.join(backup_dir, "db_backup_*")
        backup_files = glob.glob(wildcard)
        
        # Sort files by modification time (oldest first)
        backup_files.sort(key=os.path.getmtime)
        
        if len(backup_files) > keep_count:
            files_to_delete = backup_files[:-keep_count]
            for file_path in files_to_delete:
                try:
                    os.remove(file_path)
                    self.stdout.write(self.style.NOTICE(f"Deleted old backup: {os.path.basename(file_path)}"))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Failed to delete {file_path}: {e}"))
        else:
            self.stdout.write(self.style.SUCCESS("No old backups needed to be deleted."))
