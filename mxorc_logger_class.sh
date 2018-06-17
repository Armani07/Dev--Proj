#!/bin/bash
#
# Class Definiition for mxorc_logger.sh

#default properties
_logger_properties=("root" "0")

# Constructor Options
if [[ "${1}" ]]; then
    _logger_properties["${LOGGER_NAME}"]="${1}"
fi
if [[ "${2}" ]]; then
    _logger_properties["${LOGGER_LEVEL}"]="${2}"
fi


# Generic Object Property Getter/Setter
# Globals:
#     None
# Arguments:
#     property: index of the property in the properties array
#     =: If second argument is an `=` assignment is assumed
#     value: value to set the property to if second argument is an equal sign
# Returns:
#     Property's current value if not performing assignment
logger::property() {
    if [ "${2}" == "=" ]
    then
        _logger_properties["${1}"]="${3}"
    else
        echo "${_logger_properties[${1}]}"
    fi
}

# Logger Name Getter/Setter
# Globals:
#     LOGGER_NAME: Property Index
# Arguments:
#     =: If first argument is an `=` assignment is assumed
#     value: string to set the name to if first argument is an equal sign
# Returns:
#     Logger's current name if not performing assignment
logger::name() {
    if [ "${1}" == "=" ]
    then
        _logger_properties["${LOGGER_NAME}"]="${2}"
    else
        echo "${_logger_properties[${LOGGER_NAME}]}"
    fi
}

# Logger Level Getter/Setter
# Globals:
#     LOGGER_LEVEL: Property Index
# Arguments:
#     =: If first argument is an `=` assignment is assumed
#     value: number to set the level to if first argument is an equal sign
# Returns:
#     Logger's current level if not performing assignment
logger::level() {
    if [ "${1}" == "=" ]
    then
        _logger_properties["${LOGGER_LEVEL}"]="${2}"
    else
        echo "${_logger_properties[${LOGGER_LEVEL}]}"
    fi
}

# Log Printer for Debug statements.
# Globals:
#     LOGGER_LEVEL: Property index
#     LOGGER_DEBUG: Log Level for Debug statements
# Arguments:
#     message: The log message to print out
# Returns:
#     Log on stdout if LOGGER_LEVEL property is below LOGGER_DEBUG, else None
logger::debug() {
    if [[ "${_logger_properties[${LOGGER_LEVEL}]}" -le "${LOGGER_DEBUG}" ]]; then
        logger::print "DEBUG" "${1}"
    fi
}

# Log Printer for Info statements.
# Globals:
#     LOGGER_LEVEL: Property index
#     LOGGER_INFO: Log Level for Info statements
# Arguments:
#     message: The log message to print out
# Returns:
#     Log on stdout if LOGGER_LEVEL property is below LOGGER_INFO, else None
logger::info() {
    if [[ "${_logger_properties[${LOGGER_LEVEL}]}" -le "${LOGGER_INFO}" ]]; then
        logger::print "INFO" "${1}"
    fi
}

# Log Printer for Warn statements.
# Globals:
#     LOGGER_LEVEL: Property index
#     LOGGER_WARN: Log Level for Warn statements
# Arguments:
#     message: The log message to print out
# Returns:
#     Log on stdout if LOGGER_LEVEL property is below LOGGER_WARN, else None
logger::warn() {
    if [[ "${_logger_properties[${LOGGER_LEVEL}]}" -le "${LOGGER_WARN}" ]]; then
        logger::print "WARNING" "${1}"
    fi
}

# Log Printer for Error statements.
# Globals:
#     LOGGER_LEVEL: Property index
#     LOGGER_ERROR: Log Level for Error statements
# Arguments:
#     message: The log message to print out
# Returns:
#     Log on stdout if LOGGER_LEVEL property is below LOGGER_ERROR, else None
logger::error() {
    if [[ "${_logger_properties[${LOGGER_LEVEL}]}" -le "${LOGGER_ERROR}" ]]; then
        logger::print "ERROR" "${1}"
    fi
}

# Log Printer for Critical statements.
# Globals:
#     LOGGER_LEVEL: Property index
#     LOGGER_CRITICAL: Log Level for Critical statements
# Arguments:
#     message: The log message to print out
# Returns:
#     Log on stdout if LOGGER_LEVEL property is below LOGGER_CRITICAL, else None
logger::critical() {
    if [[ "${_logger_properties[${LOGGER_LEVEL}]}" -le "${LOGGER_CRITICAL}" ]]; then
        logger::print "CRITICAL" "${1}"
    fi
}

# General Log Printer
# Globals:
#     LOGGER_LEVEL: Property index
#     LOGGER_ERROR: Log Level for Error statements
# Arguments:
#     level: numeric log level
#     message: The log message to print out
# Returns:
#     if level above LOGGER_LEVEL print log
logger::log() {
    if [[ "${_logger_properties[${LOGGER_LEVEL}]}" -le "${1}" ]]; then
        logger::print "${1}" "${2}"
    fi
}

# Log Output Formatter
# Globals:
#     LOGGER_NAME: Property index
# Arguments:
#     level: The level of the log (does not validate this)
#     message: The message of the log
# Returns:
#     Log on stdout
logger::print() {
    echo "$(date +"%Y-%m-%d %H:%M:%S") - ${_logger_properties[${LOGGER_NAME}]} - ${1} : ${2}"
}
