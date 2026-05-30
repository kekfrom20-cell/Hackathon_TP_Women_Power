import json


class Statistics:
    def __init__(self):
        self.categories = {}
        self.priorities = {
            "high": 0,
            "normal": 0,
        }
        self.total = 0

    def add_email(self, category: str, priority: str = "normal"):
        self.total += 1

        if category not in self.categories:
            self.categories[category] = 0

        self.categories[category] += 1

        if priority not in self.priorities:
            self.priorities[priority] = 0

        self.priorities[priority] += 1

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "categories": self.categories,
            "priorities": self.priorities,
        }

    def save(self, path: str):
        with open(path, "w", encoding="utf-8") as file:
            json.dump(
                self.to_dict(),
                file,
                ensure_ascii=False,
                indent=4,
            )