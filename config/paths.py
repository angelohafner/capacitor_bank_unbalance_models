# config/paths.py
# Comments in English only

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent

# Runtime output directories

TEX_DIR: Path = PROJECT_ROOT / "tex_files"
REPORT_DIR: Path = TEX_DIR / "reports"
FIG_DIR: Path = REPORT_DIR / "figs"
TABLE_DIR: Path = REPORT_DIR  / "tables"


# Static templates directory
TEMPLATE_DIR: Path = PROJECT_ROOT / "templates"

# Templates (kept for backward compatibility)
TEMPLATE_FI_TEX: Path = TEMPLATE_DIR / "TEMPLATE__FI.tex"
TEMPLATE_FE_TEX: Path = TEMPLATE_DIR / "TEMPLATE__FE.tex"
TEMPLATE_FI_HBRIDGE_TEX: Path = TEMPLATE_DIR / "TEMPLATE__FI_HBridge.tex"

# ATP runtime directory
ATP_DIR: Path = PROJECT_ROOT / "atp_files"


def ensure_directories() -> None:
    """
    Create required runtime directories if they do not exist (idempotent).
    """
    TEX_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ATP_DIR.mkdir(parents=True, exist_ok=True)
