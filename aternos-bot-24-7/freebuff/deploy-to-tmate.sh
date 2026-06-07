#!/bin/bash
# Deploy freebuff-v2 to tmate session
# Run inside your tmate SSH session

mkdir -p ~/workspace
cd ~/workspace
curl -L -o freebuff-v2.tar https://tmpfiles.org/w7wiKBTSynip/freebuff-v2.tar
tar xf freebuff-v2.tar
ls -la ~/workspace/