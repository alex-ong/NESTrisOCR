# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

template_dir = "assets/sprite_templates"

addedPath = os.getcwd() #adds current path to analysis search
sprite_templates = (template_dir+"/*", template_dir )
config = ('config.ini', '.')
added_files = [sprite_templates, config]
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
