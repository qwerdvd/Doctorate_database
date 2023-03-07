import json
from typing import Dict


def read_json(filepath: str, **args) -> Dict:

    with open(filepath, **args) as f:
        return json.load(f)
