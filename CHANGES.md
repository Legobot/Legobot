# Change Log

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [1.3.4] 2021-05-14

### Changed

- Allow setting log level in Chatbot class.

## [1.3.3] 2020-10-19

### Added

- Added a Chatbot class that automatically builds and runs a bot based on a config file.

### Changed

- Updated code to match style guide.
- Updated Travis config to test 3.6, 3.7, 3.8 and deploy 3.8

## [1.3.2] 2020-08-07

### Added

- Add rate limit capability per lego with rate_config kwarg

## [1.3.1] 2020-05-16

### Added

- Add ACL capability per lego with acl kwarg -- source_user whitelist/blacklist

## [1.3.0] 2020-02-26

### Added

- Add channel_display_name (friendly name) to message metadata.
- Add dicts of channels by id and channels by name to Slack connector class as properties.
- Add helper utilities in slack connector getting channel info
- Add dicts of users by id, users by name, users by display name to Slack connector class as properties.

### Changed

- Slack connector get_channels fetches all org channels and stores them on invocation, no more "condensed" keyword.
- Slack connector get_users fetches all org users and stores them on invocation, no more "condensed" keyword.
- Get user display name in Slack lego using get_user_by_id method.
- Remove get_username method.

## [1.2.6] 2020-01-13

### Added

- Add timestamp and sub type to message metadata in Slack connector.

### Changed
- Safer and more reliable Slack user name handling
- Help changes
  - Only list Legos with names.
  - Allow referencing Lego names in Help without regard to case.

## [1.2.5] 2019-04-03

### Added

- reply_attachment method
  - Sends attachment data to the connector. Connectors must be updated to handle this. If reply_attachment is called and the connector isn't built to handle it, it will just pass through to reply method.
  - build_attachment method in Slack connector

### Changed

- Slack will now reply to threads instead of in the main channel, when a lego is invoked from a thread.
- Updated requirements
- Moved to cfg driven setup

### Fixed

- Slack connector now caches the user list to reduce calls to the Slack API. Repeated calls were causing rate limiting, resulting in exceptions.

## [1.2.4] 2018-12-12

### Added

- get opts convenience method
- Expanded get_help to allow help for sub commands / sub topics

### Updated

- Contributing section of docs

## [1.2.3] 2018-05-23

### Added

- Includes the `source_connector` in the metadata for Slack and Discord. IRC was already doing this.

### Fixed

- Fixed bug #194 which surfaced after adding `username` and `display_name` to the metadata. Slack messages with no `source_user` will now be ignored for this functionality.
- Bot users were not having userids/display names properly resolved in Slack. Added function to fix this.

## [1.2.2] 2018-04-06

### Added

- Rejoins IRC channels on kick (#190)
  - Toggled by passing the `rejoin_on_kick` arg as a bool to the IRC connector
- Automatically attempts to reconnect to IRC after losing connection to server (#191)
  - Toggled by passing the `auto_reconnect` arg as a bool to the IRC connector
- Implement Slack client's autoconnect and reconnect settings (#192)
  - Toggled by passing the `auto_reconnect` arg as a bool to the Slack connector

## [1.2.1] 2018-04-03

### Fixed

- Resolved issue where Legobot could not join registered channels at start time

### Added

- Added `metadata['user_id']` and `metadata['display_name']` to each connector to handle protocols where user IDs and display names differ (talking about you, Slack and Discord!)

## [1.2.0] 2018-01-02

Happy New Year, Legobot users!

### Added

- Discord connector is live!

### Unfixed

- I had to remove a lot of tests from travis :(

## [1.1.4] 2017-08-25

### Fixed

- Fixed Slack connector DMs. Slack api im.list didn't list all users. Switched to im.open. (#159)

## [1.1.3] 2017-08-21

### Fixed

- Fixed misleading error about NickServ when connecting to IRC (#154) (@Nitr4x)
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
