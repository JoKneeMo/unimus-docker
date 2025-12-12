#!/usr/bin/env bash
# Container entrypoint script for Unimus Core
set -e

##### Variables #####
unimus_properties="/etc/unimus-core/unimus-core.properties"


##### Functions #####
function make_properties() {
    echo -n "Making unimus-core.properties file..."
    echo -e "# Unimus Core config file\n" > "${unimus_properties}"

    for prop in $(env | grep '^PROP_' | cut -d= -f1); do
        prop_key="${prop#PROP_}"
        prop_key="${prop_key,,}"
        prop_key="${prop_key//_/.}"
        prop_value="$(env | grep "^${prop}=" | cut -d= -f2)"
        echo "${prop_key} = ${prop_value}" >> "${unimus_properties}"
    done

    echo "done"
}

function start_unimus() {
    echo "Starting Unimus Core..."
    JAVA_PARAMS=""
    [ ! -z "${JAVA_XMS}" ] && { JAVA_PARAMS="${JAVA_PARAMS} -Xms${JAVA_XMS}"; }
    [ ! -z "${JAVA_XMX}" ] && { JAVA_PARAMS="${JAVA_PARAMS} -Xmx${JAVA_XMX}"; }
    [ ! -z "${JAVA_OPTS}" ] && { JAVA_PARAMS="${JAVA_PARAMS} ${JAVA_OPTS}"; }

    java ${JAVA_PARAMS} $@ -jar /opt/unimus-core/Unimus-Core.jar
}


##### Execution #####
if [ "$MAKE_PROPERTIES" = true ]; then
    make_properties
fi

echo "${TZ}" > /etc/timezone

if [[ $# -gt 0 ]] && [[ $@ == -* ]]; then
    echo "Starting Unimus Core with arguments: $@"
    start_unimus $@
elif [[ $# -eq 0 ]]; then
    echo "Starting Unimus Core"
    start_unimus
else
    echo "Executing command: $@"
    exec "$@"
fi