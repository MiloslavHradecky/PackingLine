# 🖨️ PackingLine

Desktop application that simulates line - B on an EOL tester based on Qt.

---

## 📋 Description

A desktop application that simulates line - B on an EOL tester.
Created in Python with PyQt6.
Structured according to MVC and distributed as an ".exe" file for Windows 11+.

---

## 🚀 Technologies

- **Python 3.10+**
- **PyQt6**
- **BarTender Integration**
- **BarTender Commander Integration**
- **ConfigParser**

---

## 📂 Structure

```
📦 PackingLine/
│
├── audit/
│   ├── audit.py
│   ├── audit_report_xxxx-xx-xx_xx-xx.txt
│   └── vulture_whitelist.txt
│
├── controllers/
│   ├── login_controller.py
│   ├── print_config_controller.py
│   ├── print_controller.py
│   ├── print_loader_controller.py
│   ├── print_logic_controller.py
│   ├── work_order_controller.py
│   └── product_controller.py
│
├── docs/
│   ├── home_terminal.md
│   ├── pyproject.md
│   ├── scheme.txt
│   └── work_terminal.md
│
├── logs/
│   ├── app.json
│   └── app.txt
│
├── models/
│   └── user_model.py
│
├── packingline.egg-info/
│   ├── dependency_links.txt
│   ├── entry_points.txt
│   ├── PKG-INFO
│   ├── requires.txt
│   ├── SOURCES.txt
│   └── top_level.txt
│
├── settings/
│   ├── config.ini
│   ├── create_config.py
│   ├── create_config_home_verso_2.0.py
│   ├── create_config_work_test_verso_2.0.py
│   └── create_test_config.py
│
├── utils/
│   ├── ensure_config_file.py
│   ├── ensure_logs_dir.py
│   ├── logger.py
│   ├── messenger.py
│   ├── path_validation.py
│   ├── resources.py
│   ├── single_instance.py
│   ├── system_info.py
│   ├── validators.py
│   ├── window_effects_manager.py
│   └── window_stack.py
│
├── views/
│   ├── assets/
│   │   ├── login.tiff
│   │   ├── main.ico
│   │   ├── message.ico
│   │   ├── print.png
│   │   ├── spinner.gif
│   │   ├── splash_logo.png
│   │   └── work_order_find.png
│   │
│   ├── themes/
│   │   └── style.qss
│   │
│   ├── login_window.py
│   ├── print_window.py
│   ├── splash_screen.py
│   └── work_order_window.py
│
├── .flake8
├── .gitignore
├── .pylintrc
├── config.ini
├── dev-requirements.in
├── dev-requirements.txt
├── LICENSE
├── main.py
├── pyproject.toml
├── README.md
├── requirements.in
├── requirements.txt
└── version.txt
```

---

## 🧑‍💻 Author

Developed with 💙 and precision by [Miloslav Hradecky]  
© 2025 — Built to print, parse & simplify 🎉