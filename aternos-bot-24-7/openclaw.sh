#!/bin/bash
export PATH="/nix/store/s97a21afj6aw098a25gs3j7ias7wzanm-nodejs-22.22.0-wrapped/bin:$PATH"
export NODE_COMPILE_CACHE=/tmp/openclaw-node-cache
export OPENCLAW_NO_RESPAWN=1
exec /nix/store/s97a21afj6aw098a25gs3j7ias7wzanm-nodejs-22.22.0-wrapped/bin/node /home/runner/workspace/.config/npm/node_global/lib/node_modules/openclaw/dist/index.js "$@"
