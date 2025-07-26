#!/bin/bash
sudo dd if=/dev/sda bs=4M status=progress | gzip > time-server-pi.img.gz

