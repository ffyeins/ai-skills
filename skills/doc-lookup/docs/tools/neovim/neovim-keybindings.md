# Neovim Key Bindings

> Keymap API, leader key, default Vim motions, kickstart.nvim mappings, and which-key integration.

Verified against: Neovim 0.12.3 and a kickstart.nvim-based config (2026-09)

**Contents**

- vim.keymap.set
- Leader Key
- Default Vim Motions
- Kickstart.nvim Custom Keymaps
- Which-Key
- Inspecting Keymaps
- See Also

## vim.keymap.set

The primary API for defining key mappings in Lua:

```lua
vim.keymap.set(mode, lhs, rhs, opts)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `mode` | `string` or `table` | Mode short-name(s): `'n'`, `'i'`, `'v'`, `'x'`, `'s'`, `'o'`, `'t'`, `'c'`, `''` |
| `lhs` | `string` | Key sequence to map |
| `rhs` | `string` or `function` | Command or Lua function to execute |
| `opts` | `table` (optional) | Options table |

### Mode Short-Names

| Mode | Key | Description |
|------|-----|-------------|
| Normal | `n` | Default editing mode |
| Insert | `i` | Text insertion mode |
| Visual + Select | `v` | Both visual and select |
| Visual | `x` | Visual mode only |
| Select | `s` | Select mode only |
| Operator-pending | `o` | After an operator, before a motion |
| Terminal | `t` | Terminal buffer |
| Command-line | `c` | Command-line mode |
| All (nvo) | `''` | Normal, visual, and operator-pending |

### Common Options

| Option | Default | Description |
|--------|---------|-------------|
| `desc` | | Description (shown in which-key and `:map`) |
| `silent` | `false` | Don't echo the command |
| `buffer` | | Buffer handle; `0` or `true` for current buffer |
| `expr` | `false` | `rhs` is an expression that returns the keys |
| `remap` | `false` | Set to `true` for a recursive mapping (`noremap` isn't supported here) |
| `nowait` | `false` | Don't wait for longer key sequences |

### Examples

```lua
-- Simple mapping
vim.keymap.set('n', '<leader>w', '<cmd>write<CR>', { desc = 'Save file' })

-- Lua function
vim.keymap.set('n', '<leader>x', function()
  vim.api.nvim_buf_delete(0, {})
end, { desc = 'Close buffer' })

-- Multiple modes
vim.keymap.set({ 'n', 'v' }, '<leader>y', '"+y', { desc = 'Yank to clipboard' })

-- Buffer-local mapping (used in LSP on_attach, ftplugin, etc.)
vim.keymap.set('n', 'K', vim.lsp.buf.hover, { buffer = 0, desc = 'LSP hover' })

-- Expression mapping
vim.keymap.set('n', 'j', function()
  return vim.v.count == 0 and 'gj' or 'j'
end, { expr = true, desc = 'Move down (visual line if no count)' })
```

### Deleting a Mapping

```lua
vim.keymap.del('n', '<leader>w')
vim.keymap.del('n', 'K', { buffer = 0 })
```

## Leader Key

Kickstart.nvim sets both leader keys to space:

```lua
vim.g.mapleader = ' '
vim.g.maplocalleader = ' '
```

- `<leader>` -- used for global mappings (e.g., `<leader>sf` for search files)
- `<localleader>` -- for filetype-specific mappings

**Important**: Set leader keys before `require('lazy').setup()` so all plugins see the correct key.

## Default Vim Motions

### Movement

| Key | Motion |
|-----|--------|
| `h` `j` `k` `l` | Left, down, up, right |
| `w` / `W` | Start of next word / WORD |
| `b` / `B` | Start of previous word / WORD |
| `e` / `E` | End of next word / WORD |
| `0` / `^` / `$` | Line start / first non-blank / line end |
| `gg` / `G` | First / last line |
| `{` / `}` | Previous / next blank line (paragraph) |
| `%` | Matching bracket |
| `f{c}` / `F{c}` | Forward / backward to character |
| `t{c}` / `T{c}` | Forward / backward until character |
| `;` / `,` | Repeat / reverse last `f`/`t` |
| `<C-d>` / `<C-u>` | Scroll half-page down / up |
| `<C-f>` / `<C-b>` | Scroll full page down / up |
| `H` / `M` / `L` | Cursor to screen top / middle / bottom |
| `gd` | Go to local definition |
| `gD` | Go to global declaration |

### Operators

Operators compose with motions: `{operator}{motion}` or `{operator}{text-object}`.

| Operator | Action |
|----------|--------|
| `d` | Delete |
| `c` | Change (delete + insert) |
| `y` | Yank (copy) |
| `>` / `<` | Indent / dedent |
| `=` | Auto-indent |
| `gu` / `gU` | Lowercase / uppercase |
| `g~` | Toggle case |
| `!` | Filter through external program |
| `gq` | Format text |

Double the operator to act on the current line: `dd`, `cc`, `yy`, `>>`, `<<`.

### Text Objects

Used after an operator or in visual mode. Format: `{a|i}{object}`.

| Object | `a` (around) | `i` (inside) |
|--------|-------------|-------------|
| `w` | Word + surrounding space | Word |
| `W` | WORD + surrounding space | WORD |
| `s` | Sentence + space | Sentence |
| `p` | Paragraph + blank line | Paragraph |
| `(` or `)` or `b` | Parentheses (incl.) | Parentheses contents |
| `[` or `]` | Brackets (incl.) | Brackets contents |
| `{` or `}` or `B` | Braces (incl.) | Braces contents |
| `<` or `>` | Angle brackets (incl.) | Angle brackets contents |
| `"` / `'` / `` ` `` | Quotes (incl.) | Quotes contents |
| `t` | XML/HTML tag (incl.) | Tag contents |

Examples: `diw` (delete inner word), `ca"` (change around quotes), `yi{` (yank inside braces).

### Registers

| Register | Description |
|----------|-------------|
| `""` | Default (unnamed) register |
| `"0` | Last yank |
| `"1`-`"9` | Delete history (most recent first) |
| `"+` / `"*` | System clipboard |
| `"_` | Black hole (discard) |
| `".` | Last inserted text |
| `"%` | Current filename |
| `":` | Last command |
| `"/` | Last search pattern |

Usage: `"ayw` (yank word into register `a`), `"ap` (paste from register `a`).

### Marks

| Mark | Description |
|------|-------------|
| `m{a-z}` | Set local mark |
| `m{A-Z}` | Set global mark (across files) |
| `` `{mark} `` | Jump to mark (exact position) |
| `'{mark}` | Jump to mark (line start) |
| `` `. `` | Last change position |
| `` `^ `` | Last insert position |
| `` `[ `` / `` `] `` | Start/end of last change or yank |
| `` `< `` / `` `> `` | Start/end of last visual selection |

## Kickstart.nvim Custom Keymaps

### General

| Mapping | Mode | Action |
|---------|------|--------|
| `<Esc>` | n | Clear search highlight (`:nohlsearch`) |
| `<C-h>` | n | Move to left window |
| `<C-j>` | n | Move to lower window |
| `<C-k>` | n | Move to upper window |
| `<C-l>` | n | Move to right window |
| `<leader>q` | n | Open diagnostic quickfix list |
| `<Esc><Esc>` | t | Exit terminal mode |

### Telescope Search (`<leader>s` prefix)

| Mapping | Action |
|---------|--------|
| `<leader>sh` | Search help tags |
| `<leader>sk` | Search keymaps |
| `<leader>sf` | Search (find) files |
| `<leader>ss` | Search Telescope builtins |
| `<leader>sw` | Search current word (normal + visual) |
| `<leader>sg` | Search by grep (live grep) |
| `<leader>sd` | Search diagnostics |
| `<leader>sr` | Search resume (reopen last search) |
| `<leader>s.` | Search recent files |
| `<leader>sc` | Search commands |
| `<leader>s/` | Search in open files (live grep open buffers) |
| `<leader>sn` | Search Neovim config files |
| `<leader>/` | Fuzzy search current buffer |
| `<leader><leader>` | Find existing buffers |

### LSP (active when a language server attaches)

Neovim itself already maps `grn`, `gra`, `grr`, `gri`, `grt`, and `gO` (see `neovim-lsp.md`). Kickstart points the lookups at Telescope pickers and adds `grd`, `grD`, and `gW`.

| Mapping | Mode | Action |
|---------|------|--------|
| `grn` | n | Rename symbol |
| `gra` | n, x | Code action |
| `grr` | n | Go to references (Telescope) |
| `gri` | n | Go to implementation (Telescope) |
| `grd` | n | Go to definition (Telescope) |
| `grD` | n | Go to declaration |
| `gO` | n | Document symbols (Telescope) |
| `gW` | n | Workspace symbols (Telescope) |
| `grt` | n | Go to type definition (Telescope) |
| `<leader>th` | n | Toggle inlay hints |

### Formatting

| Mapping | Mode | Action |
|---------|------|--------|
| `<leader>f` | n | Format buffer (via conform.nvim) |

## Which-Key

Kickstart.nvim uses `folke/which-key.nvim` to display a popup of available keybindings when you press a prefix key and pause.

### Configuration in Kickstart

```lua
{
  'folke/which-key.nvim',
  event = 'VimEnter',
  opts = {
    delay = 0,
    icons = {
      mappings = vim.g.have_nerd_font,
    },
    spec = {
      { '<leader>s', group = '[S]earch' },
      { '<leader>t', group = '[T]oggle' },
      { '<leader>h', group = 'Git [H]unk', mode = { 'n', 'v' } },
    },
  },
}
```

### Registering Groups

Which-key shows group names in the popup. Define them via the `spec` table:

```lua
require('which-key').add({
  { '<leader>c', group = '[C]ode' },
  { '<leader>d', group = '[D]ocument' },
  { '<leader>r', group = '[R]ename' },
})
```

The `[X]` bracket convention highlights the mnemonic letter in the which-key popup.

### Tips

- Press `<leader>` and wait to see all leader mappings
- Any mapping with a `desc` option appears in which-key
- Use `:checkhealth which-key` to find mapping conflicts

## Inspecting Keymaps

```vim
:map              " Show all mappings
:nmap             " Show normal mode mappings
:verbose nmap K   " Show where a mapping was defined
:Telescope keymaps  " Search all keymaps interactively
```

## See Also

- `neovim-overview.md` -- modes, buffers, windows, configuration
- `neovim-lua-api.md` -- vim.keymap.set internals, vim.api, vim.fn
- `neovim-lsp.md` -- LSP keybindings in detail, on_attach pattern
- `neovim-plugins.md` -- which-key plugin configuration, Telescope
