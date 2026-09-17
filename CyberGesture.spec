# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules


mediapipe_datas = collect_data_files("mediapipe")
mediapipe_hiddenimports = collect_submodules("mediapipe")


a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("assets/models/hand_landmarker.task", "assets/models"),
        ("assets/models/face_landmarker.task", "assets/models"),
        ("assets/icons/logo.png", "assets/icons"),
        ("assets/icons/icon.ico", "assets/icons"),
        ("cybercam/config/defaults.json", "cybercam/config"),
    ] + mediapipe_datas,
    hiddenimports=mediapipe_hiddenimports,
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
    [],
    exclude_binaries=True,
    name="CyberGesture",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon="assets/icons/icon.ico",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="CyberGesture",
)