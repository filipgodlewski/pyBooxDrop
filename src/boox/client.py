class Client:
    def __init__(self, token: str):
        self.token = token

    def authorize(self):
        return self.token
