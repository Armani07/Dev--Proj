#!/bin/bash
#
# Create a python Virtual Environment.
# Uses a requirements.txt file to install libraries, if available.


PYTHON_EXE="python2"
VENV_NAME="venv"
QUIET="0"
REQUIREMENTS_FILE="requirements.txt"

# Prints Script's Usage Statement
# Global: None
# Arguments: None
# Returns: None
usage() {
    echo "${0} [-h] [-p python_exe] [-n venv_name] [-q | -r requirements_file]"
    echo " -h     Prints Usage Statement and exits."
    echo " -p PYTHON_EXE"
    echo "        The Python interpreter to use, ie. -p python2.7"
    echo "        Defaults to python2"
    echo " -n VENV_NAME"
    echo "        The name of the Virtual Environment, ie. -n venv-projectname"
    echo "        defaults to just venv"
    echo " -q     Create Virtual Environment, but don't install any libraries"
    echo " -r REQUIREMENTS_FILE"
    echo "        The file of libraries to install into the Virtual Environment"
    echo "        defaults to requirements.txt in the current directory"
}

#################### Argument Management ####################
OPTIND=1 # Reset in case getopts has been used previously in the shell.
while getopts ":hqp:n:r:" opt; do
    case "${opt}" in
    h)
        usage
        exit 0
        ;;
    p)
        PYTHON_EXE="${OPTARG}"
        ;;
    n)
        VENV_NAME="${OPTARG}"
        ;;
    q)
        QUIET="1"
        ;;
    r)
        REQUIREMENTS_FILE="${OPTARG}"
        ;;
    \?)
        echo "ERROR: ${OPTARG} is not a valid argument" >&2
        usage >&2
        exit 1
        ;;
    esac
done
shift $((OPTIND-1))

#################### End Argument Management ####################

if [[ "$(command -v virtualenv)" && "$(command -v "${PYTHON_EXE}")" ]]; then
    if [[ ! -d "${VENV_NAME}" ]]; then
        # Create Virutal Environment
        virtualenv -p "${PYTHON_EXE}" "${VENV_NAME}" 2>&2
    else
        echo "WARNING: Virtual Environment Directory already exists" >&2
    fi
    if [[ "${QUIET}" -eq 0 ]]; then
        if [[ "$(command -v pip)" && -e "${REQUIREMENTS_FILE}" ]]; then
            # Install Libraries in Virtual Environment
            # shellcheck source=/dev/null
            source "${VENV_NAME}/bin/activate"
            pip install -r "${REQUIREMENTS_FILE}" 2>&2
            deactivate
        else
            echo "ERROR: pip command or requirements file not found" >&2
            exit 1
        fi
    fi
else
    echo "ERROR: virtualenv command or python interpreter not found" >&2
    exit 1
fi

exit 0
