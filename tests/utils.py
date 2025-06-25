import os


class EmailProvider:
    def __init__(self) -> None:
        self.address = os.environ["SMTP_EMAIL"]
        self.password = os.environ["SMTP_PASSWORD"]
        self.host = os.environ["SMTP_HOST"]
