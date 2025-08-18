# Commands to create an exe file

## ManualLabelPrint

### 1. Open a session in a given folder

```Powershell
cd "C:\Users\Home\Documents\Coding\Python\PyQt\ManualLabelPrint\"
```

### 2. Create a .spec file

```Powershell
& "C:\Users\Home\AppData\Local\Programs\Python\Python313\python.exe" "C:\Users\Home\AppData\Local\Programs\Python\Python313\Scripts\pyinstaller.exe" --name=ManualLabelPrint --version-file=version.txt --noconfirm --onefile --noconsole --windowed --icon=view\assets\main.ico main.py
```

### 3. Edit the created .spec file

```Text
# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('view/assets/barcode.png', 'view/assets'),
        ('view/assets/login.tiff', 'view/assets'),
        ('view/assets/main.ico', 'view/assets'),
        ('view/assets/message.ico', 'view/assets'),
        ('view/assets/option.png', 'view/assets'),
        ('view/assets/order.png', 'view/assets'),
        ('view/assets/printer.png', 'view/assets'),
        ('view/assets/product.png', 'view/assets'),
        ('view/assets/service.png', 'view/assets'),
        ('view/assets/spinner.gif', 'view/assets'),
        ('view/assets/splash_logo.png', 'view/assets'),
        ('view/themes/style.qss', 'view/themes'),
        ('controller/', 'controller'),
        ('model/', 'model'),
        ('utils/', 'utils'),
        ('view/', 'view'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ManualLabelPrint',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version.txt',
    icon=['view/assets/main.ico'],
)
```

### 4. Create an .exe

```Powershell
& "C:\Users\Home\AppData\Local\Programs\Python\Python313\python.exe" "C:\Users\Home\AppData\Local\Programs\Python\Python313\Scripts\pyinstaller.exe" ManualLabelPrint.spec
```
