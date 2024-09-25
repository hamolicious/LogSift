# LogSift
Quickly filter your logs from any command.

## Usage
The below assumes you have added an alias (DOSKEY for windows) for LogSift, otherwise, replace references to `logsift` with `python -m logsift`.

```bash
logsift npm run somecommand
logsift cat /var/log/syslog
```

## Documentation
The documentation is available over in [/src/docs/docs.md](docs.md) or within LogSift itself, simply run `logsift` and then hit `shift+h` to read the docs.

## Installation
```bash
pip install logsift
```

## Cross compatibility
### Linux
* Assumes that you have `xclip` installed and configured to implement copy behaviour. (maybe replace with a library?)

### Windows
* Copy behaviour not currently implemented.
