# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

assets_dir = "nestris_ocr/assets"
palettes_dir = "nestris_ocr/palettes"

addedPath = os.getcwd() #adds current path to analysis search
asset_templates = ("nestris_ocr/assets/sprite_templates", "nestris_ocr/assets/sprite_templates")
palette_files = ("nestris_ocr/palettes", "nestris_ocr/palettes")

added_files = [asset_templates, palette_files]
a = Analysis(['main.py'],
             pathex=[addedPath],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['numba'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='main')
