from dataclasses import dataclass


@dataclass
class Mail:
    filename: str
    subject: str
    sender: str
    body: str

    def is_empty(self) -> bool:
        return len((self.subject + self.body).strip()) == 0

    def full_text(self) -> str:
        return f"{self.subject}\n{self.body}"