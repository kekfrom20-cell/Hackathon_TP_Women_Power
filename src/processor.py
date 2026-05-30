import os

from src.classifier import MailClassifier, CATEGORY_KEYWORDS
from src.file_manager import FileManager
from src.reader import MailReader
from src.report import ReportGenerator
from src.stats import Statistics


class MailProcessor:
    def __init__(
        self,
        inbox_path="inbox",
        processed_path="processed",
        log_path="logs/result.log",
        stats_path="stats.json",
        report_path="report.html",
        copy_files=False,
        dry_run=False,
        make_report=True,
    ):
        self.inbox_path = inbox_path
        self.processed_path = processed_path
        self.log_path = log_path
        self.stats_path = stats_path
        self.report_path = report_path
        self.make_report = make_report

        self.reader = MailReader()
        self.classifier = MailClassifier()
        self.statistics = Statistics()
        self.report_generator = ReportGenerator()

        self.file_manager = FileManager(
            inbox_path=self.inbox_path,
            processed_path=self.processed_path,
            log_path=self.log_path,
            copy_files=copy_files,
            dry_run=dry_run,
        )

        self.processed_emails = []

    def get_categories(self):
        categories = list(CATEGORY_KEYWORDS.keys())
        categories.append("unclassified")
        categories.append("corrupted")
        return categories

    def save_result(self, filename, category, priority, status):
        self.statistics.add_email(category, priority)

        self.processed_emails.append(
            {
                "filename": filename,
                "category": category,
                "priority": priority,
                "status": status,
            }
        )

    def process_one_file(self, file_path):
        filename = os.path.basename(file_path)

        try:
            mail = self.reader.read(file_path)

            category = self.classifier.classify(mail)
            priority = self.classifier.define_priority(mail)

            self.file_manager.move_or_copy_file(file_path, category)

            self.save_result(
                filename=filename,
                category=category,
                priority=priority,
                status="processed",
            )

            self.file_manager.write_log(
                f"{filename} -> {category}, priority={priority}"
            )

        except Exception as error:
            category = "corrupted"
            priority = "normal"

            try:
                self.file_manager.move_or_copy_file(file_path, category)
            except Exception as move_error:
                self.file_manager.write_log(
                    f"{filename} -> corrupted, move error: {move_error}"
                )

            self.save_result(
                filename=filename,
                category=category,
                priority=priority,
                status=f"error: {error}",
            )

            self.file_manager.write_log(
                f"{filename} -> corrupted: {error}"
            )

    def process_all(self):
        categories = self.get_categories()
        self.file_manager.create_folders(categories)

        files = os.listdir(self.inbox_path)

        for filename in files:
            file_path = os.path.join(self.inbox_path, filename)

            if os.path.isfile(file_path):
                self.process_one_file(file_path)

        stats = self.statistics.to_dict()
        self.statistics.save(self.stats_path)

        if self.make_report:
            self.report_generator.generate(
                stats=stats,
                processed_emails=self.processed_emails,
                output_path=self.report_path,
            )

        return stats