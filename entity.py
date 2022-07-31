import json


class Problem:
    def __init__(self, success: int, fail: int, name: str = "Problem"):
        self.success = success
        self.fail = fail
        self.name = name
