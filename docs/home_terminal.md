# Commands to create an exe file

## PackingLine

### 1. Open a session in a given folder

```Powershell
cd "C:\Users\Home\Documents\Coding\Python\PyQt\PackingLine\"
```

### 2. Create a .spec file

```Powershell
& "C:\Users\Home\AppData\Local\Programs\Python\Python313\python.exe" "C:\Users\Home\AppData\Local\Programs\Python\Python313\Scripts\pyinstaller.exe" --name=LineB --version-file=version.txt --noconfirm --onefile --noconsole --windowed --icon=views\assets\main.ico main.py
```

### 3. Edit the created .spec file

```Text
# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('views/assets/login.tiff', 'views/assets'),
        ('views/assets/main.ico', 'views/assets'),
        ('views/assets/message.ico', 'views/assets'),
        ('views/assets/print.png', 'views/assets'),
        ('views/assets/work_order_find.png', 'views/assets'),
        ('views/assets/spinner.gif', 'views/assets'),
        ('views/assets/splash_logo.png', 'views/assets'),
        ('views/themes/style.qss', 'views/themes'),
        ('controllers/', 'controllers'),
        ('models/', 'models'),
        ('utils/', 'utils'),
        ('views/', 'views'),
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
    name='LineB',
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
    icon=['views/assets/main.ico'],
)
```

### 4. Create an .exe

```Powershell
& "C:\Users\Home\AppData\Local\Programs\Python\Python313\python.exe" "C:\Users\Home\AppData\Local\Programs\Python\Python313\Scripts\pyinstaller.exe" LineB.spec
```
