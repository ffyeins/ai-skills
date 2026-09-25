# Neovim LSP

> Language server setup with Mason and lspconfig, diagnostics, blink.cmp completion, and Conform formatting.

Verified against: Neovim 0.12.3 and a kickstart.nvim-based config (2026-09)

**Contents**

- Architecture
- Adding a Language Server
- vim.lsp.buf -- LSP Actions
- Diagnostics
- Blink.cmp -- Completion
- Conform.nvim -- Formatting
- LSP Troubleshooting
- See Also

## Architecture

Neovim has a built-in LSP client (`vim.lsp`). The typical kickstart.nvim stack:

```
mason-tool-installer → Mason          nvim-lspconfig → vim.lsp.config() → vim.lsp.enable()
        ↓                                   ↓                                   ↓
 Installs binaries                  Default server configs        Starts servers for matching files
```

- **Mason** -- installs language servers, formatters, linters into `~/.local/share/nvim/mason/`
- **mason-tool-installer.nvim** -- installs everything listed in `ensure_installed` on startup
- **nvim-lspconfig** -- ships default configs (command, filetypes, root markers) for each server
- **`vim.lsp.config()` / `vim.lsp.enable()`** -- built into Neovim: merge your settings over those defaults, then start the server when a matching file opens
- **blink.cmp** -- completion engine that integrates with LSP
- **conform.nvim** -- formatting layer (independent of LSP)

## Adding a Language Server

### Step 1: Add the Server to the Config

In kickstart.nvim, add your server to the `servers` table:

```lua
local servers = {
  lua_ls = {
    settings = {
      Lua = {
        completion = { callSnippet = 'Replace' },
      },
    },
  },
  -- Add new servers here:
  pyright = {},
  ts_ls = {},
  gopls = {},
  rust_analyzer = {},
  clangd = {},
  jsonls = {},
  yamlls = {},
  bashls = {},
}
```

### Step 2: Ensure Mason Installs It

The `ensure_installed` table tells `mason-tool-installer` what to auto-install:

```lua
local ensure_installed = vim.tbl_keys(servers)
vim.list_extend(ensure_installed, {
  'stylua',    -- Lua formatter
  'black',     -- Python formatter
  'prettier',  -- JS/TS formatter
  'shfmt',     -- Shell formatter
})
require('mason-tool-installer').setup({ ensure_installed = ensure_installed })
```

### Step 3: Server Starts Automatically

Kickstart loops over `servers`, adds blink.cmp's capabilities, and hands each entry to Neovim:

```lua
local capabilities = require('blink.cmp').get_lsp_capabilities()

for name, server in pairs(servers) do
  server.capabilities = vim.tbl_deep_extend('force', {}, capabilities, server.capabilities or {})
  vim.lsp.config(name, server)  -- merge with nvim-lspconfig's defaults
  vim.lsp.enable(name)          -- start it for matching filetypes
end
```

### Manual Server Setup (Without Mason)

For a server Mason doesn't install, point `cmd` at your binary:

```lua
vim.lsp.config('serve_d', {
  cmd = { '/usr/local/bin/serve-d' },
})
vim.lsp.enable('serve_d')
```

nvim-lspconfig supplies the filetypes and root markers for servers it knows. For one it doesn't, also set `filetypes` and `root_markers` (e.g. `{ '.git' }`).

## vim.lsp.buf -- LSP Actions

These functions operate on the current buffer's attached language server:

| Function | Description |
|----------|-------------|
| `vim.lsp.buf.hover()` | Show hover documentation |
| `vim.lsp.buf.definition()` | Jump to definition |
| `vim.lsp.buf.declaration()` | Jump to declaration |
| `vim.lsp.buf.references()` | List all references |
| `vim.lsp.buf.implementation()` | Jump to implementation |
| `vim.lsp.buf.type_definition()` | Jump to type definition |
| `vim.lsp.buf.rename()` | Rename symbol under cursor |
| `vim.lsp.buf.code_action()` | Show available code actions |
| `vim.lsp.buf.signature_help()` | Show function signature |
| `vim.lsp.buf.format()` | Format buffer (or range) |
| `vim.lsp.buf.document_symbol()` | List symbols in buffer |
| `vim.lsp.buf.workspace_symbol()` | Search workspace symbols |

### Document Highlights

Kickstart.nvim highlights other occurrences of the symbol under the cursor:

```lua
vim.api.nvim_create_autocmd('LspAttach', {
  callback = function(event)
    local client = vim.lsp.get_client_by_id(event.data.client_id)
    if client and client:supports_method('textDocument/documentHighlight') then
      local group = vim.api.nvim_create_augroup('kickstart-lsp-highlight', { clear = false })
      vim.api.nvim_create_autocmd({ 'CursorHold', 'CursorHoldI' }, {
        buffer = event.buf,
        group = group,
        callback = vim.lsp.buf.document_highlight,
      })
      vim.api.nvim_create_autocmd({ 'CursorMoved', 'CursorMovedI' }, {
        buffer = event.buf,
        group = group,
        callback = vim.lsp.buf.clear_references,
      })
    end
  end,
})
```

### Inlay Hints

Toggle inlay hints (type annotations inline) with:

```lua
vim.lsp.inlay_hint.enable(not vim.lsp.inlay_hint.is_enabled())
```

Kickstart.nvim maps this to `<leader>th`.

## Diagnostics

Neovim displays diagnostics (errors, warnings) from LSP and other sources.

### Configuration

```lua
vim.diagnostic.config({
  severity_sort = true,
  float = { border = 'rounded', source = true },
  underline = { severity = vim.diagnostic.severity.ERROR },
  signs = {
    text = {
      [vim.diagnostic.severity.ERROR] = '󰅚 ',
      [vim.diagnostic.severity.WARN] = '󰀪 ',
      [vim.diagnostic.severity.INFO] = '󰋽 ',
      [vim.diagnostic.severity.HINT] = '󰌶 ',
    },
  },
  virtual_text = {
    source = true,
    prefix = '●',
  },
})
```

### Diagnostic Functions

| Function | Description |
|----------|-------------|
| `vim.diagnostic.open_float()` | Show diagnostic in floating window |
| `vim.diagnostic.setloclist()` | Send diagnostics to location list |
| `vim.diagnostic.setqflist()` | Send diagnostics to quickfix list |
| `vim.diagnostic.get(bufnr)` | Get diagnostics for a buffer |
| `vim.diagnostic.enable(enable, filter)` | Enable/disable diagnostics |

### Default LSP and Diagnostic Keymaps

Neovim 0.12 sets these without any config. Kickstart.nvim replaces some with Telescope pickers (see `neovim-keybindings.md`).

| Mapping | Action |
|---------|--------|
| `grn` | Rename symbol |
| `gra` | Code action (normal and visual mode) |
| `grr` | List references |
| `gri` | Go to implementation |
| `grt` | Go to type definition |
| `grx` | Run code lens |
| `gO` | Document symbols |
| `<C-s>` (insert mode) | Signature help |
| `[d` / `]d` | Previous / next diagnostic |
| `[D` / `]D` | First / last diagnostic in the buffer |
| `<C-w>d` | Open diagnostic float |

## Blink.cmp -- Completion

Kickstart.nvim uses `saghen/blink.cmp` for auto-completion.

### Configuration in Kickstart

```lua
{
  'saghen/blink.cmp',
  version = '1.*',
  dependencies = { 'L3MON4D3/LuaSnip', version = 'v2.*' },
  opts = {
    keymap = { preset = 'default' },
    appearance = {
      nerd_font_variant = 'mono',
    },
    completion = {
      documentation = { auto_show = false, auto_show_delay_ms = 500 },
    },
    sources = {
      default = { 'lsp', 'path', 'snippets', 'buffer' },
    },
    snippets = { preset = 'luasnip' },
    signature = { enabled = true },
  },
}
```

### Default Keymaps (blink.cmp default preset)

| Key | Action |
|-----|--------|
| `<C-space>` | Show completion / toggle documentation |
| `<C-y>` | Accept completion |
| `<C-e>` | Cancel completion |
| `<C-p>` / `<C-n>` (or `<Up>` / `<Down>`) | Previous / next item |
| `<C-b>` / `<C-f>` | Scroll docs up / down |
| `<Tab>` / `<S-Tab>` | Next / previous snippet placeholder |
| `<C-k>` | Toggle signature help |

### Adding Completion Sources

```lua
-- In the blink.cmp opts:
sources = {
  default = { 'lsp', 'path', 'snippets', 'buffer' },
  providers = {
    buffer = {
      name = 'Buffer',
      module = 'blink.cmp.sources.buffer',
      score_offset = -3,  -- lower priority
    },
  },
},
```

## Conform.nvim -- Formatting

Conform.nvim provides a formatting layer independent of LSP:

### Configuration in Kickstart

```lua
{
  'stevearc/conform.nvim',
  event = { 'BufWritePre' },
  cmd = { 'ConformInfo' },
  keys = {
    { '<leader>f', function()
      require('conform').format({ async = true, lsp_format = 'fallback' })
    end, desc = '[F]ormat buffer' },
  },
  opts = {
    notify_on_error = false,
    format_on_save = function(bufnr)
      local disable_filetypes = { c = true, cpp = true }
      if disable_filetypes[vim.bo[bufnr].filetype] then
        return nil
      end
      return { timeout_ms = 500, lsp_format = 'fallback' }
    end,
    formatters_by_ft = {
      lua = { 'stylua' },
    },
  },
}
```

### Adding Formatters

Add entries to `formatters_by_ft`:

```lua
formatters_by_ft = {
  lua = { 'stylua' },
  python = { 'black' },
  javascript = { 'prettier' },
  typescript = { 'prettier' },
  json = { 'prettier' },
  yaml = { 'prettier' },
  markdown = { 'prettier' },
  sh = { 'shfmt' },
  go = { 'gofmt' },
  rust = { 'rustfmt' },
  -- Run multiple formatters sequentially
  css = { 'stylelint', 'prettier' },
}
```

### Disabling Format-on-Save

```lua
-- Per filetype (in format_on_save function)
local disable_filetypes = { c = true, cpp = true, java = true }

-- Globally: set format_on_save = false in opts
```

### Manual Formatting

```lua
-- Format current buffer
require('conform').format({ async = true, lsp_format = 'fallback' })

-- Format a range (visual selection)
require('conform').format({ async = true, range = { start, end_ } })
```

### Checking Formatter Status

```vim
:ConformInfo    " Show active formatters for current buffer
```

## LSP Troubleshooting

| Command | Purpose |
|---------|---------|
| `:checkhealth vim.lsp` | Active clients, enabled configs, and the log file's location |
| `:LspInfo` | Alias for `:checkhealth vim.lsp` (nvim-lspconfig) |
| `:LspLog` | Open the LSP log file (nvim-lspconfig) |
| `:lsp restart` | Restart language servers (built in; nvim-lspconfig also has `:LspRestart`) |
| `:Mason` | Open Mason UI to manage installations |
| `:MasonLog` | Open Mason log |

### Common Issues

- **Server not starting**: Check `:checkhealth vim.lsp`, `:LspLog`, and `:Mason` to verify installation
- **No completions**: Verify blink.cmp is loaded (`:Lazy check blink.cmp`) and server supports completion
- **Formatting not working**: Run `:ConformInfo` to see which formatter is active
- **Slow diagnostics**: Increase `updatetime` or configure `vim.diagnostic.config()` to reduce visual noise

## See Also

- `neovim-overview.md` -- autocommands (LspAttach), configuration basics
- `neovim-lua-api.md` -- vim.api functions used in LSP setup
- `neovim-keybindings.md` -- LSP keymaps, which-key groups
- `neovim-plugins.md` -- Mason, Telescope (used for LSP pickers), plugin management
