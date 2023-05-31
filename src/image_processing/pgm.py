import csv
import sys
import argparse
import os
import pathlib

from plotting_utils.plotting_helper import file_arg, path_arg, int_arg_positive_nonzero, check_aedat_csv_format


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "aedat_csv_file", help="CSV containing AEDAT data to be plotted (On,Off,Both,PGM_String)", type=file_arg
    )
    parser.add_argument(
        "--max_images",
        "-i",
        help="Max number of pgm images to extract",
        type=int_arg_positive_nonzero,
        default="default"
    )
    parser.add_argument("--save_directory", "-d", help="Save file to directory", type=path_arg, default=".")

    return parser.parse_args()


def main(args: argparse.Namespace):
    csv_file = args.aedat_csv_file
    max_images = args.max_images

    with open(csv_file, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")

        header = next(reader, None)  # Grab the header
        if header is None:
            raise ValueError(f"Error: File '{csv_file}' seems to be empty")

        # Strip whitespace from header if there is any
        header = [x.strip(" ") for x in header]

        if not check_aedat_csv_format(header, ["PGM_String"]):
            sys.exit(
                f"File {csv_file} does not contain a PGM_String column"
            )

        pgm_index = header.index("PGM_String")

        first_row = next(reader, None)
        if first_row is None:
            raise ValueError(f"Error: File '{csv_file}' has a header but contains no data")

        image_count = 0
        for row in reader:
            if image_count >= max_images:
                break

            pgm_string = row[pgm_index]
            pgm_string = pgm_string.replace('-', '\n')

            csv_stem = pathlib.Path(csv_file).stem
            filename = f"{csv_stem}_{image_count}"
            output_path = os.path.join(args.save_directory, filename)

            with open(output_path, 'w') as pgm_file:
                pgm_file.write(pgm_string)

            image_count += 1


if __name__ == "__main__":
    args = get_args()
    main(args)
