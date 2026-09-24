# Neovim Overview

> Core concepts, configuration layout, options, autocommands, and runtime directories for Neovim.

**Contents**

- Modes
- Buffers, Windows, and Tabs
- Configuration
- Options
- Autocommands
- User Commands
- Global Variables
- Health Checks
- See Also

## Modes

| Mode | Enter | Description |
|------|-------|-------------|
| Normal | `<Esc>` | Default mode; navigate and compose commands |
| Insert | `i`, `a`, `o`, etc. | Type text into the buffer |
| Visual | `v` (char), `V` (line), `<C-v>` (block) | Select text for operations |
| Command | `:` | Execute Ex commands on the command line |
| Replace | `R` | Overwrite characters in place |
| Terminal | `:terminal` | Interact with a shell inside Neovim |
| Select | `gh`, `gH` | Like visual, but typing replaces selection |

Use `<Esc>` (or `<C-[>`) to return to normal mode from any other mode. In terminal mode kickstart.nvim maps `<Esc><Esc>` to exit back to normal mode.

## Buffers, Windows, and Tabs

| Concept | Description |
|---------|-------------|
| **Buffer** | An in-memory copy of a file; may be hidden (not displayed) |
| **Window** | A viewport into a buffer; multiple windows can show the same buffer |
| **Tab page** | A collection of windows; acts as a workspace layout |

```vim
:e file.lua          " Open file in current window (new buffer)
:split / :vsplit     " Horizontal / vertical split
:tabnew              " New tab page
:ls                  " List buffers
:b <name|number>     " Switch to buffer
```

Kickstart.nvim maps `<C-h>`, `<C-j>`, `<C-k>`, `<C-l>` to navigate between windows.

## Configuration

### File Locations

Neovim looks for configuration in this order:

| Path | Notes |
|------|-------|
| `~/.config/nvim/init.lua` | Primary config (kickstart.nvim lives here) |
| `$XDG_CONFIG_HOME/nvim/init.lua` | Respected if `XDG_CONFIG_HOME` is set |
| `~/.config/nvim/lua/` | Lua modules loaded via `require()` |
| `~/.local/share/nvim/` | Data directory (plugins, shada, swap) |
| `~/.local/state/nvim/` | State directory (logs, undo files) |
| `~/.cache/nvim/` | Cache (generated files) |

### Kickstart.nvim Structure

Kickstart.nvim uses a single `init.lua` by default. To split into modules:

```lua
-- init.lua
require('options')    -- loads lua/options.lua or lua/options/init.lua
require('keymaps')
require('plugins')
```

The `lua/custom/plugins/` directory is gitignored by kickstart.nvim so you can add personal plugin specs without modifying init.lua.

### Runtime Directories

Neovim merges files from multiple runtime paths (`runtimepath`):

| Directory | Purpose |
|-----------|---------|
| `plugin/` | Lua/Vimscript files sourced automatically on startup |
| `ftplugin/` | Filetype-specific settings (e.g., `ftplugin/python.lua`) |
| `after/plugin/` | Runs after all `plugin/` files; good for overrides |
| `after/ftplugin/` | Filetype overrides that run last |
| `syntax/` | Custom syntax definitions |
| `indent/` | Custom indentation rules |
| `colors/` | Colorscheme definitions |

## Options

Set options with `vim.opt` (Lua table wrapper) or `vim.o` (raw access).

### Common Options

```lua
vim.opt.number = true           -- Show line numbers
vim.opt.relativenumber = true   -- Relative line numbers
vim.opt.mouse = 'a'             -- Enable mouse in all modes
vim.opt.showmode = false        -- Hide mode (shown in statusline)
vim.opt.clipboard = 'unnamedplus' -- Use system clipboard

vim.opt.breakindent = true      -- Indent wrapped lines
vim.opt.undofile = true         -- Persistent undo across sessions

vim.opt.ignorecase = true       -- Case-insensitive search...
vim.opt.smartcase = true        -- ...unless uppercase is used

vim.opt.signcolumn = 'yes'      -- Always show sign column
vim.opt.updatetime = 250        -- Faster CursorHold events
vim.opt.timeoutlen = 300        -- Time for mapped sequences

vim.opt.splitright = true       -- Open vertical splits to the right
vim.opt.splitbelow = true       -- Open horizontal splits below

vim.opt.list = true             -- Show whitespace characters
vim.opt.listchars = { tab = '» ', trail = '·', nbsp = '␣' }

vim.opt.inccommand = 'split'    -- Live preview for substitutions
vim.opt.cursorline = true       -- Highlight current line
vim.opt.scrolloff = 10          -- Lines of context above/below cursor
```

### Option Scopes

| Scope | Access | Example |
|-------|--------|---------|
| Global | `vim.o`, `vim.go` | `vim.o.background = 'dark'` |
| Window-local | `vim.wo` | `vim.wo.wrap = false` |
| Buffer-local | `vim.bo` | `vim.bo.filetype = 'lua'` |
| Global + local | `vim.opt` | `vim.opt.expandtab = true` |

`vim.opt` is generally preferred because it handles list/map/set options naturally:

```lua
vim.opt.wildignore:append('*.o')          -- Append to list
vim.opt.shortmess:append('I')             -- Append to flags
vim.opt.listchars = { tab = '» ', trail = '·' }  -- Set as table
```

## Autocommands

Create autocommands with `vim.api.nvim_create_autocmd`:

```lua
vim.api.nvim_create_autocmd('TextYankPost', {
  desc = 'Highlight when yanking text',
  group = vim.api.nvim_create_augroup('kickstart-highlight-yank', { clear = true }),
  callback = function()
    vim.hl.on_yank()
  end,
})
```

### Commonly Used Events

| Event | When it fires |
|-------|---------------|
| `BufReadPost` | After reading a buffer from a file |
| `BufWritePre` | Before writing a buffer to a file |
| `BufEnter` | After entering a buffer |
| `FileType` | When filetype is set |
| `LspAttach` | When an LSP client attaches to a buffer |
| `VimEnter` | After all startup is complete |
| `TextYankPost` | After text is yanked |
| `CursorHold` | When cursor hasn't moved for `updatetime` ms |
| `InsertEnter` / `InsertLeave` | Entering/leaving insert mode |
| `WinResized` | After a window is resized |

### Autocommand Groups

Always use groups to prevent duplicate autocommands on config reload:

```lua
local group = vim.api.nvim_create_augroup('my-group', { clear = true })

vim.api.nvim_create_autocmd('BufWritePre', {
  group = group,
  pattern = '*.lua',
  callback = function()
    -- trim trailing whitespace
    vim.cmd([[%s/\s\+$//e]])
  end,
})
```

## User Commands

Define custom `:CommandName` commands:

```lua
vim.api.nvim_create_user_command('Hello', function(opts)
  print('Hello, ' .. opts.args)
end, {
  nargs = '?',     -- 0 or 1 arguments
  desc = 'Say hello',
})
```

## Global Variables

| Variable | Purpose |
|----------|---------|
| `vim.g.mapleader` | Leader key (kickstart: `' '` space) |
| `vim.g.maplocalleader` | Local leader key (kickstart: `' '` space) |
| `vim.g.have_nerd_font` | Kickstart flag for Nerd Font icons |
| `vim.g.loaded_netrw` | Set to `1` to disable netrw (when using file explorer plugins) |

Set leader keys **before** loading plugins so that all mappings use the correct key.

## Health Checks

Run `:checkhealth` to diagnose issues with Neovim and installed plugins.

```vim
:checkhealth              " Check everything
:checkhealth telescope    " Check a specific plugin
:checkhealth lspconfig    " Check LSP configuration
```

Plugins can register health checks in `lua/<plugin>/health.lua` by implementing `check()`.

## See Also

- `neovim-lua-api.md` -- Lua API functions, vim.api, vim.fn, vim.cmd, module system
- `neovim-keybindings.md` -- keymap API, leader key, default Vim motions, which-key
- `neovim-lsp.md` -- LSP setup, Mason, diagnostics, completion, formatting
- `neovim-plugins.md` -- Lazy.nvim, Telescope, Treesitter, and other plugins
