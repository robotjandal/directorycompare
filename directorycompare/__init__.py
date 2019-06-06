from pathlib import Path
from directorycompare.utils import create_folders, DATA_FOLDER, LOG_FOLDER


data_path = Path.cwd() / DATA_FOLDER
logs_path = Path.cwd() / LOG_FOLDER

# Adding folders if not found
if not data_path.is_dir():
    create_folders(data_path)

if not logs_path.is_dir():
    create_folders(logs_path)
