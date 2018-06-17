#!/usr/bin/env bash
# Start a local Tomcat Instance via Web Service's swacat control scripts

# Usage Statement
# Globals:
#     None
# Arguments:
#     None
# Returns:
#     None
usage() {
    echo "${0} [-h] <instance>"
    echo "    -h               Displays this Usage Statement and Exits."
    echo "    INSTANCE         The Service Instance to attempt to start."
    echo "                     eg. SWAMPBoard-B WorkOrderExport_1.0.26-A"
}

OPTIND=1 # Reset in case getopts has been used previously in the shell.
while getopts ":h" opt; do
    case $opt in
        h)
            usage
            exit 0
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            usage >&2
            exit 1
            ;;
    esac
done
shift $((OPTIND-1))

# Start a tomcat service instance
# Globals:
#     None
# Arguments:
#     instance - the instance of the service
# Returns:
#     None
start_instance() {
    declare -r instance="${1}"
    declare -r instance_dir="/opt/tomcat/servers/${instance}"
    declare -r instance_control_script="${instance_dir}/bin/swa-control.sh"

    if [[ -d  "${instance_dir}" ]]; then
        if [[ -e "${instance_control_script}" ]]; then
            sudo -nu swacat "${instance_control_script}" start
            declare -r instance_start_exit_code="${?}"
            echo "${instance}"
            exit "${instance_start_exit_code}"
        else
            echo "swa-control.sh could not be found for instance, ${instance}."
            exit 3
        fi
    else
        echo "Instance Directory could not be found for instance, ${instance}"
        exit 2
    fi

}

if [[ $# -eq 0 ]]; then
    echo -e "No instance name supplied."
    usage
    exit 1
else
    start_instance "${1}"
fi
