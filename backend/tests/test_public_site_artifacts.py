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


def test_public_product_page_exposes_language_toggle() -> None:
    site_index = ROOT / "docs" / "index.html"
    html = site_index.read_text(encoding="utf-8")
    script = (ROOT / "docs" / "site.js").read_text(encoding="utf-8")

    assert "中文" in html
    assert "EN" in html
    assert "lang-switch" in html
    assert "跨境税收协定预审工具" in script


def test_public_product_page_script_supports_language_preference_persistence() -> None:
    site_script = ROOT / "docs" / "site.js"
    script = site_script.read_text(encoding="utf-8")

    assert "localStorage" in script
    assert "navigator.language" in script
    assert "zh" in script
    assert "en" in script


def test_public_product_page_has_dedicated_chinese_typography_rules() -> None:
    site_index = ROOT / "docs" / "index.html"
    site_css = ROOT / "docs" / "site.css"

    html = site_index.read_text(encoding="utf-8")
    css = site_css.read_text(encoding="utf-8")

    assert "Noto+Sans+SC" in html
    assert ':lang(zh-CN)' in css
    assert '"Noto Sans SC"' in css
