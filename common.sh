# setup colors
if [ -t 1 ]; then
    COLOR_RED="\033[31m"
    COLOR_OFF="\033[0m"
fi

error() {
    local message="$1"
    local exitcode="${2:-2}" # default 2
    echo -e "${COLOR_RED}Error: ${message}${COLOR_OFF}"
    exit $exitcode
}
