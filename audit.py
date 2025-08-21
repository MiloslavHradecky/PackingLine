import os
from datetime import datetime

# 📁 Název výstupního souboru
report_file = "audit_report.txt"

# 🕒 Timestamp pro začátek reportu
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 📦 Cílová složka projektu
target_folder = "PackingLine"

# 📝 Spuštění auditovacích nástrojů
with open(report_file, "w", encoding="utf-8") as report:
    report.write(f"📋 AUDIT REPORT — {timestamp}\n")
    report.write("=" * 60 + "\n\n")

    # 🔍 VULTURE
    report.write("🔍 VULTURE — nevyužitý kód:\n")
    report.write("-" * 40 + "\n")
    report.write(os.popen(f"vulture {target_folder}").read())
    report.write("\n\n")

    # 🧼 FLAKE8
    report.write("🧼 FLAKE8 — styl a chyby:\n")
    report.write("-" * 40 + "\n")
    report.write(os.popen(f"flake8 {target_folder}").read())
    report.write("\n\n")

    # 🧠 PYLINT
    report.write("🧠 PYLINT — statická analýza:\n")
    report.write("-" * 40 + "\n")
    report.write(os.popen(f"pylint {target_folder}").read())
    report.write("\n\n")

print(f"✅ Audit dokončen. Výstup uložen do: {report_file}")
