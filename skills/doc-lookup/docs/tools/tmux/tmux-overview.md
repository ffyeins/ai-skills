# Tmux Overview

> Conceptual overview, target specification, environment, and quick reference for tmux.

Verified against: tmux 3.7b (2026-09)

**Contents**

- Key Concepts
- Command Line Options
- Command Parsing
- Target Specification
- Environment Variables
- Files
- Quick Reference
- See Also

## Key Concepts

- **Session** -- a collection of pseudo terminals managed by tmux; survives disconnections
- **Window** -- occupies the entire screen; may be split into rectangular panes
- **Pane** -- a separate pseudo terminal inside a window
- **Client** -- displays a session on screen
- **Server** -- single process that manages all sessions

Hierarchy: server > session(s) > window(s) > pane(s). Clients attach to sessions.

## Command Line Options

| Flag | Description |
|------|-------------|
| `-2` | Force 256-colour support |
| `-C` | Start in control mode (`-CC` disables echo) |
| `-c` *cmd* | Execute shell command using default shell |
| `-D` | Do not daemonise the server |
| `-f` *file* | Alternative configuration file |
| `-L` *name* | Different socket name (allows multiple servers) |
| `-l` | Behave as login shell |
| `-N` | Do not start the server |
| `-S` *path* | Full alternative path to server socket |
| `-T` *features* | Set terminal features for the client |
| `-u` | Write UTF-8 output to terminal |
| `-V` | Print version |
| `-v` | Verbose logging |

## Command Parsing

- Commands terminated by newline or semicolon (`;`)
- Comments: unquoted `#`
- Line continuation: trailing `\`
- Strings: single-quoted (`'`), double-quoted (`"`), or braced (`{}`)
- Commands run from: shell, `bind-key`, `~/.tmux.conf`, or command prompt (`C-b :`)

### Conditionals in Config

```
%if "#{==:#{host},myhost}"
set -g status-style bg=red
%elif "#{==:#{host},myotherhost}"
set -g status-style bg=green
%else
set -g status-style bg=blue
%endif
```

## Target Specification

Most commands accept `-t` (and sometimes `-s`) to specify a target.

### Target Session

Resolved in order:

1. Session ID prefixed with `$`
2. Exact session name
3. Start of a session name
4. Glob pattern against session name

Prefix with `=` for exact match only.

### Target Window

Format: `session:window`

Resolved in order:

1. Special token (see table below)
2. Window index
3. Window ID (e.g., `@1`)
4. Exact window name
5. Start of window name
6. Glob pattern against window name

#### Window Special Tokens

| Token | Alias | Meaning |
|-------|-------|---------|
| `{start}` | `^` | Lowest-numbered window |
| `{end}` | `$` | Highest-numbered window |
| `{last}` | `!` | Previously current window |
| `{next}` | `+` | Next window by number |
| `{previous}` | `-` | Previous window by number |
| `{current}` | `@` | Current window |

### Target Pane

Format: `session:window.pane`

If pane index is omitted, the currently active pane is used.

#### Pane Special Tokens

| Token | Alias | Meaning |
|-------|-------|---------|
| `{last}` | `!` | Previously active pane |
| `{next}` | `+` | Next pane by number |
| `{previous}` | `-` | Previous pane by number |
| `{top}` | | Top pane |
| `{bottom}` | | Bottom pane |
| `{left}` | | Leftmost pane |
| `{right}` | | Rightmost pane |
| `{top-left}` | | Top-left pane |
| `{top-right}` | | Top-right pane |
| `{bottom-left}` | | Bottom-left pane |
| `{bottom-right}` | | Bottom-right pane |
| `{up-of}` | | Pane above active pane |
| `{down-of}` | | Pane below active pane |
| `{left-of}` | | Pane left of active pane |
| `{right-of}` | | Pane right of active pane |
| `{active}` | `@` | Active pane |

### Mouse and Marked Pane

- `{mouse}` or `=` -- target where the mouse event occurred
- `{marked}` or `~` -- the marked pane (set with `C-b m`)

## Environment Variables

| Variable | Description |
|----------|-------------|
| `TMUX` | Set by tmux with internal session information |
| `TMUX_PANE` | Pane ID passed to child processes |
| `TERM` | Set to `screen` or `tmux` |
| `SHELL` | Default shell |
| `EDITOR` / `VISUAL` | Affects default key bindings |
| `TMUX_TMPDIR` | Parent directory for server sockets |

## Files

| Path | Description |
|------|-------------|
| `~/.tmux.conf` | Default user configuration |
| `$XDG_CONFIG_HOME/tmux/tmux.conf` | XDG config location |
| `~/.config/tmux/tmux.conf` | Alternative config location |
| `/etc/tmux.conf` | System-wide configuration |

## Quick Reference

### Sessions

```
tmux                          Start new session
tmux new -s name              Start named session
tmux ls                       List sessions
tmux attach                   Attach to last session
tmux attach -t name           Attach to named session
tmux new -A -s name           Attach or create if missing
tmux kill-session -t name     Kill named session
C-b d                         Detach from session
C-b $                         Rename session
C-b (                         Previous session
C-b )                         Next session
C-b s                         Choose session interactively
C-b L                         Switch to last session
```

### Windows

```
C-b c                         Create window
C-b ,                         Rename window
C-b w                         List windows
C-b n                         Next window
C-b p                         Previous window
C-b 0-9                       Select window by number
C-b l                         Last (previous) window
C-b &                         Kill window
C-b '                         Prompt for window index
C-b .                         Move window to index
C-b f                         Search for text in windows
```

### Panes

```
C-b %                         Split left/right (split-window -h)
C-b "                         Split top/bottom (split-window -v)
C-b o                         Next pane
C-b ;                         Last (previous) pane
C-b q                         Show pane numbers
C-b x                         Kill pane
C-b z                         Toggle pane zoom
C-b !                         Break pane to new window
C-b {                         Swap with previous pane
C-b }                         Swap with next pane
C-b Space                     Cycle preset layouts
C-b arrows                    Navigate panes
C-b C-arrows                  Resize pane (1 cell)
C-b M-arrows                  Resize pane (5 cells)
C-b m                         Mark pane
C-b M                         Clear marked pane
```

### Copy Mode

```
C-b [                         Enter copy mode
C-b ]                         Paste buffer
C-b #                         List paste buffers
C-b =                         Choose buffer to paste
q                             Exit copy mode
Space                         Start selection (vi mode)
Enter                         Copy selection (vi mode)
/                             Search forward
?                             Search backward
n                             Next search result
```

## See Also

- `tmux-keybindings.md` -- key tables, custom bindings, mouse events, and copy-mode keys
- `tmux-scripting.md` -- commands, options, formats, styles, hooks, and scripting workflows
