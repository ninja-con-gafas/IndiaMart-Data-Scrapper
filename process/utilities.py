import json
import os
import re
from typing import List, Dict


def partition_json_by_key(input_file_path: str, output_directory: str, key: str) -> List[str]:
    """
    Loads a JSON array from a file and partitions the records based on the value of the specified key.
    Each partition is saved as a separate JSON file containing all records with the same key value.

    Parameters:
        input_file_path (str): Path to the JSON array file.
        output_directory (str): Directory to save partitioned JSON files.
        key (str): The key to partition the records by.

    Returns:
        List[str]: Paths to the generated JSON files.

    Raises:
        FileNotFoundError: If the input file does not exist.
        json.JSONDecodeError: If the input is not a valid JSON array.
        KeyError: If the specified key is missing in all records.
    """

    if not os.path.isfile(input_file_path):
        raise FileNotFoundError(f"Input file not found: {input_file_path}")

    output_directory = os.path.join(output_directory, key)
    os.makedirs(output_directory, exist_ok=True)

    with open(input_file_path, "r", encoding="utf-8") as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise json.JSONDecodeError("Expected a JSON array at root", doc=str(records), pos=0)

    grouped_records: Dict[str, List[dict]] = {}
    key_found = False

    for record in records:
        value = record.get(key)
        if value is None:
            continue
        key_found = True
        grouped_records.setdefault(str(value), []).append(record)

    if not key_found:
        raise KeyError(f"None of the records contain the key '{key}'.")

    output_paths: List[str] = []

    for value, group in grouped_records.items():
        safe_file_name = f"{re.sub(r'[^a-zA-Z0-9]+', '_', value.strip().lower())}.json"
        file_path = os.path.join(output_directory, safe_file_name)

        with open(file_path, "w", encoding="utf-8") as output_file:
            json.dump(group, output_file, ensure_ascii=False, indent=2)

        output_paths.append(file_path)

    return output_paths
