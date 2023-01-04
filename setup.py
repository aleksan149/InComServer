

from setuptools import setup

APP = ['play_pwb.py']
DATA_FILES = ['resources/']
OPTIONS = {"iconfile": "icon.icns",
           'plist': {'CFBundleName': 'InComServer_demo'}
           }

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
