#!/bin/bash
set -e
export CARGO_HOME=/tmp/cargo
export PYDANTIC_CORE_INSTALL=python-only
pip install --upgrade pip setuptools wheel
pip install --only-binary :all: pydantic-core
pip install -r backend/requirements.txt