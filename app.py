# self_bot_v5_replit.py
# نسخه نهایی برای اجرای 24/7 در Replit
# شامل وب‌سرور Flask برای بیدار نگه داشتن

import asyncio
import logging
import os # <-- جدید: برای خواندن Secrets
from datetime import datetime
from telethon import TelegramClient, errors, events
from telethon.tl.functions.account import UpdateProfileRequest

# --- وارد کردن بخش‌های جدید ---
from flask import Flask
from threading import Thread

# ----------- CONFIG -----------
# !!! این‌ها را از "Secrets" در Replit می‌خوانیم !!!
try:
    API_ID = int(os.environ.get('API_ID'))
    API_HASH = os.environ.get('API_HASH')
except (ValueError, TypeError):
    print("!!! خطا: متغیرهای API_ID و API_HASH در بخش Secrets تنظیم نشده‌اند !!!")
    exit()

SESSION_NAME = "self_bot_session" # فقط یک نام برای فایل سشن
# ------------------------------

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# ------------------------------------
# --- بخش جدید: وب‌سرور بیدار نگهدارنده ---
# ------------------------------------
app = Flask('')

@app.route('/')
def home():
    return "✅ سلف بات شما زنده و در حال اجرا است."

def run_flask():
  app.run(host='0.0.0.0', port=8080)

def start_keep_alive_server():
    """یک ترد جدید برای اجرای وب‌سرور ایجاد می‌کند"""
    t = Thread(target=run_flask)
    t.start()

# ------------------------------------
# --- تابع فونت قشنگ (بدون تغییر) ---
# ------------------------------------
def to_fancy_font(text):
    normal = "0123456789"
    fancy  = "𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗"
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
# --- ماژول ۲: دستور .info (بدون تغییر) ---
# ------------------------------------
@client.on(events.NewMessage(pattern=r"^\.info$", from_users="me"))
async def handle_info(event):
    if not event.is_reply:
        return await event.edit("❌ روی پیام یک نفر ریپلای کنید.")
    try:
        reply_msg = await event.get_reply_message()
        user_entity = await client.get_entity(reply_msg.from_id)
        username = f"@{user_entity.username}" if user_entity.username else "ندارد"
        info_text = (
            f"👤 **اطلاعات کاربر:**\n"
            f"**ID:** `{user_entity.id}`\n"
            f"**نام:** `{user_entity.first_name or 'ندارد'}`\n"
            f"**یوزرنیم:** `{username}`\n"
            f"**ربات است؟** `{' بله ' if user_entity.bot else ' خیر '}`"
        )
        await event.edit(info_text)
    except Exception as e:
        await event.edit(f"⚠️ خطایی رخ داد: {str(e)}")

# ------------------------------------
# --- ماژول ۳: دستور .type (بدون تغییر) ---
# ------------------------------------
@client.on(events.NewMessage(pattern=r"^\.type (.*)", from_users="me"))
async def handle_type(event):
    text_to_type = event.pattern_match.group(1)
    if not text_to_type:
        return await event.edit("❌ .type <متن>")
    current_text = ""
    for char in text_to_type:
        current_text += char
        try:
            await event.edit(current_text)
            await asyncio.sleep(0.05)
        except (errors.FloodWaitError, errors.MessageNotModifiedError):
            pass
        except Exception:
            break

# ------------------------------------
# --- ماژول ۴: دستور .count (بدون تغییر) ---
# ------------------------------------
@client.on(events.NewMessage(pattern=r"^\.count (\d+)$", from_users="me"))
async def handle_count(event):
    try:
        count_num = int(event.pattern_match.group(1))
    except ValueError:
        return await event.edit("❌ عدد نامعتبر است.")
    for i in range(count_num, 0, -1):
        await event.edit(f"**{i}**")
        await asyncio.sleep(1)
    await event.edit("🚀 **!Go** 🚀")


# ------------------------------------
# --- تابع اصلی اجرا (تغییر کرده) ---
# ------------------------------------
async def main_bot():
    """تابع اصلی سلف بات (کلاینت تلگرام)"""
    print("🚀 در حال اتصال سلف بات...")
    # client.start() به طور خودکار از API_ID/HASH استفاده می‌کند
    await client.start()
    user = await client.get_me()
    print(f"✅ سلف بات به عنوان {user.first_name} فعال شد.")
    
    # --- اجرای حلقه ساعت در پس‌زمینه ---
    logger.info("Starting profile clock loop (2 min interval)...")
    asyncio.create_task(profile_clock_loop())
    
    await client.send_message(
        "me",
        "✅ **سلف بات (v5) با موفقیت روی Replit فعال شد.**\n"
        "🌀 *حلقه ساعت (۲ دقیقه‌ای) فعال شد.*\n"
        "ℹ️ *دستورات `.info`, `.type`, `.count` فعال شدند.*\n\n"
        "--- 🕋 ✨ 🇮🇷 ---\n"
        "**قدرت گرفته توسط امام خمینی**"
    )
    
    print("✅ سلف بات آماده است و به دستورات گوش می‌دهد...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    # --- ۱. سرور بیدارباش را اجرا کن ---
    start_keep_alive_server()
    print("🌀 وب‌سرور بیدارباش (Keep-Alive) فعال شد.")
    
    # --- ۲. ربات اصلی را اجرا کن ---
    # از client.loop.run_until_complete برای اجرای تابع async اصلی استفاده می‌کنیم
    client.loop.run_until_complete(main_bot())
  
