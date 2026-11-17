"""Build the public web page from the Python catalog.

Writes docs/index.html, which GitHub Pages serves. Re-run after changing
demo_catalog() in adtech_agent_sim.py so the web and Python versions agree.

    python3 build_web.py
"""

import dataclasses
import json
from pathlib import Path

from adtech_agent_sim import demo_catalog

ROOT = Path(__file__).parent
TEMPLATE = ROOT / "web" / "template.html"
OUTPUT = ROOT / "docs" / "index.html"
PLACEHOLDER = "/*CATALOG*/[]"


def main() -> None:
    catalog = [dataclasses.asdict(p) for p in demo_catalog()]
    template = TEMPLATE.read_text(encoding="utf-8")
    if template.count(PLACEHOLDER) != 1:
        raise SystemExit(f"expected exactly one {PLACEHOLDER!r} in {TEMPLATE}")
    OUTPUT.write_text(
        template.replace(PLACEHOLDER, json.dumps(catalog, indent=1)),
        encoding="utf-8",
    )
    print(f"Wrote {OUTPUT} with {len(catalog)} products")


if __name__ == "__main__":
    main()
