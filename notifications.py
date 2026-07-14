import requests

def send_line_notify(channel_access_token: str, message: str) -> tuple[bool, str]:
    """
    ฟังก์ชันส่งข้อความแจ้งเตือนผ่าน LINE Messaging API (Broadcast)
    ทดแทนระบบ LINE Notify เซิร์ฟเวอร์เดิมที่ปิดบริการไปแล้ว
    """
    if not channel_access_token:
        return False, "ไม่พบ Channel Access Token ในระบบ"
        
    # 🌟 ย้ายมาใช้ Endpoint ใหม่ของ LINE Official Account
    url = "https://api.line.me/v2/bot/message/broadcast"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {channel_access_token}"
    }
    
    payload = {
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            return True, "ส่งการแจ้งเตือนเข้า LINE สำเร็จ! 🎉"
        else:
            return False, f"ส่งไม่สำเร็จ รหัสสถานะ: {response.status_code} ({response.text})"
    except Exception as e:
        return False, f"เกิดข้อผิดพลาดในการเชื่อมต่อเครือข่าย: {e}"