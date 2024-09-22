# Supalogger
A simple, easy-to-use log manager.

## Features
- Capture logs from commands in real-time.
- Filter and search through logs efficiently.

---

## Filtering
Supalogger offers a straightforward filtering mechanism to refine logs as needed.

### Syntax
The filter input accepts terms, which are space-separated strings. You can combine multiple terms to refine your search.

#### Examples:
- `term1 term2`: Matches logs containing both `term1` and `term2`.
- `!term`: Excludes logs containing `term`.

### Ingestion
The application continuously ingests logs from the provided command using `LogManager`. The ingestion process can be paused but so nothing gets lost, logs are still collected just not processed yet. Logs that don't match the filter can be excluded from the display.

- `MAX_INGESTED_LOGS = 100,000`: Maximum number of logs to keep in memory.
- `MAX_DISPLAY_LOGS = 500`: Maximum number of logs shown in the display.
- `MAX_BUFFERED_LOGS = 500`: Maximum number of logs buffered awaiting ingestion.
- You can pause the log ingestion through a toggle button or using (p)

Upon reaching any of the above limits, storage switches to FILO for the system in question.

---

## Filter Settings
Supalogger provides several settings to refine how the filter is applied:

#### 1. Toggle Active Filter
- Enables or disables filtering. When disabled, all logs are shown.

#### 2. Toggle Match All / OR Operations
- Choose between matching all terms (AND operation) or matching any one of the terms (OR operation).
  - **Enabled**: Requires logs to match *all* terms.
  - **Disabled**: Requires logs to match *any* term.

#### 3. Case Insensitivity
- Toggles case sensitivity. When enabled, the filter ignores the case of terms (e.g., "Error" will match "error").

## Display Settings

### Word Wrap
- Toggles word-wrapping logs

### Auto scroll
- Toggle scrolling to the bottom on new log added

---

### Filtering Modes
Supalogger offers two main filtering modes for logs:

#### 1. Omit Mode
- Excludes logs that don't match the filter terms.

#### 2. Highlight Mode
- Highlights logs that match the filter terms. Non-matching logs remain visible.

---

## Keybinds
*Every* UI interaction has an associated key bind:

| Keybind          | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| `f`              | Focuses the filter input.                                                   |
| `p`              | Pause ingesting logs, when toggled off, buffer will be flushed                                                 |
| `t`              | Toggles enforcing the filter.                                               |
| `m`              | Toggles between matching all terms or any term from the filter.             |
| `c`              | Toggles case sensitivity.                                                   |
| `o`              | Omits non-matching logs.                                                    |
| `l`              | Highlights matching logs.                                                   |
| `b`              | Toggles visibility of the settings panel.                                   |
| `w`              | Toggle word-wrapping logs.                                                   |
| `a`              | Toggle scrolling to the bottom on new log added.                                                   |
| `shift+h`        | Toggles the documentation panel visibility.                                 |
| `k` / `up`       | Scrolls the logger up.                                                      |
| `shift+k`        | Scrolls the logger up 10 lines.                                             |
| `j` / `down`     | Scrolls the logger down.                                                    |
| `shift+j`        | Scrolls the logger down 10 lines.                                           |
| `shift+c`        | Copies the filtered logs to the clipboard.                                  |

## Glossary
### log collection
Collecting logs refers to reading piped log-lines and storing the raw log

### log ingesting
Ingesting logs refers to processing the log into memory

### buffer
Refers to the internal, temporary buffer for storing logs while ingestion is paused.
