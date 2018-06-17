#!/usr/bin/env bash
# Determine the status of a service inputted as an arg

# Usage function
# Globals:
#   None
# Arguments:
#   None
# Returns:
#   None
usage(){
    echo -e "${0} [-h] <service_name>"
    echo -e "    -h               Displays this Usage Statement and Exits."
    echo -e "    SERVICE_NAME     The service name to check for status."
    echo -e "                     Example : WorkOrderExport"
}

OPTIND=1 # Reset in case getopts has been used previously in the shell.
while getopts ":h" opt; do
    case $opt in
        h)
            usage
            exit 0
            ;;
        \?)
            echo -e "Invalid option: -$OPTARG"
            usage
            exit 1
            ;;
    esac
done
shift $((OPTIND-1))

# Determine the status of a specified serivce, prints the running service
# Globals:
#   None
# Arguments:
#   service_name
# Returns:
#   None
determine_status(){
    service_name="${1}"
    # Regex that returns all services currently running, then is checked
    # for the specified service
    # shellcheck disable=SC2009
    service_status="$(ps -ef \
      | grep -Po "(?<=tomcat.name\\=)(${service_name})(_[0-9]+\\.[0-9]+\\.[0-9]+)?-[A-Z]")"
    status_msg="Number of running instances of ${service_name}:"
    
    # print the running service(s)
    if [[ "$(echo -e "${service_status}" | wc -w)" -eq 0 ]]; then
        echo -e "${status_msg} 0."
        exit 0
    else
        echo -e "${status_msg} $(echo "${service_status}" | wc -w)\\n${service_status}"
        exit 0
    fi
}

if [[ "${#}" -eq 0 ]]; then
    echo -e "No service name supplied."
    usage
    exit 1
else
    determine_status "${1}"
fi
