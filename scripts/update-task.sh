#!/usr/bin/env bash
set -euo pipefail

# Constants
INSTALL_SCRIPT="https://taskfile.dev/install.sh"
LOCAL_BIN_DIR="${HOME}/.local/bin"
HOME_BIN_DIR="${HOME}/bin"
TASK_BINARY="${LOCAL_BIN_DIR}/task"

err() {
  echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $*" >&2
}

log() {
  echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $*"
}

# Ensure required directories exist
for dir in "${LOCAL_BIN_DIR}" "${HOME_BIN_DIR}"; do
    mkdir -p "${dir}"
done

# Check for curl
if ! command -v curl >/dev/null 2>&1; then
    err "curl not found. Please install curl and rerun."
    exit 1
fi

# Download and run Task install script
log "Downloading Task install script..."
if ! curl -sL "${INSTALL_SCRIPT}" | sh; then
    err "Failed to download and install Task"
    exit 1
fi

# Check if ./bin/task exists
if [[ ! -f "./bin/task" ]]; then
  err "Task binary not found in ./bin/task after install."
  err "Please ensure the install script placed the binary correctly."
  exit 1
fi

# Setup binary
if [[ -f "${TASK_BINARY}" ]]; then
    rm -f "${TASK_BINARY}"
fi

if [[ -L "${HOME_BIN_DIR}/task" ]]; then
    rm -f "${HOME_BIN_DIR}/task"
fi

cp "./bin/task" "${TASK_BINARY}"

ln -sf "${TASK_BINARY}" "${HOME_BIN_DIR}/task"

# Verify installation
if ! command -v task &> /dev/null; then
    err "Task binary not found in PATH."
    err "Add ${HOME_BIN_DIR} or ${LOCAL_BIN_DIR} to your PATH."
    exit 1
fi

version="$(task --version 2>/dev/null || echo 'unknown')"
log "Task binary (${version}) successfully installed/updated."
