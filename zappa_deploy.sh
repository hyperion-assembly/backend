#!/usr/bin/env bash
zappa update dev
zappa manage dev migrate
# zappa manage dev "collectstatic --noinput"
# zappa schedule dev # update scheduled/periodic functions
