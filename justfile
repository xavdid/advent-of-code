_default:
  just --list

# error out if this isn't being run in a venv
_require-venv:
    #!/usr/bin/env python
    import sys
    sys.exit(sys.prefix == sys.base_prefix)

@install: _require-venv
  pip install ruff pyright

# run linting and typecheking over the solutions
@lint: _require-venv
  # everything lints
  ruff .
  # but I didn't want to go back and typecheck anything pre-2022
  # all of 2022 was verified against latest pyright in sept 2023
  pyright solutions/2023

# run every solution for a given year
@validate year:
	for i in $(seq 1 25); do ./advent $i --slow --year {{year}}; done;
