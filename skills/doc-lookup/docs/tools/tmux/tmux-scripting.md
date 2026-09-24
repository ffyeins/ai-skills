# Tmux Scripting & Configuration

> Commands, options, formats, styles, hooks, and configuration for tmux automation and customization.

**Contents**

- Key Concepts
- Essential Commands
- Options
- Formats
- Styles
- Hooks
- Common Workflows
- See Also

## Key Concepts

- Commands can be run from the shell, bound to keys, entered at the prompt (`C-b :`), or placed in `~/.tmux.conf`
- Commands are queued and executed in order; some (`if-shell`, `confirm-before`) pause the queue
- Semicolons separate commands into a sequence: `new-session; new-window`
- Comments start with unquoted `#`; line continuation with trailing `\`
- Strings: single-quoted (`'`), double-quoted (`"`), or braced (`{}`)
- In double quotes: `$VAR` expands env vars, `~` expands home, `\n` / `\t` / `\e` are special
- Config-file conditionals: `%if`, `%elif`, `%else`, `%endif`

```bash
%if "#{==:#{host},myhost}"
set -g status-style bg=red
%elif "#{==:#{host},myotherhost}"
set -g status-style bg=green
%else
set -g status-style bg=blue
%endif
```

## Essential Commands

### Session Commands

| Command | Alias | Description |
|---------|-------|-------------|
| `new-session [-AdDEPX] [-c dir] [-n win] [-s name] [-t group] [-x W] [-y H] [cmd]` | `new` | Create session |
| `attach-session [-dErx] [-c dir] [-t session]` | `attach` | Attach to session |
| `detach-client [-aP] [-E cmd] [-s session] [-t client]` | `detach` | Detach client |
| `kill-session [-aC] [-t session]` | | Destroy session |
| `list-sessions [-F fmt] [-f filter]` | `ls` | List sessions |
| `rename-session [-t session] name` | `rename` | Rename session |
| `switch-client [-Elnpr] [-c client] [-t session] [-T key-table]` | `switchc` | Switch client session |

### Window Commands

| Command | Alias | Description |
|---------|-------|-------------|
| `new-window [-abdkPS] [-c dir] [-n name] [-t win] [cmd]` | `neww` | Create window |
| `kill-window [-a] [-t win]` | `killw` | Kill window |
| `list-windows [-a] [-F fmt] [-f filter] [-t session]` | `lsw` | List windows |
| `rename-window [-t win] name` | `renamew` | Rename window |
| `select-window [-lnpT] [-t win]` | `selectw` | Select window |
| `next-window [-a] [-t session]` | `next` | Next window |
| `previous-window [-a] [-t session]` | `prev` | Previous window |
| `last-window [-t session]` | `last` | Last-used window |

### Pane Commands

| Command | Alias | Description |
|---------|-------|-------------|
| `split-window [-bdfhIvPZ] [-c dir] [-l size] [-t pane] [cmd]` | `splitw` | Split pane (`-h` horiz, `-v` vert) |
| `kill-pane [-a] [-t pane]` | `killp` | Kill pane |
| `select-pane [-DdeLlMmRUZ] [-T title] [-t pane]` | `selectp` | Select pane |
| `swap-pane [-dDUZ] [-s src] [-t dst]` | `swapp` | Swap two panes |
| `resize-pane [-DLMRTUZ] [-t pane] [-x W] [-y H] [adj]` | `resizep` | Resize pane |
| `break-pane [-abdP] [-F fmt] [-n name] [-s src] [-t dst]` | `breakp` | Break pane to window |
| `join-pane [-bdfhv] [-l size] [-s src] [-t dst]` | `joinp` | Join pane to window |
| `list-panes [-as] [-F fmt] [-f filter] [-t target]` | `lsp` | List panes |

### Copy Mode Commands

| Command | Alias | Description |
|---------|-------|-------------|
| `copy-mode [-deHMqSu] [-s src] [-t pane]` | | Enter copy mode |
| `paste-buffer [-dpr] [-b buf] [-s sep] [-t pane]` | `pasteb` | Paste buffer |
| `list-buffers [-F fmt] [-f filter]` | `lsb` | List buffers |
| `save-buffer [-a] [-b buf] path` | `saveb` | Save buffer to file |
| `load-buffer [-w] [-b buf] [-t client] path` | `loadb` | Load buffer from file |
| `delete-buffer [-b buf]` | `deleteb` | Delete buffer |

### Display Commands

| Command | Alias | Description |
|---------|-------|-------------|
| `display-message [-aIlNpv] [-c client] [-d delay] [-t pane] [msg]` | `display` | Display message |
| `display-panes [-bN] [-d duration] [-t client] [template]` | `displayp` | Show pane numbers |
| `command-prompt [-1beFiklN] [-I inputs] [-p prompts] [-t client] [tmpl]` | | Open command prompt |

### Miscellaneous Commands

| Command | Alias | Description |
|---------|-------|-------------|
| `source-file [-Fnqv] [-t pane] path` | `source` | Execute commands from file |
| `set-option [-aFgopqsuUw] [-t pane] option [value]` | `set` | Set an option |
| `show-options [-AgHpqsvw] [-t pane] [option]` | `show` | Show options |
| `bind-key [-nr] [-N note] [-T key-table] key [cmd ...]` | `bind` | Bind a key |
| `unbind-key [-anq] [-T key-table] key` | `unbind` | Unbind a key |
| `list-keys [-1aN] [-P prefix] [-T key-table] [key]` | `lsk` | List key bindings |
| `refresh-client [-cDlLRSU] [-t client]` | `refresh` | Refresh client |

## Options

### Server Options (`set -s`)

| Option | Values | Description |
|--------|--------|-------------|
| `default-terminal` | terminal string | Default terminal (e.g. `tmux-256color`) |
| `escape-time` | milliseconds | Wait time after Escape key (default: 500) |
| `focus-events` | on / off | Pass focus events to apps |
| `history-file` | path | Command prompt history file |
| `set-clipboard` | on / external / off | Terminal clipboard integration |

### Session Options (`set -g`)

| Option | Values | Description |
|--------|--------|-------------|
| `base-index` | number | Starting window index (default: 0) |
| `default-command` | command | Default command for new windows |
| `default-shell` | path | Default shell |
| `display-time` | milliseconds | Message display duration |
| `history-limit` | lines | Scrollback limit (default: 2000) |
| `mouse` | on / off | Mouse support |
| `prefix` | key | Prefix key (default: `C-b`) |
| `prefix2` | key | Secondary prefix key |
| `renumber-windows` | on / off | Renumber on close |
| `repeat-time` | milliseconds | Repeat key timeout (default: 500) |
| `set-titles` | on / off | Set terminal title |
| `status` | off / on / 2-5 | Status line visibility/height |
| `status-interval` | seconds | Status refresh interval |
| `status-keys` | vi / emacs | Status line key mode |
| `status-left` | format string | Left status content |
| `status-right` | format string | Right status content |
| `visual-activity` | on / off / both | Activity notification |
| `visual-bell` | on / off / both | Bell notification |

### Window Options (`set -wg`)

| Option | Values | Description |
|--------|--------|-------------|
| `aggressive-resize` | on / off | Size to smallest/largest client |
| `automatic-rename` | on / off | Auto-rename windows |
| `clock-mode-style` | 12 / 24 | Clock format |
| `main-pane-height` | height | Main pane height |
| `main-pane-width` | width | Main pane width |
| `mode-keys` | vi / emacs | Copy mode key style |
| `monitor-activity` | on / off | Activity monitoring |
| `monitor-bell` | on / off | Bell monitoring |
| `monitor-silence` | interval | Silence monitoring |
| `pane-base-index` | number | Starting pane index |
| `window-size` | largest / smallest / manual / latest | Window sizing strategy |

### Pane Options (`set -p`)

| Option | Values | Description |
|--------|--------|-------------|
| `allow-rename` | on / off | Allow programs to rename window |
| `allow-set-title` | on / off | Allow programs to set title |
| `alternate-screen` | on / off | Alternate screen support |
| `remain-on-exit` | on / off / failed | Keep pane after program exits |
| `synchronize-panes` | on / off | Send input to all panes |

## Formats

Format variables are used with `-F` flag, enclosed in `#{` and `}`.

### Common Variables

| Variable | Short | Description |
|----------|-------|-------------|
| `#{session_name}` | `#S` | Session name |
| `#{session_id}` | | Unique session ID |
| `#{session_windows}` | | Window count in session |
| `#{session_attached}` | | Attached client count |
| `#{window_name}` | `#W` | Window name |
| `#{window_id}` | | Unique window ID |
| `#{window_index}` | `#I` | Window index |
| `#{window_active}` | | 1 if active window |
| `#{window_flags}` | `#F` | Window flags |
| `#{window_panes}` | | Pane count in window |
| `#{pane_id}` | `#D` | Unique pane ID |
| `#{pane_index}` | `#P` | Pane index |
| `#{pane_title}` | `#T` | Pane title |
| `#{pane_current_command}` | | Running command |
| `#{pane_current_path}` | | Current directory |
| `#{pane_pid}` | | PID of first process |
| `#{pane_width}` | | Pane width |
| `#{pane_height}` | | Pane height |
| `#{client_name}` | | Client name |
| `#{client_tty}` | | Client pseudo terminal |
| `#{host}` | `#H` | Hostname |
| `#{host_short}` | `#h` | Hostname (no domain) |

### Conditionals and Comparisons

```bash
# Ternary conditional
#{?session_attached,attached,not attached}

# Comparisons (return 1 or 0)
#{==:#{host},myhost}       # equal
#{!=:#{host},myhost}       # not equal
#{<:#{window_index},5}     # less than
#{>:#{window_index},5}     # greater than
#{||:#{a},#{b}}            # OR
#{&&:#{a},#{b}}            # AND
```

### Modifiers

| Modifier | Description |
|----------|-------------|
| `#{=N:var}` | Limit to N characters |
| `#{t:var}` | Convert time to string |
| `#{b:var}` | Basename |
| `#{d:var}` | Dirname |
| `#{q:var}` | Escape shell characters |
| `#{E:var}` | Expand format twice |
| `#{s/foo/bar/:var}` | Substitute foo with bar |

## Styles

Styles set colors and attributes for options like `status-style`, `pane-border-style`, etc.

### Format

```
fg=colour bg=colour [attributes]
```

### Colors

- Named: `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`
- Bright: `brightred`, `brightgreen`, etc.
- 256-color: `colour0` to `colour255`
- Hex RGB: `#ffffff`
- Special: `default`, `terminal`

### Attributes

`bold` (or `bright`), `dim`, `underscore`, `blink`, `reverse`, `hidden`, `italics`, `overline`, `strikethrough`, `none` -- prefix with `no` to unset (e.g. `nobold`)

### Examples

```bash
fg=yellow bold underscore blink
bg=black,fg=default,noreverse
```

## Hooks

Hooks run commands when events occur. Set with `set-hook`, show with `show-hooks`.

### Common Hooks

| Hook | Trigger |
|------|---------|
| `after-`*command* | After any tmux command (e.g. `after-split-window`) |
| `alert-activity` | Window has activity |
| `alert-bell` | Window has bell |
| `alert-silence` | Window has been silent |
| `client-attached` | Client attached |
| `client-detached` | Client detached |
| `client-resized` | Client resized |
| `client-session-changed` | Client changed session |
| `pane-died` | Program exited, pane kept (`remain-on-exit`) |
| `pane-exited` | Program in pane exited |
| `pane-focus-in` | Focus entered pane |
| `pane-focus-out` | Focus left pane |
| `session-created` | Session created |
| `session-closed` | Session closed |
| `window-layout-changed` | Layout changed |
| `window-renamed` | Window renamed |

### Hook Commands

```bash
set-hook [-agpRuw] [-t target-pane] hook-name [command]
# Set/unset a hook; -R runs immediately

show-hooks [-gpw] [-t target-pane] [hook]
# Show hooks
```

## Common Workflows

### Configuration Examples

```bash
# Change prefix to C-a
set -g prefix C-a
unbind C-b
bind C-a send-prefix

# Mouse, history, numbering
set -g mouse on
set -g history-limit 10000
set -g base-index 1
set -g pane-base-index 1
set -g renumber-windows on

# Vi mode
set -g mode-keys vi
set -g status-keys vi

# Custom split bindings
bind | split-window -h
bind - split-window -v

# Reload config
bind r source-file ~/.tmux.conf \; display-message "Config reloaded"

# Status line styling
set -g status-style bg=black,fg=white
set -g status-left '[#S] '
set -g status-right '%H:%M %d-%b-%y'
set -g window-status-current-style bg=red,fg=white,bold

# Pane borders
set -g pane-border-style fg=blue
set -g pane-active-border-style fg=red
```

### send-keys

```bash
# Send command to a specific pane (C-m = Enter)
tmux send-keys -t session:window.pane 'ls -la' C-m

# Send text without pressing enter
tmux send-keys -t mywindow 'echo hello'
```

### pipe-pane

```bash
# Log pane output to file
tmux pipe-pane -o 'cat >> ~/output.log'

# Stop logging
tmux pipe-pane
```

### capture-pane

```bash
# Capture visible content
tmux capture-pane -p

# Capture with history (last 1000 lines)
tmux capture-pane -S -1000 -p

# Save to file
tmux capture-pane -S -1000 -p > output.txt
```

### run-shell

```bash
# Run command in background
tmux run-shell 'sleep 5 && echo done'

# Run with output shown
tmux run-shell -b 'ls -la'
```

### Conditional Execution

```bash
# If shell command succeeds, run tmux command
tmux if-shell '[ -d ~/project ]' 'display-message "Project exists"'

# Format-based condition
tmux if-shell -F '#{==:#{session_name},work}' 'set status-bg red'
```

## See Also

- `tmux-overview.md` -- core concepts, target specification, environment variables, quick reference
- `tmux-keybindings.md` -- default key bindings, mouse support, copy mode keys
