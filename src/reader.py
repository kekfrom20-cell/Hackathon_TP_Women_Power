import json
from pathlib import Path
from src.mail import Mail


class MailReader:
    def __init__(self):
        self.allowed_extensions = [".txt", ".eml", ".json", ""]

    def read(self, file_path: str) -> Mail:
        path = Path(file_path)
        if path.suffix.lower() not in self.allowed_extensions:
            raise ValueError(f"Unsupported file format: {path.suffix}")
        text = self._read_text(path)
        if path.suffix.lower() == ".json":
            return self._parse_json(path.name, text)
        return self._parse_text(path.name, text)

    def _read_text(self, path: Path) -> str:
        raw_data = path.read_bytes()
        if b"\x00" in raw_data:
            raise ValueError("File looks like binary or corrupted")

        for encoding in ["utf-8", "cp1251", "latin-1"]:
            try:
                return raw_data.decode(encoding)
            except UnicodeDecodeError:
                continue
        raise ValueError("Cannot decode file")

    def _parse_json(self, filename: str, text: str) -> Mail:
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON file")
        return Mail(
            filename=filename,
            subject=str(data.get("subject", "")),
            sender=str(data.get("from", data.get("sender", ""))),
            body=str(data.get("body", data.get("text", ""))),
        )

    def _parse_text(self, filename: str, text: str) -> Mail:
        lines = text.splitlines()
        subject = ""
        sender = ""
        body_lines = []
        reading_headers = True
        for line in lines:
            stripped_line = line.strip()
            lower_line = stripped_line.lower()
            if reading_headers and stripped_line == "":
                reading_headers = False
                continue
            if reading_headers and lower_line.startswith("subject:"):
                subject = stripped_line.split(":", 1)[1].strip()
                continue
            if reading_headers and lower_line.startswith("from:"):
                sender = stripped_line.split(":", 1)[1].strip()
                continue
            if reading_headers and lower_line.startswith(("to:", "date:", "cc:")):
                continue
            reading_headers = False
            body_lines.append(line)
        body = "\n".join(body_lines).strip()
        if not subject and not body:
            body = text.strip()
        return Mail(
            filename = filename,
            subject = subject,
            sender = sender,
            body = body,
        )