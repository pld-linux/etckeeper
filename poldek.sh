#!/bin/sh
etckeeper=/usr/bin/etckeeper

$etckeeper pre-install

/bin/rpm "$@"
rc=$?

# etckeeper might had been removed meanwhile
if [ -x $etckeeper ]; then
	$etckeeper post-install
fi

exit $rc
