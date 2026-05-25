# Changelog

## [1.4.9] - 2026-05-25

### Changed

- Bumped sqlalchemy to v2.0.50

## [1.4.8] - 2026-05-23

### Changed

- Bumped click to v8.4.1

## [1.4.7] - 2026-05-18

### Changed

- Bumped click to v8.4.0

## [1.4.6] - 2026-05-15

### Changed

- Bumped requests to v2.34.2

## [1.4.5] - 2026-05-14

### Changed

- Bumped requests to v2.34.1

## [1.4.4] - 2026-05-12

### Changed

- Bumped requests to v2.34.0

## [1.4.3] - 2026-05-10

### Added
- GitLab Release is now published automatically on each new tag, with release notes pulled from the matching CHANGELOG section
- Renovate MRs now bump CHANGELOG.md alongside VERSION via the shared bump-version template's BUMP_CHANGELOG option

### Changed
- Source tarballs attached to GitLab Releases now contain only the runnable packages plus install metadata (`LICENSE.rst`, `pyproject.toml`, `VERSION`); tests, CI configs, Dockerfile, and top-level docs are excluded via `.gitattributes`

## [1.4.2] - 2026-03-28

### Changed
- Update to TOML build method
- Add Docker build support
- Upgrade test coverage
- Update dependabot actions configuration
- Bug fixes and tox settings updates

## [1.4.1] - 2024-11-27

### Changed
- Modernity updates
- Add auto approval for test packages
- Dependency updates (sqlalchemy, click, pytz, prettytable, pylint, xmltodict, tox, jsonschema)

## [1.4.0] - 2021-12-20

### Changed
- Simplify clients, move over to pytest
- Fix email handling
- Dependency updates (sqlalchemy, click, beautifulsoup4, prettytable, jsonschema)

## [1.3.0] - 2020-02-24

### Changed
- Modernity updates

## [1.2.2] - 2020-01-04

## [1.2.0] - 2019-05-10
