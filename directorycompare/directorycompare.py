import sys
import logging
import argparse
import os
from pathlib import Path
from directorycompare import utils

IMAGE_FORMATS = {".jpg", ".jpeg", ".png"}
RAW_FORMATS = {".arw"}


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
        self.command = ""
        self.options = {}
        parser = argparse.ArgumentParser(
            description="Directory equality checker",
            usage="""Commands: source
                 compare""",
        )
        parser.add_argument("command", help="Task to run")
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print(f"Command not recognised")
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def source(self):
        """
            source command.
            Requring a name and at least one folder location.
        """
        self.command = "source"
        parser = argparse.ArgumentParser(
            description="Add a new source directory"
        )
        parser.add_argument(
            "name", metavar="name", type=str, nargs=1, help="Name for source"
        )
        parser.add_argument(
            "folder",
            metavar="path",
            type=str,
            nargs="+",
            help="Path to folder to be processed",
        )
        args = parser.parse_args(sys.argv[2:])
        paths = []
        for folder in args.folder:
            paths.append(utils.convert_to_path(folder))

        self.options = {
            "command": "source",
            "name": args.name[0],
            "paths": paths,
        }
        logging.debug(
            "Adding new %s: %s", str(self.command), str(self.options["name"])
        )

    def compare(self):
        print("Not Implemented")


class AnalyseDirectory:
    """
        Analyse a given set of directories
        Clear already existing data for supplied source
        Retrieve information about each file
        Sort lists by name and save to file per file type
    """

    def __init__(self, commandline):
        self.name = commandline["name"]
        self.paths = commandline["paths"]
        self.file_data = {}
        self.output_folder = Path(utils.SOURCE_DIRECTORY) / self.name
        if self.output_folder.is_dir():
            utils.remove_recursive(self.output_folder)
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
            contents, folders = self.process_folder(folder_list.pop())
            folder_list.extend(folders)
            images.extend(contents["images"])
            raws.extend(contents["raws"])

        files = {"images": images, "raws": raws}
        logging.debug("Total images found: %.0f", len(images))
        logging.debug("Total raws found: %.0f", len(raws))
        return files

    def process_folder(self, folder):
        """
            Takes a specific folder and returns a list of images, raw separate
            and nested folders.
        """
        # TODO: replace standalone lists to be dictionary of lists directly
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
        contents = {"images": images, "raws": raws}
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
        for path in files["raws"]:
            full_path = Path(Path.home(), path)
            file_info = os.stat(full_path)
            output_raw.append(
                {
                    "name": path.name,
                    "path": str(full_path),
                    "size": file_info.st_size,
                }
            )
        # for images
        output_images = []
        for path in files["images"]:
            full_path = Path(Path.home(), path)
            file_info = os.stat(full_path)
            output_images.append(
                {
                    "name": path.name,
                    "path": str(full_path),
                    "size": file_info.st_size,
                }
            )
        self.file_data = {"images": output_images, "raws": output_raw}
        logging.debug("Images analysed: %.0f", len(output_images))
        logging.debug("Raws analysed: %.0f", len(output_raw))

    def sort_data(self):
        """
            file_data is sorted into ascending order
        """
        self.file_data["images"] = sorted(
            self.file_data["images"], key=lambda i: i["name"]
        )
        self.file_data["raws"] = sorted(
            self.file_data["raws"], key=lambda i: i["name"]
        )

    def save_data_to_file(self):
        """
            Save dictionary data to files based upon key name in folder
            output_folder.
        """
        logging.info("Saving files to %s", self.output_folder)
        utils.create_folders(self.output_folder)
        fieldnames = ["name", "path", "size"]
        for key in self.file_data.keys():
            path = self.output_folder / (key + ".csv")
            utils.write_csv(self.file_data[key], path, fieldnames)
        print(f"Saved under {self.output_folder}")


class CompareSources:
    """
        The primary source is compared against each secondary source.
        Comparison is based on available

        primary is the first source listed
        secondary_sources are a list of all other sources
    """

    def __init__(self, commandline):
        self.primary = commandline["primary"]
        self.secondary_sources = commandline["scondary"]
        self.file_data = {}
        # self.output_folder = Path(utils.SOURCE_DIRECTORY) / self.name
        # if self.output_folder.is_dir():
        #     utils.remove_recursive(self.output_folder)
        # print(f"Adding new source: {self.name}")
        # logging.info("Adding new source: %s", self.name)


def missing_files_lists(list1, list2):
    """
        Returns missing dictionary elements from two lists.

        output_list is a list of dictionary items
        list1 is assumed to be smaller in size.
    """
    difference = []
    # TODO: instead of reverse try to access from [-1]
    list1.reverse()
    while list1:
        item = list1.pop()
        if item in list2:
            print("exists")
            list2.remove(item)
        else:
            print("not there")
            difference.append(item)

    difference.extend(list2)
    return difference


def missing_files_dictionary():
    pass
