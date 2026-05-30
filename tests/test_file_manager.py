import os
import pytest

from src.file_manager import FileManager


@pytest.fixture
def manager(tmp_path):
    return FileManager(
        inbox_path=str(tmp_path / "inbox"),
        processed_path=str(tmp_path / "processed"),
        log_path=str(tmp_path / "logs" / "app.log")
    )


@pytest.mark.parametrize(
    "categories",
    [
        ["work"],
        ["work", "spam"],
        ["work", "spam", "other"]
    ]
)
def test_create_folders(manager, categories):
    manager.create_folders(categories)

    assert os.path.exists(manager.inbox_path)
    assert os.path.exists(manager.processed_path)

    for category in categories:
        assert os.path.exists(
            os.path.join(manager.processed_path, category)
        )


def test_create_folders_empty_categories(manager):
    manager.create_folders([])

    assert os.path.exists(manager.inbox_path)
    assert os.path.exists(manager.processed_path)


def test_write_log(manager):
    os.makedirs(
        os.path.dirname(manager.log_path),
        exist_ok=True
    )

    manager.write_log("Test message")

    with open(manager.log_path, encoding="utf-8") as file:
        content = file.read()

    assert "Test message" in content


def test_get_unique_path_when_file_does_not_exist(manager, tmp_path):
    file_path = tmp_path / "mail.txt"

    result = manager.get_unique_path(str(file_path))

    assert result == str(file_path)


def test_get_unique_path_when_file_exists(manager, tmp_path):
    file_path = tmp_path / "mail.txt"
    file_path.write_text("test")

    result = manager.get_unique_path(str(file_path))

    assert result.endswith("mail_1.txt")


def test_get_unique_path_multiple_existing_files(manager, tmp_path):
    (tmp_path / "mail.txt").write_text("1")
    (tmp_path / "mail_1.txt").write_text("1")
    (tmp_path / "mail_2.txt").write_text("1")

    result = manager.get_unique_path(
        str(tmp_path / "mail.txt")
    )

    assert result.endswith("mail_3.txt")


def test_copy_file(tmp_path):
    inbox = tmp_path / "inbox"
    processed = tmp_path / "processed"

    inbox.mkdir()
    processed.mkdir()

    source_file = inbox / "mail.txt"
    source_file.write_text("hello")

    manager = FileManager(
        str(inbox),
        str(processed),
        str(tmp_path / "log.txt"),
        copy_files=True
    )

    manager.move_or_copy_file(str(source_file), "work")

    copied_file = processed / "work" / "mail.txt"

    assert copied_file.exists()
    assert source_file.exists()


def test_move_file(tmp_path):
    inbox = tmp_path / "inbox"
    processed = tmp_path / "processed"

    inbox.mkdir()
    processed.mkdir()

    source_file = inbox / "mail.txt"
    source_file.write_text("hello")

    manager = FileManager(
        str(inbox),
        str(processed),
        str(tmp_path / "log.txt"),
        copy_files=False
    )

    manager.move_or_copy_file(str(source_file), "work")

    moved_file = processed / "work" / "mail.txt"

    assert moved_file.exists()
    assert not source_file.exists()


def test_move_file_with_existing_name(tmp_path):
    inbox = tmp_path / "inbox"
    processed = tmp_path / "processed"

    inbox.mkdir()
    processed.mkdir()

    source_file = inbox / "mail.txt"
    source_file.write_text("new file")

    target_folder = processed / "work"
    target_folder.mkdir()

    existing_file = target_folder / "mail.txt"
    existing_file.write_text("old file")

    manager = FileManager(
        str(inbox),
        str(processed),
        str(tmp_path / "log.txt")
    )

    manager.move_or_copy_file(str(source_file), "work")

    assert (target_folder / "mail.txt").exists()
    assert (target_folder / "mail_1.txt").exists()


def test_dry_run_does_not_move_file(tmp_path):
    inbox = tmp_path / "inbox"
    processed = tmp_path / "processed"

    inbox.mkdir()
    processed.mkdir()

    source_file = inbox / "mail.txt"
    source_file.write_text("hello")

    manager = FileManager(
        str(inbox),
        str(processed),
        str(tmp_path / "log.txt"),
        dry_run=True
    )

    manager.move_or_copy_file(str(source_file), "work")

    assert source_file.exists()

    assert not (
        processed / "work" / "mail.txt"
    ).exists()