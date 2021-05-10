#!/bin/bash
# This is a little helper script to build a docker image with the ngrams inside the container
# to keep things nice and tidy
docker build ./languagetoolsngrams.Dockerfile -t ghcr.io/lawrencegripper/languagetoolswithngrams:latest