import os
import time
from pathlib import Path
from config import MEDIA_DIR, RETENTION_HOURS

def purge_old_media(retention_hours=RETENTION_HOURS):
    """
    Scans the generated_media directory and deletes any file
    older than retention_hours (default: 48 hours / 2 days).
    Keeps laptop storage clean with zero bloat.
    """
    cutoff_time = time.time() - (retention_hours * 3600)
    deleted_count = 0
    reclaimed_bytes = 0

    if not MEDIA_DIR.exists():
        return 0, 0

    for item in MEDIA_DIR.glob("**/*"):
        if item.is_file():
            try:
                mtime = item.stat().st_mtime
                if mtime < cutoff_time:
                    size = item.stat().st_size
                    item.unlink()
                    deleted_count += 1
                    reclaimed_bytes += size
            except Exception as e:
                print(f"[Cleaner Warning] Could not remove {item.name}: {e}")

    # Remove empty subdirectories if any
    for subdir in sorted(MEDIA_DIR.glob("**/*"), reverse=True):
        if subdir.is_dir() and not any(subdir.iterdir()):
            try:
                subdir.rmdir()
            except Exception:
                pass

    mb_reclaimed = reclaimed_bytes / (1024 * 1024)
    if deleted_count > 0:
        print(f"[Cleaner] Purged {deleted_count} files older than {retention_hours}h. Reclaimed {mb_reclaimed:.2f} MB.")
    else:
        print(f"[Cleaner] Storage check complete. All files within the {retention_hours}h retention window.")

    return deleted_count, mb_reclaimed

if __name__ == "__main__":
    purge_old_media()
