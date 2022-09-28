#!/bin/bash
set -euo pipefail

print_usage() {
    echo -e "usage: $0 [-d csv_directory] [-x x_lim] [-r]\n" >&2
    echo -e "required arguments:"
    echo "  -d        Directory containing csv files to plot"
    echo -e "optional arguments:"
    echo "  -x        X-Limit for the plot"
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

unset RECURSIVE_SEARCH X_LIM FILES_DIR FILES_STRING

# Get args
while getopts 'rx:d:?h' option; do
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
      # Make sure the arg is int or float
      if [[ $OPTARG =~ ^[+-]?[0-9]*\.?[0-9]+$ ]]; then
        set_variable X_LIM $OPTARG
      else
        echo "ERROR: x_lim must be an integer or float"
        print_usage
      fi
    ;;
    h|?) print_usage ;;
  esac
done

shift "$(($OPTIND -1))"

# Make sure required variables are set
if [ -z "${FILES_DIR+set}" ]; then
  print_usage
fi

if [ ! -z "${RECURSIVE_SEARCH+set}" ]; then
  FILES_STRING=$(find $FILES_DIR -name "*.csv")
else
  FILES_STRING=$(find $FILES_DIR -maxdepth 1 -name "*.csv")
fi

FILES_ARRAY=($(echo $FILES_STRING | tr " " "\n"))

for file_path in "${FILES_ARRAY[@]}"; do
  if [ ! -z "${X_LIM+set}" ]; then
    echo $file_path
    python src/plotting/fingerprintGraph.py $file_path -x $X_LIM
  else
    echo $file_path
    python src/plotting/fingerprintGraph.py $file_path
  fi
done
