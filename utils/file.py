import json
import os
import pickle
import shutil
from typing import Any

import yaml


class File:
    """
    A class that provides utility methods for reading and writing various file formats.
    """

    @staticmethod
    def read_pickle_file(path: str) -> Any:
        """
        Reads a pickle file from the specified file path.

        Parameters:
            path (str): The file path of the pickle file to read.
        """
        with open(path, "rb") as handle:
            return pickle.load(handle)

    @staticmethod
    def write_pickle_file(data: Any, path: str) -> None:
        """
        Write data to a pickle file with the specified file path.

        Parameters:
            data (any): The data to write into the pickle file.
            path (str): The file path of the pickle file.
        """
        if os.path.exists(path):
            os.remove(path)

        with open(path, "wb") as handle:
            pickle.dump(data, handle)

    @staticmethod
    def read_json_file(path: str) -> Any:
        """
        Reads a JSON file from the specified file path.

        Parameters:
            path (str): The file path of the JSON file to read.
        """
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def write_json_file(data: dict, path: str) -> None:
        """
        Write data to a JSON file with the specified file path.

        Parameters:
            data (dict): The data to write into the JSON file.
            path (str): The file path of the pickle file.
        """
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(data, handle)

    @staticmethod
    def make_dir(path: str) -> bool:
        """
        Create a directory with the specified path.

        Parameters:
            path (str): The path of the directory.

        Returns:
            bool: True if the creation process is successful, False otherwise.
        """
        if not os.path.exists(path):
            os.mkdir(path)
            return True
        return False

    @staticmethod
    def remmove_dir(path: str) -> None:
        """
        Remove a directory with the specified path.

        Parameters:
            path (str): The path of the directory.

        Returns:
            bool: True if the remove process is successful, False otherwise.
        """
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)

    @staticmethod
    def read_yaml_file(path: str) -> Any:
        """
        Reads a YAML file from the specified file path.

        Parameters:
            path (str): The file path of the YAML file to read.
        """
        with open(path, encoding="utf-8") as f:
            return yaml.load(f, Loader=yaml.FullLoader)
