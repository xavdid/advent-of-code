_default:
  just --list

# error out if this isn't being run in a venv
_require-venv:
    #!/usr/bin/env python
    import sys
    sys.exit(sys.prefix == sys.base_prefix)

# run linting and typecheking over the solutions
@lint: _require-venv
	ruff solutions/2022
	pyright solutions/2022

# run every solution for a given year
@validate year:
	for i in $(seq 1 25); do ./advent $i --slow --year {{year}}; done;
