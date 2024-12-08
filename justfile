_default:
  just --list

# error out if this isn't being run in a venv
_require-venv:
    #!/usr/bin/env python
    import sys
    sys.exit(sys.prefix == sys.base_prefix)

# install dev deps
@install: _require-venv
  # extra flags make this ~ as fast as I want
  pip install -r requirements.txt --quiet --disable-pip-version-check

# run linting and typecheking over the solutions
@lint: _require-venv install
  ruff check --quiet
  ruff format --check --quiet
  pyright

# run every solution for a given year
@validate year:
	for i in $(seq 1 25); do ./advent $i --slow --year {{year}}; echo; done;

# run the dev server for the blog
@dev:
  just --justfile blog/justfile dev

# manualy update this
YEAR := "2024"

# add all and commit with message "{{year}} day {{day}}"
@commit day year=YEAR:
  gg "{{year}} day {{day}}"

# open all the relevant files for a given day. Hardcodes the current year.
@open day:
  code -r solutions/{{YEAR}}/day_$(printf %02d {{day}})/solution.py solutions/{{YEAR}}/day_$(printf %02d {{day}})/input.t*  blog/src/content/writeups/{{YEAR}}/{{day}}/index.md
