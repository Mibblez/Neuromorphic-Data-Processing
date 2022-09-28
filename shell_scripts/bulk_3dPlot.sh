#!/bin/bash
set -euo pipefail

print_usage() {
    echo -e "usage: $0 [-d csv_directory] [-v default|top|side|all] [-r] [-t time_limit]\n" >&2
    echo -e "required arguments:"
    echo "  -d        Directory containing csv files to plot"
    echo "  -v        Plot viewing angle [default, top, side, all]"
    echo -e "optional arguments:"
    echo "  -r        Recursively search through csv_directory"
    echo "  -t        Time limit for the Z-axis (seconds)"
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

unset RECURSIVE_SEARCH VIEW_ANGLE FILES_DIR FILES_STRING TIME_LIMIT
VIEW_ANGLES=("default" "top" "side" "all")

# Get args
while getopts 'rt:v:d:?h' option; do
  case "$option" in
    r) set_variable RECURSIVE_SEARCH true ;;
    t)
      if [[ $OPTARG =~ ^[+-]?[0-9]*\.?[0-9]+$ ]]; then
        set_variable TIME_LIMIT $OPTARG
      else
        echo "ERROR: time_limit must be an integer or float"
        print_usage
      fi
    ;;
    d)
      # Make sure FILES_DIR is a directory
      if [ -d "$OPTARG" ]; then
        set_variable FILES_DIR $OPTARG
      else
        echo "'$OPTARG' is not a directory"
        exit 1
      fi
    ;;
    v)
      # Make sure the arg is a valid viewing angle
      if [[ "${VIEW_ANGLES[@]}" =~ "${OPTARG}" ]]; then
        set_variable VIEW_ANGLE $OPTARG
      else
        echo "ERROR: Invalid view angle"
        print_usage
      fi
    ;;
    h|?) print_usage ;;
  esac
done

shift "$(($OPTIND -1))"

# Make sure required variables are set
if [ -z "${FILES_DIR+set}" ] || [ -z "${VIEW_ANGLE+set}" ]; then
  print_usage
fi

if [ ! -z "${RECURSIVE_SEARCH+set}" ]; then
  FILES_STRING=$(find $FILES_DIR -name "*.csv")
else
  FILES_STRING=$(find $FILES_DIR -maxdepth 1 -name "*.csv")
fi

FILES_ARRAY=($(echo $FILES_STRING | tr " " "\n"))

for file_path in "${FILES_ARRAY[@]}"; do
  if [ ! -z "${TIME_LIMIT+set}" ]; then
    echo $file_path
    python src/plotting/3dplot.py $file_path -v $VIEW_ANGLE -t=$TIME_LIMIT
  else
    echo $file_path
    python src/plotting/3dplot.py $file_path -v $VIEW_ANGLE
  fi
done
