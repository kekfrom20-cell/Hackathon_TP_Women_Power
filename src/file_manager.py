import os
import shutil


class FileManager:
    def __init__(self, inbox_path, processed_path, log_path, copy_files=False, dry_run=False):
        self.inbox_path = inbox_path
        self.processed_path = processed_path
        self.log_path = log_path
        self.copy_files = copy_files
        self.dry_run = dry_run

    def create_folders(self, categories):
        os.makedirs(self.inbox_path, exist_ok=True)
        os.makedirs(self.processed_path, exist_ok=True)

        for category in categories:
            folder_path = os.path.join(self.processed_path, category)
            os.makedirs(folder_path, exist_ok=True)

        log_folder = os.path.dirname(self.log_path)

        if log_folder:
            os.makedirs(log_folder, exist_ok=True)

    def write_log(self, message):
        with open(self.log_path, "a", encoding="utf-8") as log_file:
            log_file.write(message + "\n")

    def get_unique_path(self, target_path):
        if not os.path.exists(target_path):
            return target_path

        folder = os.path.dirname(target_path)
        filename = os.path.basename(target_path)

        name, extension = os.path.splitext(filename)

        counter = 1

        while True:
            new_filename = f"{name}_{counter}{extension}"
            new_path = os.path.join(folder, new_filename)

            if not os.path.exists(new_path):
                return new_path

            counter += 1

    def move_or_copy_file(self, file_path, category):
        target_folder = os.path.join(self.processed_path, category)
        os.makedirs(target_folder, exist_ok=True)

        target_path = os.path.join(
            target_folder,
            os.path.basename(file_path)
        )

        target_path = self.get_unique_path(target_path)

        if self.dry_run:
            return

        if self.copy_files:
            shutil.copy2(file_path, target_path)
        else:
            shutil.move(file_path, target_path)