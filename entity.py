import json


class Problem:
    def __init__(self, success: int, failed: int):
        self.success = success
        self.failed = failed
