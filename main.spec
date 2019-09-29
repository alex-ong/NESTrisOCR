# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

template_dir = "assets/sprite_templates"

sprite_templates = (template_dir+"/*", template_dir )
config = ('config.ini', '.')
added_files = [sprite_templates, config]
numba_dep = [('C:/Python37/Lib/site-packages/llvmlite/binding/llvmlite.dll','.')]
a = Analysis(['main.py'],
             pathex=['D:\\Dev\\NESTrisOCR'],
             binaries=numba_dep,
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
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
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='main')
