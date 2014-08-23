circle-github-status-bridge
===========================

This thing can pull build statuses from Circle CI and push them onto GitHub. Cool, right?

This script is meant to be run periodically by something like cron, launchd, or jenkins.

## Usage

Do this once:

```bash
export STATUS_BRIDGE_CIRCLECI_API_TOKEN=1234567890123456789012345678901234567890
export STATUS_BRIDGE_GITHUB_API_TOKEN=1234567890123456789012345678901234567890
# set the earliest build that should be checked
python . set_check_head IFTTT/ifttt_front_end 12345
```

And run this periodically:

```bash
export STATUS_BRIDGE_CIRCLECI_API_TOKEN=1234567890123456789012345678901234567890
export STATUS_BRIDGE_GITHUB_API_TOKEN=1234567890123456789012345678901234567890
python . push_all_statuses_after_check_head IFTTT/ifttt_front_end
```

To make these commands one-liners, use `env`.

## About the directory format of this project

If the Python interpreter is told to "run" a directory or zip file, it will run the enclosed `__main__.py` file. Therefore this project can be run in a few ways:

- `/path/to/circle-github-status-bridge $ python . ...`
- `/path/to $ python circle-github-status-bridge ...`
- `/path/to $ python circle-github-status-bridge.zip ...`

The last variation allows the entire project to be distributed as a zip file.

## About the output format of the script

- Progress and errors should be sent to `stderr` (`print >> stderr, 'message'`)
- Return value-like output should be sent to `stdout`  (`print 'message'`)
