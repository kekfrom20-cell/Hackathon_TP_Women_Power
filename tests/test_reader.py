import pytest

from src.reader import MailReader

@pytest.fixture
def reader():
    return MailReader()

def test_read_txt_mail(reader, tmp_path):
    file_path = tmp_path / "mail.txt"
    file_path.write_text(
        "From: masha@mail.ru\n"
        "To: support@mail.ru\n"
        "Subject: Test subject\n"
        "\n"
        "Hello world!",
        encoding="utf-8",
    )
    mail = reader.read(str(file_path))
    assert mail.filename == "mail.txt"
    assert mail.sender == "masha@mail.ru"
    assert mail.subject == "Test subject"
    assert mail.body == "Hello world!"

def test_read_json_mail(reader, tmp_path):
    file_path = tmp_path / "mail.json"
    file_path.write_text(
        '{"from": "masha@mail.ru", "subject": "VPN access", "body": "Need VPN access"}',
        encoding="utf-8",
    )
    mail = reader.read(str(file_path))
    assert mail.filename == "mail.json"
    assert mail.sender == "masha@mail.ru"
    assert mail.subject == "VPN access"
    assert mail.body == "Need VPN access"

def test_read_json_with_sender_field(reader, tmp_path):
    file_path = tmp_path / "mail.json"
    file_path.write_text(
        '{"sender": "user@mail.ru", "subject": "Hello", "text": "Message text"}',
        encoding="utf-8",
    )
    mail = reader.read(str(file_path))
    assert mail.sender == "user@mail.ru"
    assert mail.subject == "Hello"
    assert mail.body == "Message text"

def test_unsupported_file_format(reader, tmp_path):
    file_path = tmp_path / "image.jpeg"
    file_path.write_text("fake image", encoding="utf-8")
    with pytest.raises(ValueError):
        reader.read(str(file_path))

def test_invalid_json(reader, tmp_path):
    file_path = tmp_path / "broken.json"
    file_path.write_text('{"from": "masha@mail.ru", "subject": ', encoding="utf-8")
    with pytest.raises(ValueError):
        reader.read(str(file_path))

def test_binary_file(reader, tmp_path):
    file_path = tmp_path / "bad.txt"
    file_path.write_bytes(b"hello\x00world")

    with pytest.raises(ValueError):
        reader.read(str(file_path))

def test_empty_file(reader, tmp_path):
    file_path = tmp_path / "empty.txt"
    file_path.write_text("", encoding="utf-8")
    mail = reader.read(str(file_path))
    assert mail.filename == "empty.txt"
    assert mail.subject == ""
    assert mail.sender == ""
    assert mail.body == ""

def test_file_without_extension(reader, tmp_path):
    file_path = tmp_path / "mail"
    file_path.write_text(
        "From: user@mail.ru\n"
        "Subject: No extension\n"
        "\n"
        "Body text",
        encoding="utf-8",
    )
    mail = reader.read(str(file_path))
    assert mail.filename == "mail"
    assert mail.sender == "user@mail.ru"
    assert mail.subject == "No extension"
    assert mail.body == "Body text"

def test_parse_text_without_headers(reader, tmp_path):
    file_path = tmp_path / "simple.txt"
    file_path.write_text("Text without headers", encoding="utf-8")
    mail = reader.read(str(file_path))
    assert mail.filename == "simple.txt"
    assert mail.subject == ""
    assert mail.sender == ""
    assert mail.body == "Text without headers"