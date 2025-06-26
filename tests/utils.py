import os


class EmailProvider:
    def __init__(self) -> None:
        self.address = os.environ["E2E_SMTP_EMAIL"]
        self.x_api_key = os.environ["E2E_SMTP_X_API_KEY"]
