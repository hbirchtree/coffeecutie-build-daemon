#! /bin/sh
### BEGIN INIT INFO
# Provides:          buildserved
# Required-Start:    networking
# Required-Stop:     
# Should-Start:      glibc
# Default-Start:     S
# Default-Stop:
# Short-Description: Display webpage with build status
# Description:       Display webpage with build status, including a REST API
### END INIT INFO

SCRIPT_LOCATION=/home/pi/coffeecutie-build-daemon/build-server
PYENV_NAME=pyenv
PIDFILE=/var/run/host-discover.pid

do_start () {
	su pi -c "$SCRIPT_LOCATION/$PYENV_NAME/bin/python3 $SCRIPT_LOCATION/src/bserver.py &"
	echo $! > $PIDFILE
}

do_status () {
	if [ -f "$PIDFILE" ]; then
		return 0;
	else
		return 4;
	fi
}

do_stop () {
	if [ -f "$PIDFILE" ]; then
		kill "$(cat $PIDFILE)"
		return 0;
	fi
	return 4;
}

force_stop () {
	if [ -f "$PIDFILE" ]; then
		kill -9 "$(cat $PIDFILE)"
		return 0;
	fi
	return 4;
}

case "$1" in
  start|"")
	do_start
	;;
  restart|reload)
	do_stop
	do_start
	;;
  force-reload)
	force_stop
	do_start
	;;
  stop)
	do_stop
	;;
  status)
	do_status
	exit $?
	;;
  *)
	echo "Usage: hostname.sh [start|stop]" >&2
	exit 3
	;;
esac

:
