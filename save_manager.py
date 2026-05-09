"""JSON persistence with offline decay calculation."""

import json
import os
import time
from pathlib import Path

from config import (
    SAVE_DIR, SAVE_FILE,
    HUNGER_DECAY_PER_HOUR,
    HAPPINESS_DECAY_PER_HOUR,
    ENERGY_DECAY_PER_HOUR,
)


class SaveManager:
    def __init__(self):
        self.save_dir = Path(SAVE_DIR).expanduser()
        self.save_path = self.save_dir / SAVE_FILE

    def save(self, data: dict):
        data["version"] = 1
        data["timestamp"] = time.time()
        self.save_dir.mkdir(parents=True, exist_ok=True)
        tmp = str(self.save_path) + ".tmp"
        with open(tmp, 'w') as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, str(self.save_path))

    def load(self) -> dict | None:
        if not self.save_path.exists():
            return None
        with open(self.save_path) as f:
            data = json.load(f)

        # Apply offline decay
        elapsed = time.time() - data.get("timestamp", time.time())
        offline_hours = elapsed / 3600.0

        if "needs" in data:
            data["needs"]["hunger"] = max(
                0, data["needs"].get("hunger", 80) - HUNGER_DECAY_PER_HOUR * offline_hours
            )
            data["needs"]["happiness"] = max(
                0, data["needs"].get("happiness", 70) - HAPPINESS_DECAY_PER_HOUR * offline_hours
            )
            data["needs"]["energy"] = max(
                0, data["needs"].get("energy", 90) - ENERGY_DECAY_PER_HOUR * offline_hours
            )

        return data
