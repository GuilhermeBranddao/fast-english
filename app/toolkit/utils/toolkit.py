import json

def normalize_text(text: str) -> str:
    """Normalizes text by converting to lowercase and stripping whitespace."""
    return text.lower().strip()

def read_json(file_path: str) -> dict:
    """Reads a JSON file and returns its content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error File not found: {file_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON: {file_path}")
    return {}