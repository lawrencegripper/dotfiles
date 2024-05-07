#!/bin/bash

# TODO: Make this templated and find the service files in the directory

systemctl --user daemon-reload
systemctl --user enable albert.service
systemctl --user restart albert.service

systemctl --user enable copyq.service
systemctl --user restart copyq.service