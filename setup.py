from setuptools import setup

APP = ['ebook_capture.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'CFBundleName': 'Ebook Capture',
        'CFBundleShortVersionString': '1.0',
        'CFBundleIdentifier': 'com.example.ebookcapture',
        'CFBundlePackageType': 'APPL',
    },
    'iconfile': 'ebook_capture.icns',
    'packages': [],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
