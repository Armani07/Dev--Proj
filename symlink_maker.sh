#!/bin/bash
#
# Create Symlink from current directory to symlink path argument.

# Prints Script's Usage Statement
# Global: None
# Arguments: None
# Returns: None
usage() {
  echo "${0} [-h] [source] <symlink>"
  echo " -h        Prints Usage Statement and exits."
  echo " [source]  Optional Source Location Path, default is Current Working Directory"
  echo " <symlink> Path to Symlink File"
}

#################### Argument Management ####################
OPTIND=1 # Reset in case getopts has been used previously in the shell.
while getopts ":h" opt; do
    case "${opt}" in
    h)
        usage
        exit 0
        ;;
    ?)
        echo "ERROR: ${OPTARG} is not a valid argument"
        usage
        exit 1
        ;;
    esac
done
shift $((OPTIND-1))

# Handle Mass-Positional Arguments
if [[ "${#}" -eq 1 ]]; then
    SYMLINK_SOURCE="${PWD}"
    SYMLINK_FILE="${1}"
elif [[ "${#}" -eq 2 ]]; then
    SYMLINK_SOURCE="${1}"
    SYMLINK_FILE="${2}"
else
    echo "Too many or Missing argument(s)." >&2
    usage >&2
    exit 1
fi
#################### End Argument Management ####################

if [[ ! -d "${SYMLINK_FILE}" ]]; then
    ln -s "${SYMLINK_SOURCE}" "${SYMLINK_FILE}"
fi

exit 0
