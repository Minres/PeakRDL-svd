#!/bin/bash

set -e

cd "$(dirname "$0")"

# Initialize venv
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate

# Install test dependencies
pip install -r requirements.txt

# Install dut
pip install -e "../[cli]"

# Run unit tests while collecting coverage
pytest --cov=peakrdl_svd

# Generate coverage report
coverage html -d htmlcov

# Run lint
pylint --rcfile pylint.rc ../src/peakrdl_svd | tee lint.rpt

# Run static type checking
mypy ../src/peakrdl_svd

rm -f tmp*.xml
