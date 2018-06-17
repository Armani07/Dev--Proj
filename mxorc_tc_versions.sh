#!/usr/bin/env bash
# View all local instanaces of a tomcat services

# Usage Statement
# Globals:
#     None
# Arguments:
#     None
# Returns:
#     None
usage() {
    echo -e "${0} [-h] <service>"
    echo -e "    -h               Displays this Usage Statement and Exits."
    echo -e "    SERVICE          The name of the service of which all"
    echo -e "                     instances will be displayed."
    echo -e "                     eg. SWAMPBoard WorkOrderExport"
}

OPTIND=1 # Reset in case getopts has been used previously in the shell.
while getopts ":h" opt; do
    case $opt in
        h)
            usage
            exit 0
            ;;
        \?)
            echo -e "Invalid option: -$OPTARG" >&2
            usage >&2
            exit 1
            ;;
    esac
done
shift $((OPTIND-1))

# Prints listing of given service, but first checks if you're on a tcServer
# Globals:
#     None
# Arguments:
#     service
# Returns:
#     None
find_all_instances(){
    declare -r service="${1}"
    declare -r tomcat_dir="/opt/tomcat/servers/"

    if [[ -d "${tomcat_dir}" ]]; then
        # shellcheck disable=SC2155
        declare -r listing="$(find "${tomcat_dir}" -maxdepth 1 -regextype posix-extended -regex ".*/(${service})(_[0-9]+\\.[0-9]+\\.[0-9]+)?-[A-Z]$" -exec basename {} \;)"
        if [[ -n "${listing}" ]]; then
            echo -e "${listing}"
            exit 0
        else
            echo -e "There are no instances of ${service}." >&2
            exit 2
        fi
    else
        echo -e "The tomcat directory (${tomcat_dir}) does not exist." >&2
        echo -e "Are you sure this is a tcServer?" >&2
        exit 3
    fi
}


if [[ "${#}" -eq 0 ]]; then
    echo -e "No service name supplied."
    usage
    exit 1
else
    find_all_instances "${1}"
fi
