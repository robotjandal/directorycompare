"""
    Find file diferences between two directories

    analyse: requires name and directory to be analysed
    compare: two files are selected and compared between them
    TODO: expand 'compare' to take any number of files
"""

import logging

from directorycompare.directorycompare import (
    ArgCommandParse,
    AnalyseDirectory,
    CompareSources,
)

logging.basicConfig(filename=("logs/app.log"), level=logging.DEBUG)


def run():
    args = ArgCommandParse()
    if args.command == "source":
        action = AnalyseDirectory(args.options)
        action.analyse()
    if args.command == "compare":
        action = CompareSources(args.options)
        action.compare()
    print(f"Success!")
