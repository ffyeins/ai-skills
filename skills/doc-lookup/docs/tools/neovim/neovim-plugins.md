# Neovim Plugins

> Lazy.nvim plugin manager, Telescope, Treesitter, gitsigns, mini.nvim, and how to add new plugins.

**Contents**

- Lazy.nvim -- Plugin Manager
- Telescope -- Fuzzy Finder
- Treesitter -- Syntax and Structure
- Gitsigns -- Git Integration
- Mini.nvim -- Utility Collection
- Todo-comments.nvim
- Guess-indent.nvim
- Adding a New Plugin -- Checklist
- See Also

## Lazy.nvim -- Plugin Manager

Kickstart.nvim uses `folke/lazy.nvim` for plugin management. It handles installation, loading, and updates.

### Bootstrap

Lazy.nvim is bootstrapped at the top of `init.lua`:

```lua
local lazypath = vim.fn.stdpath('data') .. '/lazy/lazy.nvim'
if not (vim.uv or vim.loop).fs_stat(lazypath) then
  local out = vim.fn.system({
    'git', 'clone', '--filter=blob:none',
    '--branch=stable',
    'https://github.com/folke/lazy.nvim.git',
    lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)
```

### Plugin Spec Format

Each plugin is a Lua table with these fields:

| Field | Type | Description |
|-------|------|-------------|
| `[1]` | `string` | Short GitHub URL (e.g., `'nvim-telescope/telescope.nvim'`) |
| `dependencies` | `table` | Plugins that must load first |
| `event` | `string` or `table` | Lazy-load on event(s) |
| `cmd` | `string` or `table` | Lazy-load on command(s) |
| `ft` | `string` or `table` | Lazy-load on filetype(s) |
| `keys` | `table` | Lazy-load on keymap(s) |
| `opts` | `table` or `function` | Passed to `plugin.setup(opts)` |
| `config` | `function` | Custom setup function (runs after loading) |
| `init` | `function` | Runs during startup (before loading) |
| `build` | `string` or `function` | Build command (runs after install/update) |
| `enabled` | `boolean` or `function` | Whether to load the plugin |
| `cond` | `boolean` or `function` | Condition to load (like `enabled` but affects deps) |
| `lazy` | `boolean` | Force lazy loading (default: `false`) |
| `priority` | `number` | Loading priority (higher = earlier; default: 50) |
| `version` | `string` | Version constraint (e.g., `'1.*'`, `'^1.0'`) |
| `branch` | `string` | Git branch to track |
| `tag` | `string` | Git tag to use |

### Spec Examples

```lua
-- Minimal: just install
{ 'tpope/vim-sleuth' }

-- With options (auto-calls setup())
{ 'numToStr/Comment.nvim', opts = {} }

-- Lazy-load on event
{
  'lewis6991/gitsigns.nvim',
  event = { 'BufReadPre', 'BufNewFile' },
  opts = { signs = { add = { text = '+' } } },
}

-- Lazy-load on command
{ 'stevearc/conform.nvim', cmd = { 'ConformInfo' } }

-- Lazy-load on keymap
{
  'nvim-telescope/telescope.nvim',
  keys = {
    { '<leader>sf', '<cmd>Telescope find_files<CR>', desc = 'Find files' },
  },
}

-- With build step
{
  'nvim-telescope/telescope-fzf-native.nvim',
  build = 'make',
  cond = function() return vim.fn.executable('make') == 1 end,
}

-- Full config function
{
  'neovim/nvim-lspconfig',
  config = function()
    -- complex setup logic here
  end,
}
```

### Lazy-Loading Events

| Event | When |
|-------|------|
| `VeryLazy` | After UI loads (good for non-essential plugins) |
| `BufReadPre` | Before reading a file into a buffer |
| `BufReadPost` | After reading a file |
| `BufNewFile` | When creating a new file |
| `InsertEnter` | When entering insert mode |
| `VimEnter` | After all startup is complete |
| `CmdlineEnter` | When entering the command line |

### Lazy.nvim Commands

| Command | Description |
|---------|-------------|
| `:Lazy` | Open the Lazy.nvim dashboard |
| `:Lazy update` | Update all plugins |
| `:Lazy sync` | Install, clean, and update |
| `:Lazy check` | Check for updates |
| `:Lazy clean` | Remove unused plugins |
| `:Lazy restore` | Restore plugins to lockfile versions |
| `:Lazy profile` | Show startup profiling |
| `:Lazy log` | Show recent updates |
| `:Lazy health` | Run health check |

### Adding a New Plugin

Add a spec to the `require('lazy').setup()` call, or place a file in `lua/custom/plugins/`:

```lua
-- lua/custom/plugins/autopairs.lua
return {
  'windwp/nvim-autopairs',
  event = 'InsertEnter',
  dependencies = { 'saghen/blink.cmp' },
  config = function()
    require('nvim-autopairs').setup({})
  end,
}
```

Each file in `lua/custom/plugins/` should return a plugin spec (or a list of specs). Kickstart.nvim imports this directory via:

```lua
{ import = 'custom.plugins' }
```

## Telescope -- Fuzzy Finder

`nvim-telescope/telescope.nvim` provides fuzzy finding for files, grep, LSP symbols, and more.

### Core Pickers

| Picker | Command | Description |
|--------|---------|-------------|
| `find_files` | `:Telescope find_files` | Find files by name |
| `live_grep` | `:Telescope live_grep` | Search file contents |
| `buffers` | `:Telescope buffers` | Switch between open buffers |
| `help_tags` | `:Telescope help_tags` | Search help documentation |
| `keymaps` | `:Telescope keymaps` | Search all keymaps |
| `oldfiles` | `:Telescope oldfiles` | Recently opened files |
| `commands` | `:Telescope commands` | Search all commands |
| `diagnostics` | `:Telescope diagnostics` | Browse diagnostics |
| `builtin` | `:Telescope builtin` | List all pickers |
| `resume` | `:Telescope resume` | Reopen last picker |
| `grep_string` | `:Telescope grep_string` | Grep for word under cursor |
| `current_buffer_fuzzy_find` | `:Telescope current_buffer_fuzzy_find` | Fuzzy search in buffer |

### LSP Pickers

| Picker | Description |
|--------|-------------|
| `lsp_references` | References to symbol |
| `lsp_definitions` | Definition(s) of symbol |
| `lsp_implementations` | Implementations of symbol |
| `lsp_type_definitions` | Type definition of symbol |
| `lsp_document_symbols` | Symbols in current file |
| `lsp_workspace_symbols` | Symbols across workspace |

### Telescope Keymaps in Picker

| Key | Action |
|-----|--------|
| `<C-n>` / `<C-p>` | Next / previous result |
| `<CR>` | Open selected item |
| `<C-x>` | Open in horizontal split |
| `<C-v>` | Open in vertical split |
| `<C-t>` | Open in new tab |
| `<C-q>` | Send all results to quickfix |
| `<M-q>` | Send selected to quickfix |
| `<C-/>` | Show picker keymaps (insert mode) |
| `?` | Show picker keymaps (normal mode) |

### Extensions

Kickstart.nvim loads two extensions:

```lua
pcall(require('telescope').load_extension, 'fzf')       -- faster sorting
pcall(require('telescope').load_extension, 'ui-select')  -- vim.ui.select
```

## Treesitter -- Syntax and Structure

`nvim-treesitter` provides incremental parsing for better syntax highlighting, indentation, and code navigation.

### Configuration in Kickstart

Kickstart.nvim uses a `FileType` autocommand to start treesitter for supported filetypes:

```lua
vim.api.nvim_create_autocmd('FileType', {
  pattern = { 'bash', 'c', 'diff', 'html', 'lua', 'luadoc',
              'markdown', 'markdown_inline', 'query', 'vim', 'vimdoc' },
  callback = function()
    vim.treesitter.start()
  end,
})
```

### Adding Language Support

Install a parser using `:TSInstall`:

```vim
:TSInstall python          " Install Python parser
:TSInstall javascript      " Install JavaScript parser
:TSInstall typescript
:TSInstall rust
:TSInstall go
```

Then add the filetype to the autocommand pattern, or configure `nvim-treesitter` with `ensure_installed`:

```lua
{
  'nvim-treesitter/nvim-treesitter',
  build = ':TSUpdate',
  opts = {
    ensure_installed = {
      'bash', 'c', 'lua', 'python', 'javascript',
      'typescript', 'rust', 'go', 'html', 'css',
    },
    auto_install = true,
  },
}
```

### Treesitter Commands

| Command | Description |
|---------|-------------|
| `:TSInstall {lang}` | Install a parser |
| `:TSUpdate` | Update all installed parsers |
| `:TSInstallInfo` | List installed/available parsers |
| `:InspectTree` | Show syntax tree for current buffer |
| `:TSHighlightCapturesUnderCursor` | Show highlight groups at cursor |

### Treesitter Text Objects (with nvim-treesitter-textobjects)

If you add `nvim-treesitter/nvim-treesitter-textobjects`:

```lua
-- Select function/class text objects
{ 'af', '@function.outer' }  -- around function
{ 'if', '@function.inner' }  -- inside function
{ 'ac', '@class.outer' }     -- around class
{ 'ic', '@class.inner' }     -- inside class
```

## Gitsigns -- Git Integration

`lewis6991/gitsigns.nvim` shows git diff signs in the sign column and provides hunk operations.

### Signs

| Symbol | Meaning |
|--------|---------|
| `+` | Added lines |
| `~` | Changed lines |
| `_` | Deleted line (below) |
| `‾` | Deleted line (above) |
| `┃` | Changed-deleted |

### Hunk Operations (kickstart.nvim `<leader>h` prefix)

```lua
-- In the gitsigns on_attach callback:
map('n', '<leader>hs', gitsigns.stage_hunk, 'Stage hunk')
map('n', '<leader>hr', gitsigns.reset_hunk, 'Reset hunk')
map('v', '<leader>hs', function() gitsigns.stage_hunk({ vim.fn.line('.'), vim.fn.line('v') }) end)
map('v', '<leader>hr', function() gitsigns.reset_hunk({ vim.fn.line('.'), vim.fn.line('v') }) end)
map('n', '<leader>hS', gitsigns.stage_buffer, 'Stage buffer')
map('n', '<leader>hR', gitsigns.reset_buffer, 'Reset buffer')
map('n', '<leader>hu', gitsigns.undo_stage_hunk, 'Undo stage hunk')
map('n', '<leader>hp', gitsigns.preview_hunk, 'Preview hunk')
map('n', '<leader>hb', function() gitsigns.blame_line({ full = true }) end, 'Blame line')
map('n', '<leader>hd', gitsigns.diffthis, 'Diff against index')
map('n', '<leader>hD', function() gitsigns.diffthis('~') end, 'Diff against last commit')
map('n', '<leader>tb', gitsigns.toggle_current_line_blame, 'Toggle blame')
map('n', '<leader>td', gitsigns.toggle_deleted, 'Toggle deleted')
```

### Navigation

| Mapping | Action |
|---------|--------|
| `]c` | Next hunk |
| `[c` | Previous hunk |

## Mini.nvim -- Utility Collection

Kickstart.nvim uses select modules from `echasnovski/mini.nvim`:

### mini.ai -- Extended Text Objects

Adds `a`/`i` text objects beyond built-in ones:

| Text Object | Description |
|-------------|-------------|
| `af` / `if` | Around / inside function call |
| `aa` / `ia` | Around / inside argument |
| `ab` / `ib` | Around / inside brackets (any type) |
| `aq` / `iq` | Around / inside quotes (any type) |

Example: `ciq` changes inside any quote, `daf` deletes a function call.

### mini.surround -- Surround Operations

| Key | Action | Example |
|-----|--------|---------|
| `sa{motion}{char}` | Add surrounding | `saiw"` surrounds word with `"` |
| `sd{char}` | Delete surrounding | `sd"` deletes surrounding `"` |
| `sr{old}{new}` | Replace surrounding | `sr"'` changes `"` to `'` |
| `sf{char}` | Find surrounding (forward) | |
| `sF{char}` | Find surrounding (backward) | |
| `sh{char}` | Highlight surrounding | |

### mini.statusline -- Status Line

Provides a minimal status line out of the box. Kickstart.nvim uses it with:

```lua
require('mini.statusline').setup({
  use_icons = vim.g.have_nerd_font,
})
```

## Todo-comments.nvim

Highlights and searches TODO/FIXME/HACK/NOTE comments:

```lua
{ 'folke/todo-comments.nvim', event = 'VimEnter', dependencies = { 'nvim-lua/plenary.nvim' }, opts = { signs = false } }
```

Search todos with: `:TodoTelescope`, or use `]t` / `[t` to jump between them.

## Guess-indent.nvim

Automatically detects indentation style (tabs vs spaces, width) for each file:

```lua
{ 'NMAC427/guess-indent.nvim', opts = {} }
```

## Adding a New Plugin -- Checklist

1. **Find the plugin** on GitHub
2. **Create a spec** in `lua/custom/plugins/<name>.lua` (or add to init.lua)
3. **Choose lazy-loading** strategy (event, cmd, ft, or keys)
4. **Set dependencies** if the plugin requires other plugins
5. **Configure** via `opts` (simple) or `config` (complex)
6. **Restart Neovim** -- Lazy.nvim auto-installs on startup
7. **Verify** with `:Lazy` and `:checkhealth <plugin>`

### Example: Adding a File Explorer

```lua
-- lua/custom/plugins/neo-tree.lua
return {
  'nvim-neo-tree/neo-tree.nvim',
  version = '*',
  dependencies = {
    'nvim-lua/plenary.nvim',
    'nvim-tree/nvim-web-devicons',
    'MunifTanjim/nui.nvim',
  },
  cmd = 'Neotree',
  keys = {
    { '\\', ':Neotree reveal<CR>', desc = 'NeoTree reveal', silent = true },
  },
  opts = {
    filesystem = {
      window = { mappings = { ['\\'] = 'close_window' } },
    },
  },
}
```

### Example: Adding Autopairs

```lua
-- lua/custom/plugins/autopairs.lua
return {
  'windwp/nvim-autopairs',
  event = 'InsertEnter',
  opts = {},
}
```

## See Also

- `neovim-overview.md` -- runtime directories, configuration structure
- `neovim-lua-api.md` -- Lua patterns used in plugin configs
- `neovim-keybindings.md` -- keymap API, which-key, leader key
- `neovim-lsp.md` -- Mason, lspconfig, blink.cmp, conform.nvim
