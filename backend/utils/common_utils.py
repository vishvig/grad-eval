import os
import zipfile


class CommonUtils(object):
    def __init__(self):
        pass

    @staticmethod
    def zip_files(folder_path, output_zip):
        # Create a ZipFile object
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through the directory
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.endswith('.csv') or file.endswith('.ipynb'):
                        # Create the full file path
                        file_path = os.path.join(root, file)
                        # Add file to the zip archive
                        zipf.write(file_path, os.path.relpath(file_path, folder_path))

    @staticmethod
    def make_dirs(path):
        try:
            os.makedirs(path)
        except OSError:
            pass


# Usage
# folder_path = 'path/to/your/coding_task_folder'  # Replace with your folder path
# output_zip = 'csv_files.zip'  # Name of the output zip file
# zip_csv_files(folder_path, output_zip)
