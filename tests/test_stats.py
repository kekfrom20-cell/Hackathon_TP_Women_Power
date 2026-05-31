import json

import pytest

from src.stats import Statistics


@pytest.fixture
def stats():
    return Statistics()


def test_statistics_initial_state(stats):
    result = stats.to_dict()

    assert result["total"] == 0
    assert result["categories"] == {}
    assert result["priorities"]["high"] == 0
    assert result["priorities"]["normal"] == 0


@pytest.mark.parametrize(
    "category, priority",
    [
        ("access", "high"),
        ("hardware", "normal"),
        ("spam", "normal"),
        ("unclassified", "normal"),
        ("corrupted", "normal"),
    ],
)
def test_add_one_email(stats, category, priority):
    stats.add_email(category, priority)

    result = stats.to_dict()

    assert result["total"] == 1
    assert result["categories"][category] == 1
    assert result["priorities"][priority] == 1


def test_add_several_emails_to_one_category(stats):
    stats.add_email("access", "normal")
    stats.add_email("access", "normal")
    stats.add_email("access", "high")

    result = stats.to_dict()

    assert result["total"] == 3
    assert result["categories"]["access"] == 3
    assert result["priorities"]["normal"] == 2
    assert result["priorities"]["high"] == 1


def test_add_emails_to_different_categories(stats):
    stats.add_email("access", "normal")
    stats.add_email("hardware", "normal")
    stats.add_email("spam", "high")

    result = stats.to_dict()

    assert result["total"] == 3
    assert result["categories"]["access"] == 1
    assert result["categories"]["hardware"] == 1
    assert result["categories"]["spam"] == 1
    assert result["priorities"]["normal"] == 2
    assert result["priorities"]["high"] == 1


def test_add_email_without_priority(stats):
    stats.add_email("documents")

    result = stats.to_dict()

    assert result["total"] == 1
    assert result["categories"]["documents"] == 1
    assert result["priorities"]["normal"] == 1


def test_add_new_priority(stats):
    stats.add_email("incidents", "medium")

    result = stats.to_dict()

    assert result["total"] == 1
    assert result["categories"]["incidents"] == 1
    assert result["priorities"]["medium"] == 1


def test_to_dict_has_correct_structure(stats):
    result = stats.to_dict()

    assert "total" in result
    assert "categories" in result
    assert "priorities" in result


def test_save_statistics_to_json_file(tmp_path, stats):
    stats.add_email("access", "high")
    stats.add_email("spam", "normal")

    stats_file = tmp_path / "stats.json"

    stats.save(str(stats_file))

    assert stats_file.exists()

    with open(stats_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    assert data["total"] == 2
    assert data["categories"]["access"] == 1
    assert data["categories"]["spam"] == 1
    assert data["priorities"]["high"] == 1
    assert data["priorities"]["normal"] == 1