import argparse

from src.processor import MailProcessor


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Corporate mail sorting system"
    )

    parser.add_argument(
        "--inbox",
        default="inbox",
        help="Path to folder with incoming emails",
    )

    parser.add_argument(
        "--output",
        default="processed",
        help="Path to folder for sorted emails",
    )

    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy files instead of moving them",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Classify emails without moving files",
    )

    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Do not generate HTML report",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    processor = MailProcessor(
        inbox_path=args.inbox,
        processed_path=args.output,
        copy_files=args.copy,
        dry_run=args.dry_run,
    )

    stats = processor.process_all()

    print("Processing completed.")
    print(f"Total emails: {stats['total']}")

    print()
    print("Categories:")

    for category, count in stats["categories"].items():
        print(f"{category}: {count}")

    print()
    print("Priorities:")

    for priority, count in stats["priorities"].items():
        print(f"{priority}: {count}")


if __name__ == "__main__":
    main()