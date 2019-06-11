import os
import logging
from pathlib import Path
import csv
import yaml

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


def read_yaml(path):
    """
        Reads from yaml file only if the yaml file exists.

        If no file exists nothing happens
    """
    if not path.is_file():
        logging.debug("File not found %s. No action taken", path)
        return
    try:
        with path.open('r') as f:
            data = yaml.safe_load(f)
        return data
    except IOError as e_info:
        print(e_info)
    except yaml.YAMLError as e_info:
        print("Failed to import file")
        print(e_info)


def write_yaml(path, data):
    """
        Write dictionary object to yaml file.
    """
    try:
        with path.open('w+') as f:
            yaml.dump(data, f, default_flow_style=False)
    except IOError as e_info:
        print(e_info)
