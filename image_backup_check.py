"""
    Find differences between two directories 

    analyse: requires name and directory to be analysed
    compare: two files are selected and compared between them 
    TODO: expand 'compare' to take any number of files
"""

import os
import sys
import logging
import argparse
from pathlib import Path
import csv

logging.basicConfig(filename=('photo_check.log'), level=logging.DEBUG)

IMAGE_FORMATS = { '.jpg', '.jpeg', '.png' }
RAW_FORMATS = { '.arw' }
SOURCE_DIRECTORY = 'sources'

#### Functions
####
def preprocessing():
    """
        Create required folders
    """
    create_folders(convert_to_path(SOURCE_DIRECTORY))

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

def write_csv(data, filepath, fieldnames):
    """
        Write CSV file from dictionary to file.
    """
    logging.debug("Writing to file: %s", str(filepath))
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

#### Classes
####
class ArgCommandParse(object):
    """
        Parsing command line arguments to perform tasks for directory
        based comparing.
        
        Based on: 
        https://chase-seibert.github.io/blog/2014/03/21/python-multilevel-argparse.html#
    """
    def __init__(self):
        """
            Multi-level argument parsing based upon command issued.
        """
        self.command = ''
        self.options = {}
        parser = argparse.ArgumentParser(
            description='Directory equality checker',
            usage='''Commands: source
                 compare'''
        )
        parser.add_argument('command', help='Task to run')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print (f"Command not recognised")
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def source(self):
        """
            source command.
            Requring a name and at least one folder location.
        """
        self.command = 'source'
        parser = argparse.ArgumentParser(
            description='Add a new source directory',
        )
        parser.add_argument('name', metavar='name', type=str, nargs=1,
                            help='Name for source')
        parser.add_argument('folder', metavar='path', type=str, nargs='+',
                            help='Path to folder to be processed')
        args = parser.parse_args(sys.argv[2:])
        paths = []
        for folder in args.folder:
            paths.append(convert_to_path(folder))

        self.options = {
            'command': 'source',
            'name': args.name[0],
            'paths': paths
        }
        logging.debug("Adding new %s: %s", str(self.command), 
            str(self.options['name']))


    def compare(self):
        print('Not Implemented')


class AnalyseDirectory:
    """
        Analyse a given set of directories
        Clear already existing data for supplied source
		Retrieve information about each file
		Sort lists by name and save to file per file type
    """
    def __init__(self, commandline):
        self.name = commandline['name']
        self.paths = commandline['paths']
        self.file_data = {}
        self.output_folder = Path(SOURCE_DIRECTORY) / self.name
        if self.output_folder.is_dir():
            remove_recursive(self.output_folder)
        print(f"Adding new source: {self.name}")
        logging.info("Adding new source: %s", self.name)
    
    def analyse(self):
        """
            Using folder paths found, retrieve stats for files
            contained within and save data to csv.
        """
        files = self.gather_files()
        self.retrieve_stats(files)
        self.sort_data()
        self.save_data_to_file()

    def gather_files(self):
        """
            Go through specified folders and find all images separting raw image
			files.
        """
        print(f"Searching folders")
        folder_list = self.paths
        images = []
        raws = []
        while folder_list:
            contents, folders  = self.process_folder(folder_list.pop())
            folder_list.extend(folders)
            images.extend(contents['images'])
            raws.extend(contents['raws'])

        files = {
            'images': images,
            'raws': raws,
        }
        logging.debug("Total images found: %.0f", len(images))
        logging.debug("Total raws found: %.0f", len(raws))
        return files

    def process_folder(self, folder):
        """
            Takes a specific folder and returns a list of images, raw separate and
            nested folders.
        """
        #TODO: replace standalone lists to be dictionary of lists directly
        raws = []
        images = []
        folders = []
        logging.debug("Processing folder: %s", folder)
        for child in folder.iterdir():
            if child.suffix.lower() in IMAGE_FORMATS and child.is_file():
                images.append(child)
            elif child.suffix.lower() in RAW_FORMATS and child.is_file():
                raws.append(child)
            elif child.is_dir():
                folders.append(Path(child))
        logging.debug("Found folders: %.0f", len(folders))
        logging.debug("Found images: %.0f", len(images))
        logging.debug("Found raws: %.0f", len(raws))
        contents = {
            'images': images,
            'raws': raws,
        }
        return contents, folders
    
    def retrieve_stats(self, files):
        """
            Retrieve information about the file. 

            Image files can be analysed for further information compared with
            raw files.
        """
        print(f"Analysing files")
        logging.info("Analysing files")
        # for raws
        output_raw = []
        for path in files['raws']:
            full_path = Path(Path.home(), path)
            file_info = os.stat(full_path)
            output_raw.append(
                {
                    'name': path.name,
                    'path': str(full_path),
                    'size': file_info.st_size
                }
            )
        # for images
        output_images = []
        for path in files['images']:
            full_path = Path(Path.home(), path)
            file_info = os.stat(full_path)
            output_images.append(
                {
                    'name': path.name,
                    'path': str(full_path),
                    'size': file_info.st_size
                }
            )
        self.file_data = {
            'images': output_images,
            'raws': output_raw,
        }
        logging.debug('Images analysed: %.0f', len(output_images))
        logging.debug('Raws analysed: %.0f', len(output_raw))

    def sort_data(self):
        """
            file_data is sorted into ascending order
        """
        self.file_data['images'] = sorted(self.file_data['images'], key = lambda i: i['name']) 
        self.file_data['raws'] = sorted(self.file_data['raws'], key = lambda i: i['name']) 

    def save_data_to_file(self):
        """
            Save dictionary data to files based upon key name in folder 
			output_folder.
        """
        print(f"Saving data to {self.output_folder}")
        logging.info("Saving files to %s", self.output_folder)
        create_folders(self.output_folder)
        fieldnames = ['name', 'path', 'size']
        for key in self.file_data.keys():
            path = self.output_folder / (key + '.csv')
            write_csv(self.file_data[key], path, fieldnames)

#### Main
#### 
if __name__ == "__main__":
    preprocessing()
    args = ArgCommandParse()
    if args.command is 'source':
        action = AnalyseDirectory(args.options)
        action.analyse()   
    if args.command is 'compare':
        print(f"Not yet complete")     
    print(f"Success")
