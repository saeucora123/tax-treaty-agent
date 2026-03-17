from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = REPO_ROOT / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from app.guided_facts import build_frontend_contract_source

OUTPUT_PATH = REPO_ROOT / "frontend" / "src" / "generated" / "contract.ts"


def main() -> int:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(build_frontend_contract_source() + "\n", encoding="utf-8")
    print(f"Wrote frontend contract: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
