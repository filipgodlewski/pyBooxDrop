return {
  {
    "stevearc/conform.nvim",
    optional = true,
    opts = {
      formatters = {
        pyupgrade = {
          prepend_args = "--py312-plus",
        },
      },
    },
  },
}
