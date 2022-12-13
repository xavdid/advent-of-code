# CHANGELOG

Though this repo doesn't have traditional "releases", I do periodically add features and make breaking changes to the way `advent`, and my `BaseSolution` work. I handle the updates to my existing solutions, but if you periodically copy my helpers back into your repo, it will be helpful to know how far behind your version of this repo is.

Below is a rough changelog of new features added, which largely follows [SemVer](https://semver.org/):

- Breaking changes will require you to update existing solutions to continue working
- Minor versions add new, backwards-compatible features you may want to start using
- Patch versions are internal functionality updates or changes to the template that won't affect compatibility with existing solutions

## 3.0.0

_released `2022-12-13`_

- BREAKING: requires python@3.11.x to take advantage of some new typing features (see below)
- fixed: really nail the typing around the `@answer` decorator, which will require its arguments to match the return type of the wrapped function
- fixed: remove some `typing` imports and replaced with their generic containers (which is preferred since Py 3.9); adjusted template accordingly.

## 2.2.0

_released `2022-12-12`_

- added: `max_x_size` and `max_y_size` to `base.neighbors`
- fixed: improved handling of non-tuple responses from `solve`

## 2.1.4

_released `2022-12-07`_

- fixed: further improved the typing around the `@answer` to support `tuple` responses from `solve`

## 2.1.3

_released `2022-12-06`_

- fixed: improved the typing around the `@answer` decorator to better support (rare) non-int answers

## 2.1.2

_released `2022-12-04`_

- fixed: simplified answer parsing code by _always_ calling `solution.solve()` and having it default to calling parts 1 & 2 itself.

## 2.1.1

_released `2022-12-01`_

- fixed: typing for the TSV input type
- fixed: simplify the input parsing internals

## 2.1.0

_released `2022-11-30`_

- added: the `--version` flag to `advent`
- added: the `--test-data` flag to `advent`; `start` now creates this by default
- fixed: the `start` command now treats November 30th as part of the current puzzle year

## 2.0.0

_released `2022-10-29`_

In the interest of not going too far back in time, this is the first version tracked in the changelog.

- BREAKING CHANGE: pad the folder names for days 1-9 with a leading 0 (e.g. `day_1/...` -> `day_01/...`. Run `python misc/pad_day_migration.py` from the repo root to update your local files. Only really tested on macOS, so proceed with a little caution.

## 1.x.x

All versions of this repo prior to `2022-10-28` are using what is henceforth known as the "1.0" version of this package. See [2.0](#200) for migration information.
