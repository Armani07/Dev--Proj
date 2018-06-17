#!/bin/bash
#
# Logging Package that attempts to emulate the Python logging module
# Usage:
#
# source mxorc_logger.sh
# Logger object_name [logger_name] [logger_level]
# object_name::warn "Warning Message"

#property indices
declare -rx LOGGER_NAME=0
declare -rx LOGGER_LEVEL=1

#logging levels
declare -rx LOGGER_DEBUG=10
declare -rx LOGGER_INFO=20
declare -rx LOGGER_WARN=30
declare -rx LOGGER_ERROR=40
declare -rx LOGGER_CRITICAL=50

# Logger Constructor
# Globals:
#     None
# Arguments:
#     object_name: String to use for the Logger Object Variable Name
#     logger_name: String to use for the Logger's Name
#     logger_level: Number of the log level to use for the Logger Object
# Returns:
#     None
Logger(){
    declare -l DIR
    DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    # Keep first option as variable name, rest are passed to class
    declare -l obj_name="${1}"
    shift 1

    # Source the class definition, replacing all references of obj with the
    # variable name so you get var::funct as a result
    # shellcheck source=./mxorc_logger_class.sh
    . <(sed "s/logger/${obj_name}/g" "${DIR}/mxorc_logger_class.sh")
}
