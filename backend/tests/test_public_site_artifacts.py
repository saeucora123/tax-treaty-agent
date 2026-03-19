from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_readme_links_to_public_product_overview() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "Open product overview" in readme
    assert "https://saeucora123.github.io/tax-treaty-agent/" in readme


def test_public_product_page_exists_with_expert_facing_tax_copy() -> None:
    site_index = ROOT / "docs" / "index.html"

    assert site_index.exists()

    html = site_index.read_text(encoding="utf-8")
    assert "Cross-border treaty pre-screening for international tax teams" in html
    assert "Start with a faster first-pass review" in html
    assert "This tool does not replace a final tax opinion" in html
