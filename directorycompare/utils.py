import os
import logging
from pathlib import Path
import csv

# Globals
DATA_FOLDER = "data"
LOG_FOLDER = "logs"


# Functions
def convert_to_path(folder_path):
    """
        Convert a string to Path either from root or current directory
    """
    path = Path(folder_path)
    if path.is_absolute():
        return path
    else:
        return Path(Path.cwd() / path).resolve()


def remove_recursive(path):
    """
        Removing folders recursively firstly by removing
        files within the folder and then the folder.
        Requires folder in path form.
        Includes removal of first supplied path.
    """
    logging.debug("remove_recursive: path: %s", path)
    if path.is_file():
        remove_file(path)
    else:
        while os.listdir(path):
            item = os.listdir(path)[0]
            item = path / item
            item = convert_to_path(item)
            logging.debug("item: %s", item)
            remove_recursive(item)
        remove_folder(path)


def remove_file(item):
    """
        Remove file (in Path form)
    """
    try:
        os.remove(item)
        logging.debug("File removed: %s", item)
    except OSError as error:
        print(error)


def remove_folder(folder):
    """
        Remove empty folder (in Path form)
    """
    try:
        os.rmdir(folder)
        logging.debug("Folder removed: %s", folder)
    except OSError as error:
        print(error)


def create_folders(folder):
    """
        Create folders supplied as a Path
        If folders already exist, do nothing
    """
    try:
        os.makedirs(folder)
        logging.debug("Created folder: %s", folder)
    except OSError:
        pass


def read_csv(filepath):
    """
        Reading CSV file as a ordered dictionary.

        fieldnames are not returned.
    """
    data = []
    with open(filepath, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # print(row)
            data.append(row)
    return data


def write_csv(data, filepath, fieldnames):
    """
        Write CSV file from dictionary to file.
    """
    logging.debug("Writing to file: %s", str(filepath))
    with open(filepath, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
