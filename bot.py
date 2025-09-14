#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بوت أذكار باستخدام asyncio فقط بدون JobQueue
- يبدأ مباشرة لكل chat_id
- يرسل ذكر كل 30 ثانية للتجربة
- يحذف الرسالة السابقة إن أمكن
"""

import sys
import subprocess
import logging
import asyncio

# تثبيت المكتبة تلقائيًا
try:
    import telegram
    from telegram import ParseMode
    from telegram.ext import Application, CommandHandler, ContextTypes
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-telegram-bot==20.3"])
    import telegram
    from telegram import ParseMode
    from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = "8402234547:AAEoQZWPToTRkdHUc5qvy91JQB5619QUG9U"

FIXED_CHAT_IDS = [
    -1003074032990,
    -1003088520407,
    -1003028994230,
    -1002986847855,
]

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("azkar_bot")

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

class AzkarBot:
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(self.token).build()
        self.chat_states = {}  # chat_id -> index
        self.last_messages = {}  # chat_id -> message_id

    async def start(self, update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("أهلاً بك، سيتم إرسال الأذكار لكل المجموعات المحددة!")

    async def zikr_loop(self):
        """حلقة مستمرة لإرسال الأذكار لكل الدردشات"""
        while True:
            for chat_id in FIXED_CHAT_IDS:
                index = self.chat_states.get(chat_id, 0)
                text = AZKAR_LIST[index]
                try:
                    last_msg_id = self.last_messages.get(chat_id)
                    if last_msg_id:
                        await self.application.bot.delete_message(chat_id=chat_id, message_id=last_msg_id)
                except Exception:
                    pass
                try:
                    sent = await self.application.bot.send_message(
                        chat_id=chat_id,
                        text=f"📿 ذكر ودعاء\n\n{text}",
                        parse_mode=ParseMode.HTML
                    )
                    self.last_messages[chat_id] = sent.message_id
                    self.chat_states[chat_id] = (index + 1) % len(AZKAR_LIST)
                except Exception as e:
                    logger.error(f"خطأ في إرسال ذكر إلى {chat_id}: {e}")
            await asyncio.sleep(30)  # للتجربة، يمكن تغييره لـ 7200 = ساعتين

    def run(self):
        self.application.add_handler(CommandHandler("start", self.start))
        logger.info("تشغيل بوت الأذكار")
        # تشغيل البوت وحلقة الأذكار
        async def main_async():
            # بدء الحلقة بدون JobQueue
            asyncio.create_task(self.zikr_loop())
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            await self.application.updater.idle()
        asyncio.run(main_async())

if __name__ == "__main__":
    bot = AzkarBot(BOT_TOKEN)
    bot.run()
