return {
  {
    "stevearc/conform.nvim",
    optional = true,
    opts = function(_, opts)
      table.insert(opts.formatters.pyupgrade.args, 1, "--py312-plus")
      opts.formatters_by_ft.python = { "pyupgrade", "ruff_fix", "ruff_format" }
    end,
  },
}
