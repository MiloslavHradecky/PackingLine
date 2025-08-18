# 🖨️ ManualLabelPrint

Desktop application for printing labels using MLP database based on Qt.

---

## 📋 Description

Desktop application for printing labels, built in Python with PyQt6.
Structured according to MVC and distributed as '.exe' for Windows 11+.

---

## 🚀 Technologies

- **Python 3.10+**
- **PyQt6**
- **BarTender Commander Integration**
- **ConfigParser**

---

## 📂 Structure

```
📦 ManualLabelPrint/
│
├── controller/
│   ├── check_snc_controller.py
│   ├── login_controller.py
│   ├── manual_controller.py
│   ├── manual_pcs_controller.py
│   ├── multipack_controller.py
│   ├── option_controller.py
│   ├── product_controller.py
│   ├── serialization_controller.py
│   └── service_controller.py
│
├── docs/
│   ├── home_terminal.md
│   ├── scheme.txt
│   └── work_terminal.md
│
├── logs/
│   ├── app.json
│   └── app.txt
│
├── model/
│   └── user_model.py
│
├── utils/
│   ├── ensure_config_file.py
│   ├── ensure_logs_dir.py
│   ├── logger.py
│   ├── messenger.py
│   ├── resources.py
│   ├── single_instance.py
│   ├── system_info.py
│   ├── window_effects_manager.py
│   └── window_stack.py
│
├── view/
│   ├── assets/
│   │   ├── barcode.png
│   │   ├── login.tiff
│   │   ├── main.ico
│   │   ├── message.ico
│   │   ├── option.png
│   │   ├── order.png
│   │   ├── printer.png
│   │   ├── product.png
│   │   ├── service.png
│   │   ├── spinner.gif
│   │   └── splash_logo.png
│   │
│   ├── themes/
│   │   └── style.qss
│   │
│   ├── login_window.py
│   ├── manual_pcs_window.py
│   ├── manual_window.py
│   ├── multipack_window.py
│   ├── option_window.py
│   ├── product_window.py
│   ├── serialization_window.py
│   ├── service_window.py
│   └── splash_screen.py
│
├── .gitignore
├── config.ini
├── LICENSE
├── main.py
├── README.md
└── version.txt
```

---

## 🧑‍💻 Author

Developed with 💙 and precision by [Miloslav Hradecky]  
© 2025 — Built to print, parse & simplify 🎉