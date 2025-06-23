# 📖 pyBooxDrop

![CI](https://github.com/filipgodlewski/pyBooxDrop/actions/workflows/ci.yml/badge.svg)
[![PyPI version](https://img.shields.io/pypi/v/booxdrop.svg)](https://pypi.org/project/booxdrop/)
[![Python Version](https://img.shields.io/pypi/pyversions/booxdrop.svg)](https://pypi.org/project/booxdrop/)
[![License](https://img.shields.io/pypi/l/booxdrop.svg)](https://github.com/filipgodlewski/pyBooxDrop/blob/main/LICENSE)

A simple, unofficial Python API library for Onyx BooxDrop.
If you’re not a fan of the official app,
here’s a cleaner, modern, and easy-to-use alternative —
perfect for managing your books on your Boox device.

## Features

- Standardized and organized API client for BooxDrop
- Fully typed with `pydantic` and type hints
- Open source, modern Python 3.12+ support

## Requirements

- Python version >=3.12

## Installation

```bash
pip install pybooxdrop
```

## Usage

Basic example of using the library:

```python
# TODO: sample code
```

## Development

Please use `[astral-sh/uv](https://github.com/astral-sh/uv)` for your development.
Be aware that the CI lint job depends on the packages found in "lint" extra.

Sync uv with the following command:

```bash
uv sync
# OR
uv sync --extra lint
```

## Contributing

Contributions are welcome!

- Please fork the repository and create a branch for your feature or bugfix.
- Use pytest to run tests and add new tests when applicable.
- Follow the existing code style, checked by ruff and pyupgrade.
- Open a pull request with a clear description of your changes.

## Special thanks

Big thanks to [hrw](https://github.com/hrw)
and their project [onyx-send2boox](https://github.com/hrw/onyx-send2boox).
Their work was the main inspiration behind this tool.
While pyBooxDrop is a fresh, focused take on just the API,
this project wouldn’t exist without their awesome groundwork.

Thanks for the great job!
