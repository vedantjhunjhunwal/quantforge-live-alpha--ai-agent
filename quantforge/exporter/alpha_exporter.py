from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any


class AlphaExporter:
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.output_file = self.output_dir / "validated_alphas.jsonl"

    def export(self, payload: Dict[str, Any]) -> Path:
        with self.output_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, default=str) + "\n")
        return self.output_file
