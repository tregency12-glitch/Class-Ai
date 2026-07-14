import json
import streamlit as st
import pandas as pd
from datetime import datetime, time
from PIL import Image

from utils.constants import DAYS_TH, DEFAULT_CONFIG
from utils.storage import load_schedule, save_schedule, load_config, save_config
from utils.schedule import (
    today_name,
    get_classes_for_day,
    get_class_status,
    format_countdown,
    total_hours_today,
    get_class_state,
    is_duplicate,
    build_timeline_html,
    check_overlaps,
    build_weekly_grid_html,
)
from utils.styles import (
    inject_global_css,
    render_metric_card,
    render_status_banner,
    render_class_card,
)
from utils.ai_scanner import scan_schedule_image
from utils.notifications import send_line_notify


def render_live_countdown(next_class: dict) -> str:
    if not next_class:
        return ""
    
    target_time = next_class['start_time'] # "HH:MM"
    subject = next_class['subject']
    room = next_class.get('room') or 'ไม่ระบุห้อง'
    
    html_out = f"""
    <div class="live-countdown-card">
        <div class="live-countdown-title">⏱️ นับถอยหลังเข้าเรียนวิชาถัดไป</div>
        <div class="live-countdown-subject">{subject} · ห้อง {room}</div>
        <div id="live-timer" class="live-timer-value">--:--:--</div>
    </div>
    <script>
    (function() {{
        var targetTimeStr = "{target_time}";
        var parts = targetTimeStr.split(":");
        var targetDate = new Date();
        targetDate.setHours(parseInt(parts[0], 10));
        targetDate.setMinutes(parseInt(parts[1], 10));
        targetDate.setSeconds(0);
        targetDate.setMilliseconds(0);
        
        function updateTimer() {{
            var now = new Date();
            var diff = targetDate - now;
            var timerEl = document.getElementById("live-timer");
            if (!timerEl) return;
            
            if (diff <= 0) {{
                timerEl.innerHTML = "ถึงเวลาเรียนแล้ว!";
                timerEl.style.color = "#34D399";
                return;
            }}
            
            var hours = Math.floor(diff / (1000 * 60 * 60));
            var mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            var secs = Math.floor((diff % (1000 * 60)) / 1000);
            
            var hStr = hours < 10 ? "0" + hours : hours;
            var mStr = mins < 10 ? "0" + mins : mins;
            var sStr = secs < 10 ? "0" + secs : secs;
            
            timerEl.innerHTML = hStr + ":" + mStr + ":" + sStr;
        }}
        
        updateTimer();
        var timerId = setInterval(updateTimer, 1000);
    }})();
    </script>
    """
    return "".join(line.strip() for line in html_out.split("\n"))



# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Class AI | Smart Reminder",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_css()

# ── Session state init ─────────────────────────────────────────
if "schedule" not in st.session_state:
    st.session_state.schedule = load_schedule()
if "scan_preview" not in st.session_state:
    st.session_state.scan_preview = None

# ระบบจัดการสเตตนำทาง (Navigation State Sync)
if "current_menu" not in st.session_state:
    st.session_state["current_menu"] = "📋 แดชบอร์ด"

# ตรวจเช็กหากมีการกดปุ่มข้ามหน้ามาจากหน้าอื่น
if "_nav" in st.session_state:
    st.session_state["current_menu"] = st.session_state.pop("_nav")


def persist_schedule():
    save_schedule(st.session_state.schedule)


config = load_config()
now = datetime.now()
today = today_name()


# ── Sidebar ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 Class AI")
    st.caption("Smart Class Reminder")
    st.divider()

    menu_options = ["📋 แดชบอร์ด", "📅 ตารางเรียน", "📸 สแกนตาราง", "➕ เพิ่มวิชา", "⚙️ ตั้งค่า"]
    
    if st.session_state["current_menu"] not in menu_options:
        st.session_state["current_menu"] = "📋 แดชบอร์ด"

    menu = st.radio(
        "เมนูหลัก",
        menu_options,
        index=menu_options.index(st.session_state["current_menu"]),
        label_visibility="collapsed",
        key="main_menu_radio"
    )
    st.session_state["current_menu"] = menu

    st.divider()
    st.metric("📅 วันนี้", f"วัน{today}")
    st.metric("⏰ เวลาปัจจุบัน", now.strftime("%H:%M น."))

    today_classes_sidebar = get_classes_for_day(st.session_state.schedule, today)
    _, next_cls = get_class_status(today_classes_sidebar)
    if next_cls:
        st.info(f"วิชาถัดไป: **{next_cls['subject']}** ({next_cls['start_time']})")
    elif today_classes_sidebar:
        st.success("เรียนครบหมดแล้ววันนี้ 🎉")
    else:
        st.warning("ไม่มีตารางเรียนวันนี้")

    token_val = config.get("channel_access_token") or config.get("line_token")
    line_ok = "✅" if token_val else "❌"
    gemini_ok = "✅" if config.get("gemini_key") else "❌"
    st.caption(f"LINE {line_ok} · Gemini {gemini_ok}")


def page_header(title: str, subtitle: str = ""):
    sub_html = f"<div class='hero-sub'>{subtitle}</div>" if subtitle else ""
    st.markdown(
        f"<div class='hero-header'><div><h1 class='hero-title'>{title}</h1>{sub_html}</div></div>",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════
# PAGE 1: Dashboard
# ══════════════════════════════════════════════════════════════
if st.session_state["current_menu"] == "📋 แดชบอร์ด":
    page_header("📋 แดชบอร์ด", f"วัน{today} · {now.strftime('%d/%m/%Y')}")

    today_classes = get_classes_for_day(st.session_state.schedule, today)
    current, next_class = get_class_status(today_classes)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        val = current["subject"] if current else ("ไม่มีเรียน" if today_classes else "—")
        render_metric_card("กำลังเรียน", val, "metric-value--live" if current else "")
    with m2:
        if next_class:
            val = f"{next_class['subject']} ({format_countdown(next_class['start_time'])})"
        else:
            val = "ไม่มีเรียน" if today_classes else "—"
        render_metric_card("วิชาถัดไป", val, "metric-value--next" if next_class else "")
    with m3:
        render_metric_card("วิชาวันนี้", str(len(today_classes)))
    with m4:
        hours = total_hours_today(today_classes)
        render_metric_card("ชั่วโมงเรียนรวม", f"{hours:.1f} ชม.")

    st.markdown("---")

    if current:
        render_status_banner(
            "now",
            "กำลังเรียนอยู่ขณะนี้",
            f"{current['subject']} · ห้อง {current.get('room', '—')} · เลิกเรียน {current['end_time']}",
        )
    elif next_class:
        st.markdown(render_live_countdown(next_class), unsafe_allow_html=True)
    elif not today_classes:
        render_status_banner("free", "วันนี้ไม่มีเรียน", "วันพักผ่อนสบายๆ ไม่มีตารางเรียนในระบบ")
    else:
        render_status_banner("free", "เลิกเรียนแล้ว", "เย้! เรียนครบถ้วนทุกวิชาของวันนี้แล้วครับ 🎉")

    st.subheader("ไทม์ไลน์วันนี้")
    # 🌟 แก้ไข: ลบ , now ออกจากฟังก์ชัน build_timeline_html เพื่อไม่ให้พารามิเตอร์เกิน
    st.markdown(build_timeline_html(today_classes), unsafe_allow_html=True)

    st.subheader("รายวิชาวันนี้")
    if today_classes:
        for c in sorted(today_classes, key=lambda x: x["start_time"]):
            render_class_card(c, get_class_state(c))
    else:
        st.markdown('<div class="empty-state"><h3>🎉 ยังไม่มีตารางเรียนวันนี้</h3><p>คุณสามารถสแกนรูปตารางเรียนหรือเพิ่มวิชาด้วยตนเองได้ด่วนที่ปุ่มด้านล่าง</p></div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📸 ไปสแกนตาราง", use_container_width=True):
                st.session_state["current_menu"] = "📸 สแกนตาราง"
                st.rerun()
        with c2:
            if st.button("➕ เพิ่มวิชา", use_container_width=True):
                st.session_state["current_menu"] = "➕ เพิ่มวิชา"
                st.rerun()


# ══════════════════════════════════════════════════════════════
# PAGE 2: Full schedule
# ══════════════════════════════════════════════════════════════
elif st.session_state["current_menu"] == "📅 ตารางเรียน":
    page_header("📅 ตารางเรียนทั้งหมด", "ตรวจสอบรายการวิชาเรียนสะสมในระบบ")

    search_query = st.text_input("🔍 ค้นหาวิชาเรียน", placeholder="พิมพ์เพื่อค้นหาตามชื่อวิชาเรียน...")

    tab_week, tab_grid, tab_all = st.tabs([
        "📆 มุมมองภาพรวมรายสัปดาห์ (รายวัน)",
        "📊 ตารางเรียนรายสัปดาห์ (Grid)",
        "📋 แก้ไข/ลบรายรายการ"
    ])

    with tab_week:
        cols = st.columns(7)
        for i, day_item in enumerate(DAYS_TH):
            with cols[i]:
                st.markdown(f"### {day_item}")
                day_classes = [c for c in st.session_state.schedule if c["day"] == day_item]
                if search_query:
                    day_classes = [c for c in day_classes if search_query.lower() in c["subject"].lower()]
                
                if day_classes:
                    for c in sorted(day_classes, key=lambda x: x["start_time"]):
                        st.info(f"📖 **{c['subject']}**\n\n⏱️ {c['start_time']} - {c['end_time']}\n\n🚪 ห้อง: {c.get('room','—')}")
                else:
                    st.caption("ไม่มีวิชาเรียน")

    with tab_grid:
        # Show grid timetable
        grid_schedule = st.session_state.schedule
        if search_query:
            grid_schedule = [c for c in grid_schedule if search_query.lower() in c["subject"].lower()]
        
        st.markdown(build_weekly_grid_html(grid_schedule), unsafe_allow_html=True)

    with tab_all:
        if not st.session_state.schedule:
            st.info("ยังไม่มีข้อมูลตารางเรียนในระบบฐานข้อมูล")
        else:
            visible_count = 0
            for idx, c in enumerate(st.session_state.schedule):
                if search_query and search_query.lower() not in c["subject"].lower():
                    continue
                visible_count += 1
                with st.expander(f"📍 [{c['day']}] {c['start_time']} - {c['end_time']}  👉  {c['subject']}", expanded=False):
                    with st.form(f"edit_{idx}"):
                        sub = st.text_input("ชื่อวิชาเรียน", value=c["subject"])
                        day = st.selectbox("วันเรียน", DAYS_TH, index=DAYS_TH.index(c["day"]))
                        t1, t2 = st.columns(2)
                        with t1:
                            sh, sm = map(int, c["start_time"].split(":"))
                            start = st.time_input("เวลาเริ่ม", value=time(sh, sm), key=f"s_{idx}")
                        with t2:
                            eh, em = map(int, c["end_time"].split(":"))
                            end = st.time_input("เวลาเลิก", value=time(eh, em), key=f"e_{idx}")
                        room = st.text_input("ห้องเรียน", value=c.get("room", ""))

                        c1, c2 = st.columns(2)
                        with c1:
                            save_btn = st.form_submit_button("💾 บันทึกการแก้ไข", use_container_width=True)
                        with c2:
                            del_btn = st.form_submit_button("🗑️ ลบวิชานี้", use_container_width=True)

                        if save_btn:
                            updated = {
                                "subject": sub.strip(),
                                "day": day,
                                "start_time": start.strftime("%H:%M"),
                                "end_time": end.strftime("%H:%M"),
                                "room": room.strip(),
                            }
                            
                            # check overlaps
                            overlaps = check_overlaps(st.session_state.schedule, updated, exclude_index=idx)
                            
                            if is_duplicate(st.session_state.schedule, updated, exclude_index=idx):
                                st.error("ไม่สามารถบันทึกได้เนื่องจากวันและเวลาซ้ำกับวิชาอื่นตรงกันทุกประการ")
                            else:
                                if overlaps:
                                    st.warning("⚠️ เวลาเรียนคาบนี้ซ้อนทับกับวิชาอื่นในระบบ:")
                                    for o in overlaps:
                                        st.write(f"- {o['subject']} ({o['start_time']} - {o['end_time']})")
                                st.session_state.schedule[idx] = updated
                                persist_schedule()
                                st.toast("อัปเดตวิชาเรียบร้อย")
                                st.rerun()

                        if del_btn:
                            st.session_state.schedule.pop(idx)
                            persist_schedule()
                            st.toast("ลบข้อมูลวิชาออกแล้ว")
                            st.rerun()
            if visible_count == 0:
                st.info("ไม่พบวิชาเรียนที่ตรงกับคำค้นหา")


# ══════════════════════════════════════════════════════════════
# PAGE 3: AI Scanner
# ══════════════════════════════════════════════════════════════
elif st.session_state["current_menu"] == "📸 สแกนตาราง":
    page_header("📸 AI Schedule Scanner", "แปลงรูปถ่ายตารางเรียนให้เป็นดิจิทัลด้วย Gemini API")

    if not config.get("gemini_key"):
        st.warning("⚠️ กรุณาตั้งค่าคอนฟิกตัวแปร Gemini API Key ที่หน้าเมนู ⚙️ ตั้งค่า ก่อนเริ่มใช้งานสแกนภาพ")
    else:
        uploaded = st.file_uploader("อัปโหลดไฟล์ภาพตารางเรียนของคุณ", type=["jpg", "jpeg", "png", "webp"])

        if uploaded:
            col_img, col_info = st.columns([1, 1])
            with col_img:
                st.image(uploaded, caption="ภาพตารางเรียนต้นฉบับ", use_container_width=True)
            with col_info:
                st.markdown("### 🤖 ขั้นตอนการทำงานของระบบ AI")
                st.write("1. ตรวจสอบความชัดเจนของรูปภาพ\n2. กดปุ่มวิเคราะห์เพื่อส่งข้อมูลหาโมเดล AI\n3. ระบบจะแปลงผลลัพธ์ลงตารางดิจิทัลให้อัตโนมัติ")

                if st.button("🧠 สั่ง AI เริ่มแกะข้อมูลตารางเรียน", type="primary", use_container_width=True):
                    with st.spinner("AI กำลังวิเคราะห์และแยกวิชาเรียนให้โปรดรอสักครู่..."):
                        try:
                            img = Image.open(uploaded)
                            st.session_state.scan_preview = scan_schedule_image(img, config["gemini_key"])
                            st.success(f"🎉 ตรวจสอบข้อมูลเสร็จสิ้น! พบรายวิชาทั้งหมด {len(st.session_state.scan_preview)} รายการ")
                        except Exception as e:
                            st.error(f"การวิเคราะห์รูปภาพล้มเหลวเนื่องจาก: {e}")
                            st.session_state.scan_preview = None

        if st.session_state.scan_preview:
            st.subheader("👀 ตรวจสอบความถูกต้องของข้อมูลจาก AI")
            df = pd.DataFrame(st.session_state.scan_preview)
            st.dataframe(df, use_container_width=True, hide_index=True)

            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("✅ ยืนยันเพิ่มเข้าตารางหลัก", type="primary", use_container_width=True):
                    st.session_state.schedule.extend(st.session_state.scan_preview)
                    persist_schedule()
                    st.session_state.scan_preview = None
                    st.toast("เพิ่มวิชาทั้งหมดลงระบบแล้ว!")
                    st.rerun()
            with c2:
                if st.button("🔄 ล้างและบันทึกแทนที่ตารางเก่า", use_container_width=True):
                    st.session_state.schedule = list(st.session_state.scan_preview)
                    persist_schedule()
                    st.session_state.scan_preview = None
                    st.toast("เขียนทับตารางเรียนเดิมเรียบร้อย!")
                    st.rerun()
            with c3:
                if st.button("❌ ยกเลิกและล้างสเตต", use_container_width=True):
                    st.session_state.scan_preview = None
                    st.rerun()


# ══════════════════════════════════════════════════════════════
# PAGE 4: Manual add
# ══════════════════════════════════════════════════════════════
elif st.session_state["current_menu"] == "➕ เพิ่มวิชา":
    page_header("➕ เพิ่มวิชาเรียน", "เพิ่มตารางเรียนแมนนวลด้วยตัวคุณเอง")

    with st.form("add_class", clear_on_submit=True):
        sub = st.text_input("ชื่อวิชาเรียน *", placeholder="เช่น Advance Computer Programming")
        day = st.selectbox("วันเรียน *", DAYS_TH, index=DAYS_TH.index(today))
        c1, c2 = st.columns(2)
        with c1:
            start = st.time_input("เวลาเริ่มเรียน *", value=time(9, 0))
        with c2:
            end = st.time_input("เวลาเลิกเรียน *", value=time(10, 30))
        room = st.text_input("ห้องเรียน / สถานที่เรียน", placeholder="เช่น ห้องบรรยาย 402 หรือ เรียนออนไลน์ WebEx")

        submitted = st.form_submit_button("💾 ยืนยันบันทึกวิชาเรียน", type="primary", use_container_width=True)

        if submitted:
            if not sub.strip():
                st.error("กรุณาระบุชื่อวิชาเรียนด้วยครับ")
            elif start >= end:
                st.error("เวลาเลิกเรียนต้องอยู่หลังเวลาเริ่มเรียนเสมอ")
            else:
                entry = {
                    "subject": sub.strip(),
                    "day": day,
                    "start_time": start.strftime("%H:%M"),
                    "end_time": end.strftime("%H:%M"),
                    "room": room.strip() if room.strip() else "ไม่ระบุห้องเรียน",
                }
                
                # Check duplication and overlap
                overlaps = check_overlaps(st.session_state.schedule, entry)
                
                if is_duplicate(st.session_state.schedule, entry):
                    st.error("❌ วิชานี้ไม่สามารถบันทึกได้เนื่องจากมีข้อมูลซ้ำซ้อนตรงกันทุกประการ")
                else:
                    if overlaps:
                        st.warning("⚠️ เวลาเรียนคาบนี้ซ้อนทับกับวิชาอื่นในระบบ:")
                        for o in overlaps:
                            st.write(f"- {o['subject']} ({o['start_time']} - {o['end_time']})")
                    
                    st.session_state.schedule.append(entry)
                    persist_schedule()
                    st.toast("บันทึกวิชาใหม่สำเร็จ!")
                    st.success(f"เพิ่มวิชา **{entry['subject']}** เข้าตารางวัน{entry['day']} สำเร็จแล้ว")


# ══════════════════════════════════════════════════════════════
# PAGE 5: Settings
# ══════════════════════════════════════════════════════════════
elif st.session_state["current_menu"] == "⚙️ ตั้งค่า":
    page_header("⚙️ ตั้งค่าระบบ", "จัดการรหัสเชื่อมต่อ API และการตั้งเวลาทำงานระบบแจ้งเตือน")

    with st.form("settings"):
        st.subheader("🔑 บันทึกสิทธิ์และ API Keys")
        line_token_input = st.text_input(
            "LINE Channel Access Token",
            value=config.get("channel_access_token") or config.get("line_token") or "",
            type="password",
            help="คัดลอกโทเค็นแบบ Long-Lived มาจากเมนู Messaging API ในหน้า LINE Developers Console",
        )
        gemini_key = st.text_input(
            "Gemini API Key",
            value=config.get("gemini_key", ""),
            type="password",
            help="สร้างสิทธิ์การใช้งานคีย์ฟรีได้ที่เว็บไซต์ Google AI Studio",
        )

        st.subheader("🔔 คอนฟิกตัวตั้งเวลาเปิดกระดิ่งแจ้งเตือน")
        c1, c2 = st.columns(2)
        with c1:
            remind_1day_hour = st.number_input(
                "เตือนล่วงหน้าช่วงค่ำ (เวลา น. ของวันก่อนหน้าเรียน)",
                min_value=0, max_value=23, value=int(config.get("remind_1day_hour", 20)),
            )
        with c2:
            remind_hours_before = st.number_input(
                "ส่งไลน์ส่งซ้ำก่อนคาบเรียนเริ่มจี้ตัว (จำนวนชั่วโมงก่อนเริ่ม)",
                min_value=0.5, max_value=6.0, value=float(config.get("remind_hours_before", 2.0)), step=0.5,
            )

        saved = st.form_submit_button("💾 บันทึกข้อมูลคอนฟิกทั้งหมดลงไฟล์ระบบ", type="primary", use_container_width=True)
        if saved:
            new_cfg = {
                "line_token": line_token_input.strip(),
                "channel_access_token": line_token_input.strip(),
                "gemini_key": gemini_key.strip(),
                "remind_1day_hour": int(remind_1day_hour),
                "remind_hours_before": float(remind_hours_before),
            }
            save_config(new_cfg)
            config.update(new_cfg)
            st.toast("บันทึกคอนฟิกเสร็จสิ้น")
            st.success("ระบบทำการปรับปรุงค่าการเชื่อมต่อเรียบร้อยแล้ว")

    st.divider()
    st.subheader("🧪 ทดสอบการบรอดแคสต์ผ่าน LINE OA")
    if st.button("ส่งข้อความทดสอบเข้า LINE", use_container_width=True):
        active_token = config.get("channel_access_token") or config.get("line_token", "")
        
        if not active_token:
            st.error("❌ ไม่พบคีย์ไลน์ในระบบ กรุณากรอกโทเค็นในช่องด้านบนและกดปุ่มบันทึกก่อนทำการส่งทดสอบครับ")
        else:
            with st.spinner("ระบบกำลังทดสอบส่ง Broadcast ยิงสัญญาณหาไอดีคุณ..."):
                ok, msg = send_line_notify(
                    active_token,
                    "✅ Class AI — ทดสอบการส่งข้อความผ่านระบบ LINE Official Account ด้วย Messaging API เรียบร้อย!",
                )
                if ok:
                    st.success(msg)
                    st.toast("ส่งสำเร็จ! เช็กมือถือได้เลย", icon="🟢")
                else:
                    st.error(msg)

    st.divider()
    st.subheader("📦 ส่วนจัดการไฟล์และข้อมูลสำรอง")
    c1, c2 = st.columns(2)
    with c1:
        uploaded_backup = st.file_uploader("Import ข้อมูลโครงสร้างแบบ JSON", type=["json"], key="import_json")
        if uploaded_backup:
            try:
                imported = json.load(uploaded_backup)
                if isinstance(imported, list):
                    if st.button("ยืนยันการทำ Import ข้อมูลด่วน"):
                        st.session_state.schedule = imported
                        persist_schedule()
                        st.toast("Import สำเร็จ")
                        st.rerun()
                else:
                    st.error("โครงสร้างไฟล์อัปโหลดภายนอกต้องอยู่ในรูปแบบอาร์เรย์รายการตารางเท่านั้น")
            except json.JSONDecodeError:
                st.error("รูปแบบไฟล์ JSON ชำรุดหรือไม่ถูกต้อง")

    with c2:
        st.metric("จำนวนตารางเรียนสะสมปัจจุบันทั้งหมด", len(st.session_state.schedule))
        
        # Backup export download button
        schedule_json_str = json.dumps(st.session_state.schedule, ensure_ascii=False, indent=4)
        st.download_button(
            label="📥 Export สำรองข้อมูลตารางเรียน (JSON)",
            data=schedule_json_str,
            file_name="class_ai_backup.json",
            mime="application/json",
            use_container_width=True
        )
        
        if st.button("🗑️ รีเซ็ตลบฐานข้อมูลตารางเรียนทั้งหมด", use_container_width=True, type="primary"):
            st.session_state.schedule = []
            persist_schedule()
            st.toast("รีเซ็ตระบบเรียบร้อย")
            st.rerun()