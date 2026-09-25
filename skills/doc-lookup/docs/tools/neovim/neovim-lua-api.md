# Neovim Lua API

> Core Lua interfaces for interacting with Neovim: vim.api, vim.fn, vim.cmd, options, variables, and utilities.

Verified against: Neovim 0.12.3 (2026-09)

**Contents**

- Module System
- vim.api -- Neovim API Functions
- vim.fn -- Vimscript Functions
- vim.cmd -- Execute Ex Commands
- Options
- Variable Scopes
- Table and Utility Functions
- Logging and Debugging
- See Also

## Module System

Neovim loads Lua modules from `lua/` directories in `runtimepath`.

```lua
-- File: lua/mymodule.lua
local M = {}

function M.greet(name)
  print('Hello, ' .. name)
end

return M
```

```lua
-- In init.lua or another module
local mymodule = require('mymodule')
mymodule.greet('world')
```

### Resolution Order

`require('foo')` searches for:

1. `lua/foo.lua`
2. `lua/foo/init.lua`

Modules are cached after first load. Use `:lua package.loaded['foo'] = nil` to force a reload.

### Dot Notation for Subdirectories

```lua
require('plugins.telescope')  -- loads lua/plugins/telescope.lua
```

## vim.api -- Neovim API Functions

Direct bindings to the Neovim C API. These are the most stable and performant way to interact with Neovim.

### Buffer Functions

| Function | Description |
|----------|-------------|
| `nvim_buf_get_lines(buf, start, end, strict)` | Get buffer lines (0-indexed) |
| `nvim_buf_set_lines(buf, start, end, strict, lines)` | Set buffer lines |
| `nvim_buf_get_name(buf)` | Get buffer filename |
| `nvim_buf_set_name(buf, name)` | Set buffer name |
| `nvim_buf_line_count(buf)` | Get number of lines |
| `nvim_buf_delete(buf, opts)` | Delete a buffer |
| `nvim_buf_is_valid(buf)` | Check if buffer handle is valid |

```lua
-- Get current buffer contents
local lines = vim.api.nvim_buf_get_lines(0, 0, -1, false)

-- Replace line 5 (0-indexed)
vim.api.nvim_buf_set_lines(0, 4, 5, false, { 'new content' })

-- Delete buffer without saving
vim.api.nvim_buf_delete(0, { force = true })
```

### Window Functions

| Function | Description |
|----------|-------------|
| `nvim_win_get_cursor(win)` | Get cursor position `{row, col}` (1-indexed row) |
| `nvim_win_set_cursor(win, pos)` | Set cursor position |
| `nvim_win_get_width(win)` | Get window width |
| `nvim_win_get_height(win)` | Get window height |
| `nvim_win_get_buf(win)` | Get window's buffer |
| `nvim_win_set_buf(win, buf)` | Set window's buffer |
| `nvim_win_close(win, force)` | Close window |

```lua
-- Get cursor position in current window
local pos = vim.api.nvim_win_get_cursor(0)  -- {row, col}
```

### General Functions

| Function | Description |
|----------|-------------|
| `nvim_get_current_buf()` | Current buffer handle |
| `nvim_get_current_win()` | Current window handle |
| `nvim_get_current_line()` | Current line as string |
| `nvim_list_bufs()` | List all buffer handles |
| `nvim_list_wins()` | List all window handles |
| `nvim_command(cmd)` | Execute an Ex command |
| `nvim_exec2(src, opts)` | Execute Vimscript, optionally capture output |
| `nvim_echo(chunks, history, opts)` | Display a message; `opts = { err = true }` for an error (replaces the deprecated `nvim_err_writeln`) |
| `nvim_feedkeys(keys, mode, escape_ks)` | Send keys as if typed |
| `nvim_replace_termcodes(str, ...)` | Translate terminal codes like `<CR>` |

### Autocommands and User Commands

```lua
-- Create autocommand group
local group = vim.api.nvim_create_augroup('MyGroup', { clear = true })

-- Create autocommand
vim.api.nvim_create_autocmd('BufWritePre', {
  group = group,
  pattern = '*.lua',
  callback = function(ev)
    -- ev.buf, ev.file, ev.match available
  end,
})

-- Create user command
vim.api.nvim_create_user_command('Greet', function(opts)
  print('Hello ' .. opts.args)
end, { nargs = '?', desc = 'Greet someone' })
```

### Highlights and Namespaces

```lua
-- Set a highlight group
vim.api.nvim_set_hl(0, 'MyHighlight', { fg = '#ff0000', bold = true })

-- Create a namespace (for extmarks, virtual text)
local ns = vim.api.nvim_create_namespace('my_plugin')

-- Add virtual text
vim.api.nvim_buf_set_extmark(buf, ns, line, col, {
  virt_text = { { 'ghost text', 'Comment' } },
})
```

## vim.fn -- Vimscript Functions

Call any Vimscript function from Lua. Function names with special characters use bracket syntax.

```lua
vim.fn.expand('%:p')           -- Full path of current file
vim.fn.fnamemodify(path, ':t') -- Tail (filename) of path
vim.fn.filereadable(path)      -- 1 if file exists and is readable
vim.fn.isdirectory(path)       -- 1 if path is a directory
vim.fn.system('ls')            -- Run shell command, return output
vim.fn.systemlist('ls')        -- Same but returns list of lines
vim.fn.input('Name: ')         -- Prompt user for input
vim.fn.confirm('Sure?', '&Yes\n&No') -- Confirmation dialog
vim.fn.getcwd()                -- Current working directory
vim.fn.stdpath('config')       -- ~/.config/nvim
vim.fn.stdpath('data')         -- ~/.local/share/nvim
vim.fn.has('nvim-0.10')        -- Feature detection (returns 0 or 1)
```

### Special Character Functions

```lua
-- Functions with # or other special chars
vim.fn['fzf#run']({ source = 'ls' })
```

## vim.cmd -- Execute Ex Commands

```lua
vim.cmd('colorscheme tokyonight-night')
vim.cmd('write')
vim.cmd('edit ~/.config/nvim/init.lua')

-- Multi-line with heredoc syntax
vim.cmd([[
  augroup MyGroup
    autocmd!
    autocmd FileType lua setlocal tabstop=2
  augroup END
]])

-- Structured form (safer, avoids string escaping)
vim.cmd.colorscheme('tokyonight-night')
vim.cmd.write()
vim.cmd.edit('~/.config/nvim/init.lua')
```

## Options

### vim.opt vs vim.o

| Interface | Type | List/Map support | Best for |
|-----------|------|-------------------|----------|
| `vim.opt` | `Option` object | Yes (`:append()`, `:remove()`, `:get()`) | Most uses |
| `vim.o` | Raw value | No | Simple scalar options |
| `vim.go` | Global only | No | Force global scope |
| `vim.bo` | Buffer-local | No | Per-buffer settings |
| `vim.wo` | Window-local | No | Per-window settings |

```lua
-- vim.opt: list/map operations
vim.opt.wildignore:append({ '*.o', '*.pyc' })
vim.opt.listchars = { tab = '» ', trail = '·' }
local expandtab = vim.opt.expandtab:get()  -- returns boolean

-- vim.o: simple assignment
vim.o.tabstop = 4
vim.o.background = 'dark'

-- Buffer/window local
vim.bo.filetype = 'markdown'
vim.wo.number = true
```

## Variable Scopes

| Lua accessor | Vimscript scope | Example |
|--------------|-----------------|---------|
| `vim.g` | `g:` (global) | `vim.g.mapleader = ' '` |
| `vim.b` | `b:` (buffer) | `vim.b.my_var = true` |
| `vim.w` | `w:` (window) | `vim.w.my_var = 42` |
| `vim.t` | `t:` (tab) | `vim.t.my_var = 'tab'` |
| `vim.v` | `v:` (Vim special) | `vim.v.count` |
| `vim.env` | `$` (environment) | `vim.env.TERM` |

```lua
-- Delete a variable by setting to nil
vim.g.loaded_netrw = 1       -- set
vim.g.loaded_netrw = nil     -- delete
```

## Table and Utility Functions

### vim.tbl_* -- Table Utilities

```lua
-- Deep merge tables (last wins)
vim.tbl_deep_extend('force', defaults, overrides)

-- Shallow merge
vim.tbl_extend('force', t1, t2)

-- Filter table values
vim.tbl_filter(function(v) return v > 0 end, { -1, 0, 3, 5 })

-- Map over table values
vim.tbl_map(function(v) return v * 2 end, { 1, 2, 3 })

-- Check if value is in list
vim.tbl_contains({ 'a', 'b', 'c' }, 'b')  -- true

-- Get keys
vim.tbl_keys({ a = 1, b = 2 })  -- { 'a', 'b' }

-- Get values
vim.tbl_values({ a = 1, b = 2 })  -- { 1, 2 }

-- Check if table is empty
vim.tbl_isempty({})  -- true

-- Check if table is a list (consecutive integer keys)
vim.islist({ 1, 2, 3 })  -- true
```

### vim.inspect -- Pretty Print

```lua
print(vim.inspect({ a = 1, b = { 2, 3 } }))
-- Output: { a = 1, b = { 2, 3 } }

-- Useful for debugging
vim.print(some_table)  -- shorthand, uses vim.inspect internally
```

### vim.notify -- Notifications

```lua
vim.notify('Something happened', vim.log.levels.INFO)
vim.notify('Oops!', vim.log.levels.ERROR)
vim.notify('Careful', vim.log.levels.WARN)
```

Notification plugins (like `nvim-notify`) override `vim.notify` for better UI.

### Scheduling and Async

```lua
-- Schedule a callback on the main loop (safe from fast callbacks)
vim.schedule(function()
  vim.api.nvim_buf_set_lines(0, 0, 0, false, { 'hello' })
end)

-- Deferred function call
vim.defer_fn(function()
  print('after 1 second')
end, 1000)
```

### vim.fs -- Filesystem Utilities

```lua
vim.fs.basename('/path/to/file.lua')  -- 'file.lua'
vim.fs.dirname('/path/to/file.lua')   -- '/path/to'
vim.fs.joinpath('/path', 'to', 'file') -- '/path/to/file'

-- Find files upward from current file
vim.fs.find({ '.git', 'Makefile' }, {
  upward = true,
  path = vim.fs.dirname(vim.api.nvim_buf_get_name(0)),
})
```

### vim.json -- JSON Encoding/Decoding

```lua
local json_str = vim.json.encode({ key = 'value' })
local table = vim.json.decode('{"key": "value"}')
```

### Type Checking

```lua
vim.validate('name', name, 'string')
vim.validate('age', age, 'number')
vim.validate('callback', cb, 'function', true)  -- true = optional
```

The older single-table form, `vim.validate({ name = { name, 'string' } })`, is deprecated.

## Logging and Debugging

```lua
-- Print to :messages
print('debug info')
vim.print(some_table)

-- Check runtime log
-- :edit $NVIM_LOG_FILE

-- Verbose mode
-- nvim -V10logfile.log
```

## See Also

- `neovim-overview.md` -- modes, configuration, options, autocommands
- `neovim-keybindings.md` -- vim.keymap.set, leader key, default motions
- `neovim-lsp.md` -- LSP client API, diagnostics, completion
- `neovim-plugins.md` -- Lazy.nvim, plugin development patterns
