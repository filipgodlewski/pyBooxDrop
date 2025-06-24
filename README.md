# 📖 pyBooxDrop

![CI](https://github.com/filipgodlewski/pyBooxDrop/actions/workflows/ci.yml/badge.svg)
[![PyPI version](https://img.shields.io/pypi/v/booxdrop.svg)](https://pypi.org/project/booxdrop/)
[![Python Version](https://img.shields.io/pypi/pyversions/booxdrop.svg)](https://pypi.org/project/booxdrop/)
[![License](https://img.shields.io/pypi/l/booxdrop.svg)](https://github.com/filipgodlewski/pyBooxDrop/blob/main/LICENSE)

🐍 A friendly Python wrapper for the BOOXDrop API — unofficial, but built with care.
📚 Great if you want to manage files on your BOOX device programmatically,
automate uploads/downloads, or plug it into your own tools and scripts.

---

## ✨ Features

- Clean and consistent API client for BOOXDrop
- Fully typed (with `pydantic`) and 100% modern Python 3.12+
- Open-source, MIT-licensed, built with readability in mind

---

## 📦 Installation

```bash
pip install pybooxdrop
```

---

## 🚀 Quickstart

```python
from boox.client import BooxClient

# Given it is the very first connection, and no token is available:
client = BooxClient(url="eur.boox.com")
payload = {"mobi": "foo@bar.com"}
_ = client.users.send_verification_code(payload=payload)
```

---

## 🧪 Testing

TODO: add description

---

## 📮 Feedback

Got ideas, feedback, or feature requests? Feel free to open an issue or pull request!

---

## 👷 Contributing

Contributions are welcome!

- Please fork the repository and create a branch for your feature or bugfix.
- Use pytest to run tests and add new tests when applicable.
- Follow the existing code style, checked by ruff, bandit and pyupgrade.
- Open a pull request with a clear description of your changes.

---

## 🫶 Special thanks

Big thanks to [hrw](https://github.com/hrw)
for the project [onyx-send2boox](https://github.com/hrw/onyx-send2boox).
The project was the main inspiration behind this library.
While pyBooxDrop is a fresh, focused take on just the API,
this project wouldn’t exist without this awesome groundwork.

Thanks for the great job!

---

## 🪪 License

MIT – use it, hack it, ship it.
