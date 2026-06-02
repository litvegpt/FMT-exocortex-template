#!/usr/bin/env python3
"""
Синхронизирует communication-style-base.md с downstream-файлами.
Вставляет базовые правила между маркерами COMMUNICATION-STYLE-BASE-START/END.

Запуск:
    python3 scripts/sync-communication-style.py

Downstream-файлы настраиваются в списке DOWNSTREAM_FILES ниже.
"""

import re
import sys
from pathlib import Path

# Относительно корня FMT-шаблона
BASE_FILE = Path("memory/communication-style-base.md")

# Маркеры для markdown-файлов
MD_START = "<!-- COMMUNICATION-STYLE-BASE-START -->"
MD_END = "<!-- COMMUNICATION-STYLE-BASE-END -->"

# Маркеры для JS/TS файлов
JS_START = "// COMMUNICATION-STYLE-BASE-START"
JS_END = "// COMMUNICATION-STYLE-BASE-END"

# Список downstream-файлов: (путь относительно корня FMT, тип)
DOWNSTREAM_FILES = [
    ("AGENTS.md", "markdown"),
    ("CLAUDE.md", "markdown"),
    ("../DS-IT-systems/aist_bot_newarchitecture/config/standard_claude.md", "markdown"),
    ("../DS-MCP/gateway-mcp/src/index.ts", "js"),
]


def read_base_content() -> str:
    """Читает communication-style-base.md и убирает frontmatter."""
    path = Path(__file__).parent.parent / BASE_FILE
    if not path.exists():
        print(f"ERROR: base file not found: {path}", file=sys.stderr)
        sys.exit(1)

    text = path.read_text(encoding="utf-8")
    # Убираем YAML frontmatter
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            text = parts[2]
    return text.strip()


def update_markdown(path: Path, base_content: str) -> bool:
    """Обновляет markdown-файл между MD маркерами."""
    if not path.exists():
        print(f"WARNING: file not found: {path}")
        return False

    text = path.read_text(encoding="utf-8")
    pattern = f"({re.escape(MD_START)})\\n*.*?\\n*({re.escape(MD_END)})"
    replacement = f"{MD_START}\\n\\n{base_content}\\n\\n{MD_END}"
    new_text, count = re.subn(pattern, replacement, text, flags=re.DOTALL)

    if count == 0:
        print(f"WARNING: markers not found in {path}")
        return False

    path.write_text(new_text, encoding="utf-8")
    print(f"  OK  {path}")
    return True


def update_js(path: Path, base_content: str) -> bool:
    """Обновляет JS/TS файл между JS маркерами внутри template literal."""
    if not path.exists():
        print(f"WARNING: file not found: {path}")
        return False

    text = path.read_text(encoding="utf-8")
    # Экранируем для JS template literal
    escaped = base_content.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    pattern = f"({re.escape(JS_START)})\\n*.*?\\n*({re.escape(JS_END)})"
    replacement = f"{JS_START}\\n{escaped}\\n{JS_END}"
    new_text, count = re.subn(pattern, replacement, text, flags=re.DOTALL)

    if count == 0:
        print(f"WARNING: markers not found in {path}")
        return False

    path.write_text(new_text, encoding="utf-8")
    print(f"  OK  {path}")
    return True


def main():
    base = read_base_content()
    fmt_root = Path(__file__).parent.parent
    ok_count = 0
    skip_count = 0

    print(f"Syncing base ({len(base)} chars) to downstream files...")
    for rel_path, ftype in DOWNSTREAM_FILES:
        path = fmt_root / rel_path
        if not path.exists():
            print(f"SKIP {rel_path} (not found)")
            skip_count += 1
            continue
        if ftype == "markdown":
            if update_markdown(path, base):
                ok_count += 1
        elif ftype == "js":
            if update_js(path, base):
                ok_count += 1
        else:
            print(f"UNKNOWN type {ftype} for {rel_path}")
            skip_count += 1

    print(f"Done: {ok_count} updated, {skip_count} skipped.")
    return 0 if skip_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
