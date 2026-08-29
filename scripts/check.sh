#!/usr/bin/env bash
set -euo pipefail

ansible-lint
python -m unittest discover -s tests/unit/filter_plugins -p 'test_*.py'
ansible-playbook -i localhost, tests/integration/compose_bind_directories.yml
