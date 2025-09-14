import asyncio
import logging
from telethon import TelegramClient, events

# ===== إعدادات البوت =====
API_ID = 29789809
API_HASH = "0de38c2562a2b5a6bef9047db3d681de"
BOT_TOKEN = "8402234547:AAEoQZWPToTRkdHUc5qvy91JQB5619QUG9U"

# ===== القروبات =====
CHAT_IDS = [
    -1003074032990,
    -1003088520407,
    -1003028994230,
    -1002986847855,
]

# ===== قائمة الأذكار =====
import asyncio
import logging
from telethon import TelegramClient, events

# ===== إعدادات البوت =====
API_ID = 29789809
API_HASH = "0de38c2562a2b5a6bef9047db3d681de"
BOT_TOKEN = "8402234547:AAEoQZWPToTRkdHUc5qvy91JQB5619QUG9U"

# ===== القروبات =====
CHAT_IDS = [
    -1003074032990,
    -1003088520407,
    -1003028994230,
    -1002986847855,
]

# ===== قائمة الأذكار =====
AZKAR_LIST = [
    "🌸 اللَّهُمَّ بِكَ أَصْبَحْنَا ...",
    "🍃 اللّهُمَّ أَنْتَ رَبِّي ...",
    "🌿 لَا إِلَهَ إِلَّا اللَّهُ ...",
    "📖 ﴿اللَّهُ لَا إِلَهَ إِلَّا هُوَ ...﴾",
    "🌸 يَا حَيُّ يَا قَيُّومُ ...",
    "🍃 بِسْمِ اللَّهِ الَّذِي لَا يَضُرُّ ...",
    "🌿 اللّهُمَّ إِنِّي أَسْأَلُكَ ...",
    "🌸 اللّهُمَّ أَصْلِحْ لِي دِينِي ...",
    "🍃 اللّهُمَّ رَبَّنَا آتِنَا ...",
    "🌿 يَا مُقَلِّبَ الْقُلُوبِ ...",
    "🌸 رَبِّ اغْفِرْ لِي وَتُبْ عَلَيَّ ...",
    "🍃 اللّهُمَّ صَلِّ وَسَلِّمْ عَلَى نَبِيِّنَا ..."
]

# ===== الإعدادات =====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("azkar_bot")

chat_states = {chat_id: 0 for chat_id in CHAT_IDS}
last_messages = {}

# ===== إنشاء العميل =====
client = TelegramClient('azkar_bot_session', API_ID, API_HASH)

async def send_azkar_loop():
    await client.start(bot_token=BOT_TOKEN)
    logger.info("البوت متصل وجاهز للإرسال")
    while True:
        for chat_id in CHAT_IDS:
            index = chat_states[chat_id]
            text = AZKAR_LIST[index]
            try:
                # حذف الرسالة السابقة إذا موجودة
                if chat_id in last_messages:
                    await client.delete_messages(chat_id, last_messages[chat_id])
            except Exception:
                pass
            try:
                msg = await client.send_message(chat_id, f"📿 ذكر ودعاء\n\n{text}")
                last_messages[chat_id] = msg.id
                chat_states[chat_id] = (index + 1) % len(AZKAR_LIST)
            except Exception as e:
                logger.error(f"خطأ عند الإرسال لـ {chat_id}: {e}")
        await asyncio.sleep(30)

# ===== أمر /start =====
@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.reply("أهلاً! سيتم إرسال الأذكار تلقائيًا لجميع القروبات المحددة.")

# ===== تشغيل البوت =====
async def main():
    await client.start(bot_token=BOT_TOKEN)
    logger.info("تشغيل بوت الأذكار")
    client.loop.create_task(send_azkar_loop())
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())

# ===== الإعدادات =====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("azkar_bot")

chat_states = {chat_id: 0 for chat_id in CHAT_IDS}
last_messages = {}

# ===== إنشاء العميل =====
client = TelegramClient('azkar_bot_session', API_ID, API_HASH)

async def send_azkar_loop():
    await client.start(bot_token=BOT_TOKEN)
    logger.info("البوت متصل وجاهز للإرسال")
    while True:
        for chat_id in CHAT_IDS:
            index = chat_states[chat_id]
            text = AZKAR_LIST[index]
            try:
                # حذف الرسالة السابقة إذا موجودة
                if chat_id in last_messages:
                    await client.delete_messages(chat_id, last_messages[chat_id])
            except Exception:
                pass
            try:
                msg = await client.send_message(chat_id, f"📿 ذكر ودعاء\n\n{text}")
                last_messages[chat_id] = msg.id
                chat_states[chat_id] = (index + 1) % len(AZKAR_LIST)
            except Exception as e:
                logger.error(f"خطأ عند الإرسال لـ {chat_id}: {e}")
        await asyncio.sleep(30)

# ===== أمر /start =====
@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.reply("أهلاً! سيتم إرسال الأذكار تلقائيًا لجميع القروبات المحددة.")

# ===== تشغيل البوت =====
async def main():
    await client.start(bot_token=BOT_TOKEN)
    logger.info("تشغيل بوت الأذكار")
    client.loop.create_task(send_azkar_loop())
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())

