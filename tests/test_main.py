import sys
from unittest.mock import Mock

import src.main as main_module


def test_parse_arguments_default_values(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py"])

    args = main_module.parse_arguments()

    assert args.inbox == "inbox"
    assert args.output == "processed"
    assert args.copy is False
    assert args.dry_run is False
    assert args.no_report is False


def test_parse_arguments_custom_values(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--inbox",
            "custom_inbox",
            "--output",
            "custom_output",
            "--copy",
            "--dry-run",
            "--no-report",
        ],
    )

    args = main_module.parse_arguments()

    assert args.inbox == "custom_inbox"
    assert args.output == "custom_output"
    assert args.copy is True
    assert args.dry_run is True
    assert args.no_report is True


def test_main_calls_processor_with_default_arguments(monkeypatch, capsys):
    mock_processor = Mock()
    mock_processor.process_all.return_value = {
        "total": 2,
        "categories": {
            "spam": 1,
            "documents": 1,
        },
        "priorities": {
            "high": 1,
            "normal": 1,
        },
    }

    mock_processor_class = Mock(return_value=mock_processor)

    monkeypatch.setattr(sys, "argv", ["main.py"])
    monkeypatch.setattr(main_module, "MailProcessor", mock_processor_class)

    main_module.main()

    mock_processor_class.assert_called_once_with(
        inbox_path="inbox",
        processed_path="processed",
        copy_files=False,
        dry_run=False,
        make_report=True,
    )

    mock_processor.process_all.assert_called_once()

    captured = capsys.readouterr()

    assert "Processing completed." in captured.out
    assert "Total emails: 2" in captured.out
    assert "spam: 1" in captured.out
    assert "documents: 1" in captured.out
    assert "high: 1" in captured.out
    assert "normal: 1" in captured.out


def test_main_calls_processor_with_custom_arguments(monkeypatch):
    mock_processor = Mock()
    mock_processor.process_all.return_value = {
        "total": 0,
        "categories": {},
        "priorities": {},
    }

    mock_processor_class = Mock(return_value=mock_processor)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--inbox",
            "test_inbox",
            "--output",
            "test_processed",
            "--copy",
            "--dry-run",
            "--no-report",
        ],
    )

    monkeypatch.setattr(main_module, "MailProcessor", mock_processor_class)

    main_module.main()

    mock_processor_class.assert_called_once_with(
        inbox_path="test_inbox",
        processed_path="test_processed",
        copy_files=True,
        dry_run=True,
        make_report=False,
    )

    mock_processor.process_all.assert_called_once()