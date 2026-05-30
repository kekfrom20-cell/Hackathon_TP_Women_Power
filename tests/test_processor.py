import json
import os
import pytest
from src.processor import MailProcessor


@pytest.fixture
def processor(tmp_path):
    inbox = tmp_path / "inbox"
    processed = tmp_path / "processed"
    logs = tmp_path / "logs"
    stats_path = tmp_path / "stats.json"
    inbox.mkdir()
    return MailProcessor(
        inbox_path=str(inbox),
        processed_path=str(processed),
        log_path=str(logs / "result.log"),
        stats_path=str(stats_path),
    )

def test_get_categories_contains_extra_categories(processor):
    categories = processor.get_categories()

    assert "unclassified" in categories
    assert "corrupted" in categories
    assert "access" in categories
    assert "spam" in categories


def test_process_one_file_moves_file_to_right_category(processor):
    file_path = os.path.join(processor.inbox_path, "mail.txt")

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(
            "From: user@mail.ru\n"
            "Subject: Запрос доступа к VPN\n"
            "\n"
            "Нужен доступ к VPN."
        )
    processor.file_manager.create_folders(processor.get_categories())
    processor.process_one_file(file_path)
    new_path = os.path.join(
        processor.processed_path,
        "access",
        "mail.txt",
    )
    assert os.path.exists(new_path)
    assert not os.path.exists(file_path)

def test_process_one_file_writes_log(processor):
    file_path = os.path.join(processor.inbox_path, "mail.txt")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(
            "From: user@mail.ru\n"
            "Subject: Проблема с принтером\n"
            "\n"
            "Принтер не печатает."
        )
    processor.file_manager.create_folders(processor.get_categories())
    processor.process_one_file(file_path)
    with open(processor.log_path, "r", encoding="utf-8") as log_file:
        log_text = log_file.read()
    assert "mail.txt" in log_text
    assert "hardware" in log_text

def test_process_one_file_updates_statistics(processor):
    file_path = os.path.join(processor.inbox_path, "mail.txt")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(
            "From: user@mail.ru\n"
            "Subject: Вы выиграли подарок\n"
            "\n"
            "Перейдите по ссылке."
        )
    processor.file_manager.create_folders(processor.get_categories())
    processor.process_one_file(file_path)
    stats = processor.statistics.to_dict()
    assert stats["total"] == 1
    assert stats["categories"]["spam"] == 1

def test_process_corrupted_file(processor):
    file_path = os.path.join(processor.inbox_path, "bad.txt")
    with open(file_path, "wb") as file:
        file.write(b"hello\x00world")
    processor.file_manager.create_folders(processor.get_categories())
    processor.process_one_file(file_path)
    new_path = os.path.join(
        processor.processed_path,
        "corrupted",
        "bad.txt",
    )
    assert os.path.exists(new_path)
    stats = processor.statistics.to_dict()
    assert stats["categories"]["corrupted"] == 1

def test_process_unknown_format_as_corrupted(processor):
    file_path = os.path.join(processor.inbox_path, "image.jpeg")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("fake image")
    processor.file_manager.create_folders(processor.get_categories())
    processor.process_one_file(file_path)
    new_path = os.path.join(
        processor.processed_path,
        "corrupted",
        "image.jpeg",
    )
    assert os.path.exists(new_path)

def test_process_all_saves_stats_file(processor):
    file_path = os.path.join(processor.inbox_path, "mail.txt")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(
            "From: user@mail.ru\n"
            "Subject: Ошибка в Excel\n"
            "\n"
            "Excel зависает после обновления."
        )
    stats = processor.process_all()
    assert stats["total"] == 1
    assert stats["categories"]["software"] == 1
    assert os.path.exists(processor.stats_path)
    with open(processor.stats_path, "r", encoding="utf-8") as file:
        saved_stats = json.load(file)
    assert saved_stats["total"] == 1
    assert saved_stats["categories"]["software"] == 1

def test_copy_files_mode_keeps_original_file(tmp_path):
    inbox = tmp_path / "inbox"
    processed = tmp_path / "processed"
    logs = tmp_path / "logs"
    stats_path = tmp_path / "stats.json"
    inbox.mkdir()
    processor = MailProcessor(
        inbox_path=str(inbox),
        processed_path=str(processed),
        log_path=str(logs / "result.log"),
        stats_path=str(stats_path),
        copy_files=True,
    )
    file_path = inbox / "mail.txt"
    file_path.write_text(
        "From: user@mail.ru\n"
        "Subject: Больничный лист\n"
        "\n"
        "Отправляю больничный.",
        encoding="utf-8",
    )
    processor.process_all()
    original_path = inbox / "mail.txt"
    copied_path = processed / "hr" / "mail.txt"
    assert original_path.exists()
    assert copied_path.exists()