"""Tanári ellenőrzés: _megoldas fájlok ideiglenes másolása, pytest, visszaállítás."""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEGOLDAS = ROOT / "_megoldas"
BACKUP = ROOT / ".verify_backup"

COPY_MAP = [
    ("config/settings.py", "config/settings.py"),
    ("config/urls.py", "config/urls.py"),
    ("courses/models.py", "courses/models.py"),
    ("courses/admin.py", "courses/admin.py"),
    ("courses/permissions.py", "courses/permissions.py"),
    ("courses/api", "courses/api"),
    ("courses/management/commands/seed_courses.py", "courses/management/commands/seed_courses.py"),
    ("courses/tests/test_api.py", "courses/tests/test_api.py"),
    ("README.md", "README.md"),
    ("docs/er_diagram.md", "docs/er_diagram.md"),
    ("docs/api_tesztek.md", "docs/api_tesztek.md"),
]

BACKUP_RELS = [dst for _, dst in COPY_MAP]


def copy_tree(src: Path, dst: Path):
    if src.is_dir():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def main():
    if not MEGOLDAS.exists():
        print("_megoldas mappa nem található", file=sys.stderr)
        return 1

    if BACKUP.exists():
        shutil.rmtree(BACKUP)
    BACKUP.mkdir()

    for rel in BACKUP_RELS:
        src = ROOT / rel
        if src.exists():
            copy_tree(src, BACKUP / rel)

    try:
        for src_rel, dst_rel in COPY_MAP:
            src = MEGOLDAS / src_rel
            if not src.exists():
                print(f"Hiányzó megoldás fájl: {src}", file=sys.stderr)
                return 1
            copy_tree(src, ROOT / dst_rel)

        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            cwd=ROOT,
            check=True,
        )
        subprocess.run(
            [sys.executable, "manage.py", "makemigrations", "courses", "--noinput"],
            cwd=ROOT,
            check=True,
        )
        subprocess.run(
            [sys.executable, "manage.py", "migrate", "--noinput"],
            cwd=ROOT,
            check=True,
        )
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "test_vizsga.py", "-v", "--tb=short"],
            cwd=ROOT,
        )
        return result.returncode
    finally:
        for rel in BACKUP_RELS:
            backup_src = BACKUP / rel
            dst = ROOT / rel
            if dst.exists():
                if dst.is_dir():
                    shutil.rmtree(dst)
                else:
                    dst.unlink()
            if backup_src.exists():
                copy_tree(backup_src, dst)
        # Generált migrációk ne maradjanak a starterben
        migrations_dir = ROOT / "courses" / "migrations"
        for path in migrations_dir.glob("*.py"):
            if path.name != "__init__.py":
                path.unlink()
        db_path = ROOT / "db.sqlite3"
        if db_path.exists():
            db_path.unlink()
        if BACKUP.exists():
            shutil.rmtree(BACKUP)


if __name__ == "__main__":
    sys.exit(main())
