from src.mail import Mail


def test_is_empty_when_subject_and_body_empty():
    mail = Mail(
        filename="test.txt",
        subject="",
        sender="user@test.com",
        body=""
    )

    assert mail.is_empty() is True


def test_is_empty_when_subject_and_body_contain_only_spaces():
    mail = Mail(
        filename="test.txt",
        subject="   ",
        sender="user@test.com",
        body="\n\t "
    )

    assert mail.is_empty() is True


def test_is_not_empty_when_subject_contains_text():
    mail = Mail(
        filename="test.txt",
        subject="Important message",
        sender="user@test.com",
        body=""
    )

    assert mail.is_empty() is False


def test_is_not_empty_when_body_contains_text():
    mail = Mail(
        filename="test.txt",
        subject="",
        sender="user@test.com",
        body="Hello"
    )

    assert mail.is_empty() is False


def test_full_text():
    mail = Mail(
        filename="test.txt",
        subject="Subject",
        sender="user@test.com",
        body="Message body"
    )

    assert mail.full_text() == "Subject\nMessage body"