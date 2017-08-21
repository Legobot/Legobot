# Change Log

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [UNRELEASED] 0000-00-00

## [1.1.3] 2017-08-21
#### Fixed

- Fixed misleading error about NickServ when connecting to IRC
- Limited IRC messages to 256 chars. Long messages will be split and sent in chunks.
- IRC connector now handles newlines returned from Legos (#129, #140, #142) (@bbriggs)
  - With improvements from @pry0cc
- Fixed a nasty bug where a response directed at one user or channel would be sent to a channel or user of the same name on another connector. (#141, #143) (@bbriggs)
- Messages sent to a user-id in Slack now properly route to the DM channel (#163).

### Added

- New Utilities class to provide convenience methods for legos
- Slack connector now has methods to resolve a user-id to a username and a user-id to a DM channel id

## [1.1.2] 2017-02-08
### Fixed

- Legobot will now respond with its actual name instead of `bot` in Slack

## [1.1.1] 2017-01-17
### Fixed

- Missing package dep `slackclient` added

## [1.1.0] 2017-01-16
### Added

- New Slack connector/backend
- Use bandit and quantified code test for known bugs

### Fixed

- Style and security fixes recommended by bandit, QuantifiedCode,
and flake8

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
