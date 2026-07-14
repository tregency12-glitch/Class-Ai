import time
import json
import os
import requests
from datetime import datetime, timedelta

DB_FILE = "schedule_db.json"
CONFIG_FILE = "config.json"
DAYS_TH = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]

DEFAULT_CONFIG = {
    "line_token": "",
    "gemini_key": "",
    "remind_1day_hour": 20,
    "remind_hours_before": 2.0,
}


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    merged = DEFAULT_CONFIG.copy()
    merged.update(cfg)
    return merged


def send_line(token, msg):
    if not token:
        return
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "messages": [
            {
                "type": "text",
                "text": msg
            }
        ]
    }
    try:
        requests.post(url, headers=headers, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending message: {e}")


print("🤖 Class Reminder Worker กำลังทำงาน...")

already_sent_1day = []
already_sent_2hours = []

while True:
    now = datetime.now()
    current_day = DAYS_TH[now.weekday()]
    tomorrow = now + timedelta(days=1)
    tomorrow_day = DAYS_TH[tomorrow.weekday()]

    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            schedule = json.load(f)
        config = load_config()
        token = config.get("line_token", "")
        remind_hour = int(config.get("remind_1day_hour", 20))
        remind_before = float(config.get("remind_hours_before", 2.0))
        remind_window = (remind_before - 0.5, remind_before)

        # แจ้งเตือนล่วงหน้า 1 วัน
        if now.hour == remind_hour and now.minute == 0 and tomorrow_day not in already_sent_1day:
            classes = [c for c in schedule if c["day"] == tomorrow_day]
            if classes:
                msg = f"\n📚 [แจ้งเตือนล่วงหน้า 1 วัน]\nพรุ่งนี้ (วัน{tomorrow_day}) คุณมีเรียน:\n"
                for c in sorted(classes, key=lambda x: x["start_time"]):
                    msg += f"- {c['subject']} ({c['start_time']}-{c['end_time']}) ห้อง {c['room']}\n"
                send_line(token, msg)
                already_sent_1day.append(tomorrow_day)

        if now.hour == 0 and now.minute == 0:
            already_sent_1day.clear()
            already_sent_2hours.clear()

        # แจ้งเตือนก่อนเรียน
        for c in schedule:
            if c["day"] != current_day:
                continue
            class_dt = datetime.strptime(
                f"{now.strftime('%Y-%m-%d')} {c['start_time']}", "%Y-%m-%d %H:%M"
            )
            diff_h = (class_dt - now).total_seconds() / 3600
            key = f"{c['subject']}_{c['start_time']}"

            if remind_window[0] <= diff_h <= remind_window[1] and key not in already_sent_2hours:
                msg = (
                    f"\n🚨 [เตรียมตัวเรียน]\n"
                    f"วิชา: {c['subject']}\n"
                    f"⏰ {c['start_time']} น.\n"
                    f"📍 ห้อง {c['room']}"
                )
                send_line(token, msg)
                already_sent_2hours.append(key)

    time.sleep(30)