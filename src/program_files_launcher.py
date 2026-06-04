#!/usr/bin/python3

'''
## ubuntu ##
python3 -m venv venv-temporal
source venv-temporal/bin/activate
pip install --upgrade pip

## windows ##
python -m venv venv-temporal
venv-temporal\Scripts\activate
python -m pip install --upgrade pip


pip install pyinstaller pyinstaller-hooks-contrib
pip install -r requirements.txt
cd src


## ubuntu ##
python3 -m PyInstaller --onefile --windowed --name list_data_tools --add-data "list_data_tools/icons:icons" --collect-all PyQt5  program_files_launcher.py

## windows ##
python -m PyInstaller --onefile --windowed --name list_data_tools --add-data "list_data_tools/icons;icons" --collect-all PyQt5  program_files_launcher.py

'''

import os
from PyQt5.QtCore import QLibraryInfo

os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = QLibraryInfo.location(
    QLibraryInfo.PluginsPath
)

from list_data_tools.program_files import main

if __name__ == "__main__":
    main()

