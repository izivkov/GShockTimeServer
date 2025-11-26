#!/bin/bash

# This script runs all setup scripts in order.

. ./setup.sh
. ./setup-display.sh
. ./setup-boot.sh
. ./gshock-updater.sh
. ./enable-spi.sh
