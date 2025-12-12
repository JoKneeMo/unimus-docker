#!/usr/bin/env bash
# Container entrypoint script for Unimus Server
set -e

##### Variables #####
unimus_properties="/etc/unimus/unimus.properties"
unimus_defaults="/etc/default/unimus"


##### Functions #####
function make_properties() {
    echo -n "Making unimus.properties file..."
    echo -e "# Unimus config file\n" > "${unimus_properties}"

    for prop in $(env | grep '^PROP_' | cut -d= -f1); do
        prop_key="${prop#PROP_}"
        prop_key="${prop_key,,}"
        prop_key="${prop_key//_/.}"
        prop_value="$(env | grep "^${prop}=" | cut -d= -f2)"
        echo "${prop_key} = ${prop_value}" >> "${unimus_properties}"
    done

    echo "done"
}

function make_defaults() {
    echo -n "Making unimus defaults file..."
    echo -e "# Unimus default file\n" > "${unimus_defaults}"

    for prop in $(env | grep '^DEFAULT_' | cut -d= -f1); do
        prop_key="${prop#DEFAULT_}"
        prop_key="${prop_key,,}"
        prop_key="${prop_key//_/.}"
        prop_value="$(env | grep "^${prop}=" | cut -d= -f2)"
        echo "${prop_key} = ${prop_value}" >> "${unimus_defaults}"
    done

    echo "done"
}

function start_unimus() {
    echo "Starting Unimus..."
    JAVA_PARAMS=""
    [ ! -z "${JAVA_XMS}" ] && { JAVA_PARAMS="${JAVA_PARAMS} -Xms${JAVA_XMS}"; }
    [ ! -z "${JAVA_XMX}" ] && { JAVA_PARAMS="${JAVA_PARAMS} -Xmx${JAVA_XMX}"; }
    [ ! -z "${JAVA_OPTS}" ] && { JAVA_PARAMS="${JAVA_PARAMS} ${JAVA_OPTS}"; }

    UNIMUS_PARAMS=""
    while read -r param || [ -n "${param}" ]; do
        if [[ "${param}" == \#* ]] || [[ -z "${param}" ]]; then
            continue
        else 
            UNIMUS_PARAMS="${UNIMUS_PARAMS} -D${param}"
        fi
    done < "${unimus_defaults}"

    java ${JAVA_PARAMS} ${UNIMUS_PARAMS} $@ -jar /opt/unimus/Unimus.jar
}


##### Execution #####
if [ "$MAKE_PROPERTIES" = true ]; then
    make_properties
fi

if [ "$MAKE_DEFAULTS" = true ]; then
    make_defaults
fi

echo "${TZ}" > /etc/timezone

if [[ $# -gt 0 ]] && [[ $@ == -* ]]; then
    echo "Starting Unimus with arguments: $@"
    start_unimus $@
elif [[ $# -eq 0 ]]; then
    echo "Starting Unimus"
    start_unimus
else
    echo "Executing command: $@"
    exec "$@"
fi