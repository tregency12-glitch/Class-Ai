import json
import os
from utils.constants import DB_FILE, CONFIG_FILE, DEFAULT_CONFIG


def load_json(path: str, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # 🌟 หากไฟล์ว่างเปล่า (0 bytes) หรือเสียหาย ให้คืนค่าเริ่มต้นทันที แอปจะไม่พัง
        return default


def save_json(path: str, data) -> None:
    # 🌟 ตรวจสอบและสร้างไดเรกทอรีให้อัตโนมัติหากยังไม่มี
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)
        
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_schedule() -> list:
    return load_json(DB_FILE, [])


def save_schedule(schedule: list) -> None:
    save_json(DB_FILE, schedule)


def load_config() -> dict:
    cfg = load_json(CONFIG_FILE, DEFAULT_CONFIG.copy())
    merged = DEFAULT_CONFIG.copy()
    merged.update(cfg)
    return merged


def save_config(config: dict) -> None:
    save_json(CONFIG_FILE, config)