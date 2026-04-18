"""Force-upsert all compounds from compoundGameList.ts into the DB."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database import init_db
from app.services.compound_seed_service import _load_compounds_from_seed_file
from app.repositories.compound_repository import upsert_compounds

seed_path = Path(__file__).parent.parent / "compoundGameList.ts"
if not seed_path.exists():
    print(f"Seed file not found: {seed_path}")
    sys.exit(1)

init_db()
compounds = _load_compounds_from_seed_file(seed_path)
count = upsert_compounds(compounds)
print(f"Upserted {count} compounds.")
