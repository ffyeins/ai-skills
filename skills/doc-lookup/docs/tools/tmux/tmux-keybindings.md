# Tmux Key Bindings

> Default key bindings, key tables, and mouse support for tmux.

**Contents**

- Key Concepts
- Default Key Bindings
- Binding Commands
- Mouse Support
- See Also

## Key Concepts

- **Prefix key**: `C-b` (Ctrl-b) by default. Press prefix, then the command key.
- **Key tables** control which bindings are active:
  - `root` -- bindings that work without prefix (e.g., mouse events)
  - `prefix` -- bindings available after pressing the prefix key
  - `copy-mode` -- bindings active in emacs-style copy mode
  - `copy-mode-vi` -- bindings active in vi-style copy mode
- Use `bind-key` / `unbind-key` to customize bindings
- Use `list-keys` (`C-b ?`) to see all current bindings

## Default Key Bindings

All bindings below require the prefix key (`C-b`) first unless noted otherwise.

### Essential

| Key | Function |
|-----|----------|
| `C-b` | Send the prefix key through to the application |
| `?` | List all key bindings |
| `:` | Enter the tmux command prompt |

### Session Management

| Key | Function |
|-----|----------|
| `$` | Rename the current session |
| `d` | Detach the current client |
| `D` | Choose a client to detach |
| `(` | Switch to the previous session |
| `)` | Switch to the next session |
| `L` | Switch back to the last session |
| `s` | Select a new session interactively |

### Window Management

| Key | Function |
|-----|----------|
| `c` | Create a new window |
| `,` | Rename the current window |
| `&` | Kill the current window |
| `'` | Prompt for a window index to select |
| `.` | Prompt for an index to move the current window |
| `0-9` | Select windows 0 to 9 |
| `n` | Change to the next window |
| `p` | Change to the previous window |
| `l` | Move to the previously selected window |
| `w` | Choose the current window interactively |
| `f` | Prompt to search for text in open windows |
| `i` | Display information about the current window |

### Pane Management

| Key | Function |
|-----|----------|
| `"` | Split the current pane top/bottom |
| `%` | Split the current pane left/right |
| `!` | Break the current pane out of the window |
| `x` | Kill the current pane |
| `o` | Select the next pane in the current window |
| `;` | Move to the previously active pane |
| `q` | Briefly display pane indexes |
| `z` | Toggle zoom state of the current pane |
| `{` | Swap the current pane with the previous pane |
| `}` | Swap the current pane with the next pane |
| `m` | Mark the current pane |
| `M` | Clear the marked pane |
| `Up/Down/Left/Right` | Change to the pane in that direction |
| `C-Up/Down/Left/Right` | Resize pane in steps of one cell |
| `M-Up/Down/Left/Right` | Resize pane in steps of five cells |
| `C-o` | Rotate the panes forwards |
| `M-o` | Rotate the panes backwards |

### Layouts

| Key | Function |
|-----|----------|
| `Space` | Arrange the current window in the next preset layout |
| `M-1` | even-horizontal layout |
| `M-2` | even-vertical layout |
| `M-3` | main-horizontal layout |
| `M-4` | main-horizontal-mirrored layout |
| `M-5` | main-vertical layout |
| `M-6` | main-vertical-mirrored layout |
| `M-7` | tiled layout |

### Copy Mode and Buffers

| Key | Function |
|-----|----------|
| `[` | Enter copy mode to copy text or view the history |
| `]` | Paste the most recently copied buffer of text |
| `#` | List all paste buffers |
| `=` | Choose which buffer to paste interactively |
| `-` | Delete the most recently copied buffer of text |
| `Page Up` | Enter copy mode and scroll one page up |

#### Copy Mode Navigation (vi mode)

| Key | Function |
|-----|----------|
| `q` | Exit copy mode |
| `Space` | Start selection |
| `Enter` | Copy selection |
| `/` | Search forward |
| `?` | Search backward |
| `n` | Next search result |

### Miscellaneous

| Key | Function |
|-----|----------|
| `t` | Show the time |
| `r` | Force redraw of the attached client |
| `~` | Show previous messages from tmux |
| `C-z` | Suspend the tmux client |
| `M-n` | Move to the next window with a bell or activity marker |
| `M-p` | Move to the previous window with a bell or activity marker |

## Binding Commands

```
bind-key [-nr] [-N note] [-T key-table] key command [arguments]
unbind-key [-anq] [-T key-table] key
list-keys [-1aN] [-P prefix-string] [-T key-table] [key]
```

- `-n` -- bind in the `root` table (no prefix needed)
- `-r` -- allow the key to repeat within `repeat-time` (default 500ms)
- `-T key-table` -- bind in a specific key table
- `-N note` -- attach a description to the binding

### Common Customizations

```bash
# Change prefix to C-a
set-option -g prefix C-a
unbind-key C-b
bind-key C-a send-prefix

# Split panes using | and -
bind-key | split-window -h
bind-key - split-window -v
unbind-key '"'
unbind-key %

# Reload config
bind-key r source-file ~/.tmux.conf \; display-message "Config reloaded"

# Vi mode keys
set-option -g mode-keys vi
set-option -g status-keys vi
```

## Mouse Support

Enable with:

```bash
set-option -g mouse on
```

### Mouse Events

| Event | Description |
|-------|-------------|
| `MouseDown1` / `MouseUp1` | Left button press/release |
| `MouseDown2` / `MouseUp2` | Middle button press/release |
| `MouseDown3` / `MouseUp3` | Right button press/release |
| `MouseDrag1` / `MouseDragEnd1` | Left button drag/drag end |
| `MouseDrag2` / `MouseDragEnd2` | Middle button drag/drag end |
| `MouseDrag3` / `MouseDragEnd3` | Right button drag/drag end |
| `WheelUp` / `WheelDown` | Scroll wheel up/down |
| `SecondClick1/2/3` | Second click (buttons 1-3) |
| `DoubleClick1/2/3` | Double click (buttons 1-3) |
| `TripleClick1/2/3` | Triple click (buttons 1-3) |

### Location Suffixes

Append a location suffix to a mouse event to scope where it applies:

| Suffix | Location |
|--------|----------|
| `Pane` | Contents of a pane |
| `Border` | Pane border |
| `Status` | Status line window list |
| `StatusLeft` | Left part of status line |
| `StatusRight` | Right part of status line |
| `StatusDefault` | Any other part of status line |

Examples: `MouseDown1Status`, `WheelDownPane`

Use `{mouse}` or `=` in commands to refer to the mouse position.

## See Also

- `tmux-overview.md` -- architecture, sessions, windows, panes, configuration, and options
- `tmux-scripting.md` -- commands, targets, formats, hooks, and automation
