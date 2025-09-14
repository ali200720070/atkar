#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بوت أذكار ثابت للقنوات والمجموعات
- يبدأ مباشرة عند تشغيل البوت لكل chat_id محدد
- يرسل ذكر كل 30 ثانية للتجربة
- يحذف الرسالة السابقة إن أمكن
"""

import sys
import subprocess
import logging
from typing import Dict

# تثبيت المكتبة تلقائياً إذا لم تكن مثبتة
try:
    import telegram
except Exception:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-telegram-bot==20.3"])

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    JobQueue,
)

# التوكن
BOT_TOKEN = "8402234547:AAEoQZWPToTRkdHUc5qvy91JQB5619QUG9U"

# قائمة الدردشات
FIXED_CHAT_IDS = [
    -1003074032990,  # تجارب
    -1003088520407,  # الادراة
    -1003028994230,  # أهل الحق
    -1002986847855,  # سيف الكلمة
]

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("azkar_bot")

# قائمة الأذكار
AZKAR_LIST = [
    "🌸 اللَّهُمَّ بِكَ أَصْبَحْنَا وَبِكَ أَمْسَيْنَا وَبِكَ نَحْيَا وَبِكَ نَمُوتُ وَإِلَيْكَ النُّشُورُ",
    "🍃 اللّهُمَّ أَنْتَ رَبِّي لَا إِلَهَ إِلَّا أَنْتَ ...",
    "🌿 لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ ...",
    "📖 ﴿اللَّهُ لَا إِلَهَ إِلَّا هُوَ الْحَيُّ ...﴾",
    "🌸 يَا حَيُّ يَا قَيُّومُ بِرَحْمَتِكَ ...",
    "🍃 بِسْمِ اللَّهِ الَّذِي لَا يَضُرُّ ...",
    "🌿 اللّهُمَّ إِنِّي أَسْأَلُكَ مِنَ الْخَيْرِ ...",
    "🌸 اللّهُمَّ أَصْلِحْ لِي دِينِي ...",
    "🍃 اللّهُمَّ رَبَّنَا آتِنَا فِي الدُّنْيَا ...",
    "🌿 يَا مُقَلِّبَ الْقُلُوبِ ثَبِّتْ قَلْبِي ...",
    "🌸 رَبِّ اغْفِرْ لِي وَتُبْ عَلَيَّ ...",
    "🍃 اللّهُمَّ صَلِّ وَسَلِّمْ عَلَى نَبِيِّنَا ..."
]

class AzkarBot:
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(self.token).build()
        self.chat_states: Dict[int, int] = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("أهلاً بك، سيتم إرسال الأذكار لكل المجموعات المحددة!")

    async def send_zikr(self, context: ContextTypes.DEFAULT_TYPE):
        job = context.job
        chat_id = job.chat_id
        last_msg_id = job.data.get("last_message_id") if hasattr(job, "data") else None

        try:
            if last_msg_id:
                await context.bot.delete_message(chat_id=chat_id, message_id=last_msg_id)
        except Exception:
            pass

        index = self.chat_states.get(chat_id, 0)
        text = AZKAR_LIST[index]
        sent = await context.bot.send_message(chat_id=chat_id, text=f"📿 ذكر ودعاء\n\n{text}", parse_mode=ParseMode.HTML)
        self.chat_states[chat_id] = (index + 1) % len(AZKAR_LIST)
        job.data = {"last_message_id": sent.message_id}

    def run(self):
        # أمر start في الخاص
        self.application.add_handler(CommandHandler("start", self.start))
        # بدء التطبيق بالـ polling
        app = self.application
        # بعد تشغيل التطبيق، نضيف المهام لكل Chat ID
        async def start_jobs(app: Application):
            for chat_id in FIXED_CHAT_IDS:
                app.job_queue.run_repeating(
                    callback=self.send_zikr,
                    interval=30,  # للتجربة: كل 30 ثانية
                    first=1,
                    chat_id=chat_id,
                    data={}
                )
        app.post_init = start_jobs
        logger.info("تشغيل بوت الأذكار")
        app.run_polling()

def main():
    bot = AzkarBot(BOT_TOKEN)
    bot.run()

if __name__ == "__main__":
    main()
