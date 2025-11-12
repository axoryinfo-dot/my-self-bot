# self_bot_v6_render.py
# نسخه نهایی با پشتیبانی از StringSession

import asyncio
import logging
import os
from datetime import datetime
from telethon import TelegramClient, errors, events
from telethon.tl.functions.account import UpdateProfileRequest

from flask import Flask
from threading import Thread
from telethon.sessions import StringSession # <-- مهم

# ----------- CONFIG -----------
try:
    API_ID = int(os.environ.get('API_ID'))
    API_HASH = os.environ.get('API_HASH')
    # --- استفاده از رشته سشن ---
    SESSION_STRING = os.environ.get('TELETHON_SESSION')
except (ValueError, TypeError):
    print("!!! خطا: متغیرهای API_ID و API_HASH تنظیم نشده‌اند !!!")
    exit()

if not SESSION_STRING:
    print("!!! خطا: متغیر TELETHON_SESSION تنظیم نشده است! !!!")
    exit()

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# --- استفاده از StringSession برای لاگین ---
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# ------------------------------------
# --- بخش وب‌سرور (بدون تغییر) ---
# ------------------------------------
app = Flask('')
@app.route('/')
def home():
    return "✅ سلف بات شما زنده و در حال اجرا است."
def run_flask():
  app.run(host='0.0.0.0', port=8080) # پورت 8080 ممکن است لازم باشد
def start_keep_alive_server():
    t = Thread(target=run_flask)
    t.start()

# ------------------------------------
# --- توابع کمکی (بدون تغییر) ---
# ------------------------------------
def to_fancy_font(text):
    normal = "0123456789"
    fancy  = "𝟎𝟏𝟐𝟑🟒𝟓𝟔𝟕𝟖𝟗"
    mapping_table = str.maketrans(normal, fancy)
    translated = text.translate(mapping_table)
    return translated.replace(":", " ∶ ")

# ------------------------------------
# --- ماژول ۱: ساعت زنده (بدون تغییر) ---
# ------------------------------------
async def profile_clock_loop():
    try:
        me = await client.get_me()
        current_first_name = me.first_name or "User"
        logger.info(f"نام کوچک فعلی شما: {current_first_name}. این نام ثابت می‌ماند.")
    except Exception as e:
        logger.error(f"خطا در دریافت نام: {e}. از 'User' استفاده می‌شود.")
        current_first_name = "User"

    last_sent_time = ""
    while True:
        try:
            now = datetime.now()
            if (now.minute % 2 == 0) and (now.strftime("%H:%M") != last_sent_time):
                current_time_str = now.strftime("%H:%M")
                fancy_time = to_fancy_font(current_time_str)
                new_last_name = f"| {fancy_time} 🇮🇷"
                new_bio = ""
                await client(UpdateProfileRequest(
                    first_name=current_first_name,
                    last_name=new_last_name,
                    about=new_bio
                ))
                last_sent_time = current_time_str
                logger.info(f"Profile updated successfully to: {new_last_name}")
                await asyncio.sleep(60)
            else:
                await asyncio.sleep(15)
        except errors.FloodWaitError as e:
            logger.warning(f"FloodWaitError: باید {e.seconds} ثانیه صبر کنیم.")
            await asyncio.sleep(e.seconds + 5) 
        except Exception as e:
            logger.error(f"خطای ناشناخته در حلقه پروفایل: {e}")
            await asyncio.sleep(60)

# ------------------------------------
# --- ماژول‌های ۲، ۳، ۴ (بدون تغییر) ---
# ------------------------------------
@client.on(events.NewMessage(pattern=r"^\.info$", from_users="me"))
async def handle_info(event):
    if not event.is_reply: return await event.edit("❌ روی پیام یک نفر ریپلای کنید.")
    try:
        reply_msg = await event.get_reply_message()
        user_entity = await client.get_entity(reply_msg.from_id)
        username = f"@{user_entity.username}" if user_entity.username else "ندارد"
        info_text = (f"👤 **اطلاعات کاربر:**\n"
                     f"**ID:** `{user_entity.id}`\n"
                     f"**نام:** `{user_entity.first_name or 'ندارد'}`\n"
                     f"**یوزرنیم:** `{username}`\n"
                     f"**ربات است؟** `{' بله ' if user_entity.bot else ' خیر '}`")
        await event.edit(info_text)
    except Exception as e: await event.edit(f"⚠️ خطایی رخ داد: {str(e)}")

@client.on(events.NewMessage(pattern=r"^\.type (.*)", from_users="me"))
async def handle_type(event):
    text_to_type = event.pattern_match.group(1)
    if not text_to_type: return await event.edit("❌ .type <متن>")
    current_text = ""
    for char in text_to_type:
        current_text += char
        try:
            await event.edit(current_text); await asyncio.sleep(0.05)
        except (errors.FloodWaitError, errors.MessageNotModifiedError): pass
        except Exception: break

@client.on(events.NewMessage(pattern=r"^\.count (\d+)$", from_users="me"))
async def handle_count(event):
    try: count_num = int(event.pattern_match.group(1))
    except ValueError: return await event.edit("❌ عدد نامعتبر است.")
    for i in range(count_num, 0, -1):
        await event.edit(f"**{i}**"); await asyncio.sleep(1)
    await event.edit("🚀 **!Go** 🚀")

# ------------------------------------
# --- تابع اصلی اجرا (بدون تغییر) ---
# ------------------------------------
async def main_bot():
    print("🚀 در حال اتصال سلف بات (v6)...")
    await client.start()
    user = await client.get_me()
    print(f"✅ سلف بات به عنوان {user.first_name} فعال شد.")
    logger.info("Starting profile clock loop (2 min interval)...")
    asyncio.create_task(profile_clock_loop())
    await client.send_message("me",
        "✅ **سلف بات (v6) با موفقیت روی Render فعال شد.**\n"
        "🌀 *حلقه ساعت (۲ دقیقه‌ای) فعال شد.*\n"
        "ℹ️ *دستورات `.info`, `.type`, `.count` فعال شدند.*\n\n"
        "--- 🕋 ✨ 🇮🇷 ---\n"
        "**قدرت گرفته توسط امام خمینی**")
    print("✅ سلف بات آماده است و به دستورات گوش می‌دهد...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    start_keep_alive_server()
    print("🌀 وب‌سرور بیدارباش (Keep-Alive) فعال شد.")
    client.loop.run_until_complete(main_bot())
