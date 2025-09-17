"""
Auditovací skript pro kontrolu kvality kódu.

Spouští nástroje Vulture, Flake8 a Pylint nad aktuální složkou nebo soubory,
sbírá výstupy a ukládá je do souboru audit_report_<timestamp>.txt.

Používá se pro ruční kontrolu čistoty a stylu kódu mimo hlavní aplikaci.

Bash: python audit/audit.py
"""

import os
import re
from datetime import datetime

# 🔍 Cesty a výjimky
TARGET_PATH = "."
EXCLUDED_DIRS = {"venv", ".venv", "__pycache__", ".git", "audit", "settings", "build", "dist", "docs", "installer", "logs", "setup"}
EXCLUDED_FILES = {
    "audit.py", "config.ini", "requirements.txt", "README.md",
    "vulture_whitelist.txt", "setup.py"
}


# 📦 Sběr souborů pro analýzu
def get_python_files():
    files = []
    for root, dirs, filenames in os.walk(TARGET_PATH):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for filename in filenames:
            if filename.endswith(".py") and filename not in EXCLUDED_FILES:
                full_path = os.path.join(root, filename)
                files.append(full_path)
    return files


# 📝 Zápis do reportu
def write_section(report, title, content):
    report.write(f"{title}\n")
    report.write("-" * 60 + "\n")
    report.write(content.strip() + "\n\n")


# 🧹 Filtrace výstupu Vulture (ignorujeme falešné pozitivy)
def parse_vulture_line(line: str) -> dict | None:
    match = re.match(r"^(.*?):(\d+): (unused \w+) '(.+?)'(?: in class '(.+?)')?", line)
    if not match:
        return None
    return {
        "file": match.group(1),
        "line": int(match.group(2)),
        "type": match.group(3),
        "name": match.group(4),
        "class": match.group(5) or "",
    }


def load_whitelist(path="audit/vulture_whitelist.txt") -> list[dict]:
    entries = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                match = re.match(r"(unused \w+) '(.+?)'(?: in class '(.+?)')?", line)
                if match:
                    entries.append({
                        "type": match.group(1),
                        "name": match.group(2),
                        "class": match.group(3) or "",
                    })
    except FileNotFoundError:
        pass
    return entries


def filter_vulture_output(output: str) -> str:
    whitelist = load_whitelist()
    lines = output.splitlines()
    filtered = []

    for line in lines:
        parsed = parse_vulture_line(line)

        # Ignoruj celý soubor vulture_whitelist.py
        if parsed and "vulture_whitelist.py" in parsed["file"]:
            continue

        # Ignoruj konkrétní metodu format v JsonFormatter
        if parsed and parsed["file"].endswith("utils/logger.py") and parsed["name"] == "format" and parsed["class"] == "JsonFormatter":
            continue

        # Ignoruj podle whitelistu
        if parsed and any(
                parsed["type"] == entry["type"] and
                parsed["name"] == entry["name"] and
                parsed["class"] == entry["class"]
                for entry in whitelist
        ):
            continue

        filtered.append(line)

    return "\n".join(filtered)


# 🚀 Spuštění auditů
def run_audit():
    python_files = get_python_files()

    if os.path.exists("main.py"):
        python_files.insert(0, "main.py")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    report_name = os.path.join("audit", f"audit_report_{timestamp}.txt")

    with open(report_name, "w", encoding="utf-8") as report:
        # 🔍 VULTURE
        vulture_cmd = f"vulture {' '.join(python_files)}"
        vulture_output = os.popen(vulture_cmd).read()
        vulture_output = filter_vulture_output(vulture_output)
        write_section(report, "🔍 VULTURE — nevyužitý kód", vulture_output)

        # 🧼 FLAKE8
        flake8_cmd = f"flake8 {' '.join(python_files)}"
        flake8_output = os.popen(flake8_cmd).read()
        write_section(report, "🧼 FLAKE8 — styl a chyby", flake8_output)

        # 🧠 PYLINT
        pylint_output = ""
        for file in python_files:
            pylint_cmd = f"pylint {file}"
            pylint_output += f"\n📄 {file}\n"
            pylint_output += os.popen(pylint_cmd).read()
        write_section(report, "🧠 PYLINT — hloubková analýza", pylint_output)

    print(f"✅ Audit dokončen. Výsledky najdeš v {report_name}")


# ▶️ Spusť audit
if __name__ == "__main__":
    run_audit()
