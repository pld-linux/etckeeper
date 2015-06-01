#!/bin/sh
etckeeper=/usr/bin/etckeeper

# etckeeper might had been removed meanwhile
if [ -x $etckeeper ]; then
	$etckeeper post-install
fi
