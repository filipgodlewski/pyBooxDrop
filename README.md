# 📖 pyBooxDrop

![CI](https://github.com/filipgodlewski/pyBooxDrop/actions/workflows/ci.yml/badge.svg)
[![PyPI version](https://img.shields.io/pypi/v/booxdrop.svg)](https://pypi.org/project/booxdrop/)
[![Python Version](https://img.shields.io/pypi/pyversions/booxdrop.svg)](https://pypi.org/project/booxdrop/)
[![License](https://img.shields.io/pypi/l/booxdrop.svg)](https://github.com/filipgodlewski/pyBooxDrop/blob/main/LICENSE)

<div>
🐍 A friendly Python wrapper for the BOOXDrop API — unofficial, but built with care.
<br>
📚 Great if you want to manage files on your BOOX device programmatically, automate uploads/downloads,
or plug it into your own tools and scripts.
</div>

---

## ✨ Features

- Clean and consistent API client for BOOXDrop
- Fully typed (with `pydantic`) and 100% modern Python 3.12+
- No external HTTP dependency — bring your own client, if you will
- HTTP client agnostic – plug in your own via simple `HttpClient` interface
- Open-source, MIT-licensed, built with readability in mind

<details>

  <summary>Supported endpoints</summary>

```http
POST /users/sendVerifyCode
```

</details>

---

## 📦 Installation

```bash
pip install pybooxdrop
```

---

## 🚀 Quick start

```python
from boox import Boox

# Given it is the very first connection, and no token is available:
with Boox(base_url="eur.boox.com") as client:
    payload = {"mobi": "foo@bar.com"}
    _ = client.users.send_verification_code(payload=payload)

# OR, if you don't want to use the context manager

client = Boox(base_url="eur.boox.com")
payload = {"mobi": "foo@bar.com"}
_ = client.users.send_verification_code(payload=payload)
client.close()
```

---

## 🔌 Custom HTTP client support

Boox lets you plug in your own HTTP client.
To do this, implement a simple `HttpClient` protocol with the required methods and pass your adapter to `Boox`.

<details>
<summary>Example</summary>

```python
import httpx
from boox import Boox, HttpClient

class MyAdapter(HttpClient):
    def post(self, url: str, json: dict | None = None) -> Any:
        # your logic using requests, httpx, or anything else
        ...

with Boox(client=MyAdapter(httpx.Client())) as boox: ...
```

</details>

Why?
This gives you full control over things like:

- ⏰ timeouts
- ♻️ retries
- 🧾 logging
- 🌍 proxies or custom headers
- 🔐 session/cookie handling

> By design, Boox does **not** depend on any specific HTTP library.
> It only uses Python’s built-in `urllib` by default — you're free to use
> [`requests`](https://docs.python-requests.org/), [`httpx`](https://www.python-httpx.org/), or your own logic.

---

## 🧪 Testing

### Running unit tests

```bash
# to run all but e2e tests do the following:
uv sync
uv run pytest
```

Alternatively, use:

```bash
make test
```

### Running E2E tests

Please note that since the E2E tests are heavy, require real internet connection,
and they connect with the real BOOXDrop server, it is not recommended to run them often.

```bash
# required environment variables:
# E2E_SMTP_EMAIL - the e-mail address on smtp.dev
# E2E_SMTP_X_API_KEY - the X-API-KEY for the account
# E2E_TARGET_DOMAIN - the target BOOXDrop domain, e.g. push.boox.com
uv sync
uv run pytest -m e2e --e2e
```

Alternatively, use:

```bash
make e2e
```

- `E2E_SMTP_EMAIL` must lead to an e-mail that is connected to a real Boox account. It must be verified prior to the tests.
- `E2E_TARGET_DOMAIN` is the domain that the Boox account is used with.
  AFAIK it can be any Boox' domain, because the account is not bound to any in particular.
  This might change in the future though, so I would rather play safe there.
- `X-API-KEY` for [SMTP.dev](https://smtp.dev/) is required, as this is the client that is being used.
  Currently there are no plans to support other providers.

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

Big thanks to [hrw](https://github.com/hrw) for the project [onyx-send2boox](https://github.com/hrw/onyx-send2boox).
The project was the main inspiration behind this library.
While pyBooxDrop is a fresh, focused take on just the API, this project wouldn’t exist without this awesome groundwork.

Thanks for the great job!

---

## 🪪 License

MIT – use it, hack it, ship it.
