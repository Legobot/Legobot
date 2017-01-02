# Change Log

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## Unreleased

### Fixed

- Apply pep8 style fixes
- Apply minor security fixes

## [1.0.2] 2016-12-12

### Added

- Allow IRC connector to authenticate to Freenode-style nickserv

## [1.0.1] 2016-12-08

### Added

- IRC lego can now respond to /query messages
- Metadata extended to provide more useful fields

### Fixed

- IRC lego no longer explodes with the fire of a thousand suns when
  sent utf-8 chars

## [1.0.0] 2016-11-04

### Complete refactor. See project docs for details on usage

- Legos are now classes that can be dropped in as plugins
- Using jaraco-irc for the IRC library
- Python3 only
- Dropped NickServ feature due to overhaul

## [0.2.0] 2016-08-02

### Added

- Legobot can now register with NickServ

## [0.1.2] 2016-08-01

### Added

- Legobot.throttle() method by pry0cc
- Travis-CI deployment to PyPI on tagged commits to master

## [0.1.1] 2016-01-16

- Initial release to PyPi
