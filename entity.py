import json


class Problem:
    def __init__(self, success: int, fail: int, onenote_url, name: str = "Problem"):
        self.success = success
        self.fail = fail
        self.name = name
        self.onenote_url = onenote_url
