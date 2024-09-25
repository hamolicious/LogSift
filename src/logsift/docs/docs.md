# LogSift
Quickly filter your logs from any command.

## Features
- Capture logs from commands in real-time.
- Filter and search through logs.

---

## Filtering
LogSift offers a straightforward filtering mechanism to refine logs as needed.

### Syntax
The filter input is dead simple... it accepts terms, space-separated strings. You can combine multiple terms to refine your search. Use `""` to match terms with spaces, `!` to exclude terms. That's it.

#### Examples:
- `"term1 term2"` : Matches logs containing both `term1` and `term2`, separated by a space.
- `!term`, `"!term"`, `!"term"`: Any of those are valid, excludes logs containing `term`.

### Ingestion
The application continuously ingests logs. The ingestion process can be paused using (p), but so nothing gets lost, logs are still collected, just not processed yet. I am still on the fence about the max ingested log limit, I built it anticipating performance issues when huge log amounts are being processed but not sure it's necessary; needs testing.

- `MAX_INGESTED_LOGS = 100,000`: Maximum number of logs to keep in memory.
- `MAX_DISPLAY_LOGS = 500`: Maximum number of logs shown in the display (May cause flickering if set too high).
- `MAX_BUFFERED_LOGS = 500`: Maximum number of logs buffered awaiting ingestion.

Upon reaching any of the above limits, storage switches to FILO for the system in question.

---

## Filter Settings
LogSift provides several settings to refine how the filter is applied:

#### 1. Toggle Active Filter
- Enables or disables filtering. When disabled, all logs are shown.

#### 2. Match All
- When on matches all terms (AND operation). When off matches any one of the terms (OR operation).
  - **Enabled**: Requires logs to match *all* terms.
  - **Disabled** (_default_): Requires logs to match *any* term.

#### 3. Case Insensitive
- Toggles case sensitivity. When enabled (_default_), the filter ignores the case of terms (e.g., "Error" will match "error").

## Display Settings

### Word Wrap
- Toggles word-wrapping logs, disabled by default.

### Auto scroll
- Toggle scrolling to the bottom on new log added, enabled by default

### Filtering Modes
LogSift offers two main filtering modes for logs:

#### 1. Omit Mode
- Excludes logs that don't match the filter terms. (_default_)

#### 2. Highlight Mode
- Highlights logs that match the filter terms. Non-matching logs remain visible.

---

## Keybinds
*Every* UI interaction has an associated key bind:

| Keybind          | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| `f`              | Focuses the filter input.                                                   |
| `p`              | Pause ingesting logs, when toggled off, buffer will be flushed              |
| `t`              | Toggles enforcing the filter.                                               |
| `m`              | Toggles between matching all terms or any term from the filter.             |
| `c`              | Toggles case sensitivity.                                                   |
| `o`              | Omits non-matching logs.                                                    |
| `l`              | Highlights matching logs.                                                   |
| `b`              | Toggles visibility of the settings panel.                                   |
| `w`              | Toggle word-wrapping logs.                                                  |
| `a`              | Toggle scrolling to the bottom on new log added.                            |
| `shift+h`        | Toggles the documentation panel visibility.                                 |
| `k` / `up`       | Scrolls the logger up.                                                      |
| `shift+k`        | Scrolls the logger up 10 lines.                                             |
| `j` / `down`     | Scrolls the logger down.                                                    |
| `shift+j`        | Scrolls the logger down 10 lines.                                           |
| `shift+c`        | Copies the displayed logs to the clipboard.                                 |

## Glossary
### log collection
Collecting logs refers to reading piped log-lines and storing the raw log

### log ingesting
Ingesting logs refers to processing the log into memory

### buffer
Refers to the internal, temporary buffer for storing logs while ingestion is paused.
