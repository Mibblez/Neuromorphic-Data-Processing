#!/bin/bash
set -euo pipefail

print_usage() {
    echo -e "usage: $0 [-d csv_directory] [-r]\n" >&2
    echo -e "required arguments:"
    echo "  -d        Directory containing csv files to plot"
    echo "  -x        X coordinate of the pixel to examine"
    echo "  -y        Y coordinate of the pixel to examine"
    echo "  -a        Size of area to plot"
    echo -e "optional arguments:"
    echo "  -t        Time limit for the X-axis (seconds)"
    echo "  -r        Recursively search through csv_directory"
    exit 2
}

set_variable() {
  local varname=$1
  shift
  if [ -z "${!varname+set}" ]; then
    eval "$varname=\"$@\""
  else
    echo "Error: $varname already set"
    print_usage
  fi
}

unset RECURSIVE_SEARCH FILES_DIR FILES_STRING PIXEL_X PIXEL_Y AREA_SIZE TIME_LIMIT

# Get args
while getopts 'rt:x:y:a:d:?h' option; do
  case "$option" in
    r) set_variable RECURSIVE_SEARCH true ;;
    d)
      # Make sure FILES_DIR is a directory
      if [ -d "$OPTARG" ]; then
        set_variable FILES_DIR $OPTARG
      else
        echo "'$OPTARG' is not a directory"
        exit 1
      fi
    ;;
    x)
      # Make sure the arg is int
      if [[ $OPTARG =~ ^[0-9]+$ ]]; then
        set_variable PIXEL_X $OPTARG
      else
        echo "ERROR: The value for -x must be an integer"
        print_usage
      fi
    ;;
    y)
      # Make sure the arg is int
      if [[ $OPTARG =~ ^[0-9]+$ ]]; then
        set_variable PIXEL_Y $OPTARG
      else
        echo "ERROR: The value for -y must be an integer"
        print_usage
      fi
    ;;
    a)
      # Make sure the arg is int
      if [[ $OPTARG =~ ^[0-9]+$ ]]; then
        set_variable AREA_SIZE $OPTARG
      else
        echo "ERROR: The value for -a must be an integer"
        print_usage
      fi
    ;;
    t)
      # Make sure the arg is int or float
      if [[ $OPTARG =~ ^[+-]?[0-9]*\.?[0-9]+$ ]]; then
        set_variable TIME_LIMIT $OPTARG
      else
        echo "ERROR: The value for -a must be an integer or float"
        print_usage
      fi
    ;;
    h|?) print_usage ;;
  esac
done

shift "$(($OPTIND -1))"

# Make sure required variables are set
if [ -z "${FILES_DIR+set}" ] || [ -z "${PIXEL_X+set}" ] || [ -z "${PIXEL_Y+set}" ] || [ -z "${AREA_SIZE+set}" ]; then
  print_usage
fi

if [ -z "${TIME_LIMIT+set}" ]; then
  TIME_LIMIT=""
else
  TIME_LIMIT="-t=$TIME_LIMIT"
fi

if [ ! -z "${RECURSIVE_SEARCH+set}" ]; then
  FILES_STRING=$(find $FILES_DIR -name "*.csv")
else
  FILES_STRING=$(find $FILES_DIR -maxdepth 1 -name "*.csv")
fi

FILES_ARRAY=($(echo $FILES_STRING | tr " " "\n"))

for file_path in "${FILES_ARRAY[@]}"; do
  echo $file_path
  python src/plotting/spikeGraph.py $file_path -x=$PIXEL_X -y=$PIXEL_Y -a=$AREA_SIZE $TIME_LIMIT
done
