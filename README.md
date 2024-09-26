![GitHub Repo stars](https://img.shields.io/github/stars/hamolicious/LogSift?style=flat-square&label=Github%20Stars)
[![PyPI - Version](https://img.shields.io/pypi/v/logsift?style=flat-square)](https://pypi.org/project/logsift/)


# LogSift
Quickly filter your logs from any command.

## Usage
The below assumes you have added an alias (DOSKEY for windows) for LogSift, otherwise, replace references to `logsift` with `python -m logsift`.

```bash
logsift npm run somecommand
logsift tail -f /var/log/syslog
```

## Documentation
The documentation is available over in docs.md (/src/logsift/docs/docs.md) or within LogSift itself, simply run `logsift` and then hit `shift+h` to read the docs.

## Installation
```bash
pip install logsift
```

## Known Bugs
I am still looking into these bugs and hoping to get them fixed asap.
* `npm run` can sometimes hang on second run. Running something like `killall node` after exiting LogSift works as a temporary workaround.

## Cross compatibility
### MacOS
* Uses the built in `pbcopy` command

### Linux
* Assumes that you have `xclip` installed and configured to implement copy behaviour. (maybe replace with a library?)

### Windows
* Copy behaviour not currently implemented.
