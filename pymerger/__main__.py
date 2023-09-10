import argparse
from .merger import merge

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-o',
        type=str,
        default="merged_files.py",
        help='output file, default is "merged_files.py"',
    )
    parser.add_argument(
        'filepaths',
        type=str,
        nargs="*",
        help='Filepaths of the files to be merged',
    )
    args = parser.parse_args()
    output_file = args.o

    merged_string = merge(args.filepaths, output=output_file)
