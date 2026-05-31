import pytest

from src.mail import Mail
from src.classifier import MailClassifier, CATEGORY_KEYWORDS


@pytest.fixture
def classifier():
    return MailClassifier()


def make_mail(subject="", body=""):
    return Mail(
        filename="test.txt",
        subject=subject,
        sender="user@example.com",
        body=body,
    )


@pytest.mark.parametrize(
    "subject, body, expected",
    [
        (
            "Критический инцидент",
            "Сервер недоступен, работа остановлена",
            "incidents",
        ),
        (
            "Запрос доступа",
            "Нужны права для VPN",
            "access",
        ),
        (
            "Проблема с принтером",
            "Принтер не печатает документы",
            "hardware",
        ),
        (
            "Ошибка в Excel",
            "Excel зависает после обновления",
            "software",
        ),
        (
            "[WARNING] Disk usage",
            "Disk usage is too high",
            "monitoring",
        ),
        (
            "Счет на оплату",
            "Отправляем договор и акт",
            "documents",
        ),
        (
            "Больничный",
            "Сотрудник отправил больничный",
            "hr",
        ),
        (
            "Жалоба клиента",
            "Клиент не может подключиться к API",
            "external",
        ),
        (
            "Дайджест",
            "Новости и статус задач за неделю",
            "info",
        ),
        (
            "Вы выиграли подарок",
            "Перейдите по ссылке и подтвердите личность",
            "spam",
        ),
    ],
)
def test_classify_all_main_categories(classifier, subject, body, expected):
    mail = make_mail(subject=subject, body=body)

    result = classifier.classify(mail)

    assert result == expected


def test_unclassified_email(classifier):
    mail = make_mail(
        subject="Обычный вопрос",
        body="Добрый день, хочу уточнить информацию",
    )

    result = classifier.classify(mail)

    assert result == "unclassified"


def test_empty_email(classifier):
    mail = make_mail(
        subject="",
        body="",
    )

    result = classifier.classify(mail)

    assert result == "unclassified"


def test_subject_has_more_weight_than_body(classifier):
    mail = make_mail(
        subject="Запрос доступа",
        body="Также в письме есть слово договор",
    )

    result = classifier.classify(mail)

    assert result == "access"


def test_body_keywords_are_used(classifier):
    mail = make_mail(
        subject="Проблема",
        body="Не открывается Outlook после обновления",
    )

    result = classifier.classify(mail)

    assert result == "software"


def test_classifier_ignores_letter_case(classifier):
    mail = make_mail(
        subject="VPN",
        body="НЕТ ДОСТУПА к корпоративному порталу",
    )

    result = classifier.classify(mail)

    assert result == "access"


@pytest.mark.parametrize(
    "subject, body",
    [
        ("Срочно нужен доступ", "Не могу зайти в VPN"),
        ("Urgent incident", "Server is not responding"),
        ("ASAP", "Нужна помощь с доступом"),
    ],
)
def test_high_priority(classifier, subject, body):
    mail = make_mail(subject=subject, body=body)

    result = classifier.define_priority(mail)

    assert result == "high"


def test_normal_priority(classifier):
    mail = make_mail(
        subject="Вопрос по документу",
        body="Посмотрите, пожалуйста, договор",
    )

    result = classifier.define_priority(mail)

    assert result == "normal"


def test_spam_wins_if_scores_are_equal(classifier):
    mail = make_mail(
        subject="",
        body="critical offer",
    )

    result = classifier.classify(mail)

    assert result == "spam"


def test_all_categories_have_keywords():
    for category, keywords in CATEGORY_KEYWORDS.items():
        assert len(keywords) > 0