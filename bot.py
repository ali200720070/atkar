#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بوت أذكار ثابت للقنوات والمجموعات
- يرسل ذكر لكل دردشة محددة كل 30 ثانية للتجربة
- يبدأ مباشرة عند تشغيل البوت لكل chat_id مذكور
"""

import sys
import subprocess
import logging
from typing import Dict, Optional

# تثبيت الحزمة تلقائياً إن لم تكن موجودة
try:
    import telegram
except Exception:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-telegram-bot==20.3"])

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ChatMemberHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = "8402234547:AAEoQZWPToTRkdHUc5qvy91JQB5619QUG9U"

# قائمة الـ Chat IDs للمجموعات/القنوات التي تريد إرسال الأذكار لها
FIXED_CHAT_IDS = [
    -1003074032990,  # تجارب
    -1003088520407,  # الادراة
    -1003028994230,  # أهل الحق
    -1002986847855,  # سيف الكلمة
]

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", level=logging.INFO)
logger = logging.getLogger("azkar_fixed_bot")

AZKAR_LIST = [
    "🌸 اللَّهُمَّ بِكَ أَصْبَحْنَا وَبِكَ أَمْسَيْنَا ...",
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
    "🍃 اللّهُمَّ صَلِّ وَسَلِّمْ عَلَى نَبِيِّنَا ...",
]

class SimpleAzkarBot:
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(self.token).build()
        self.chat_states: Dict[int, int] = {}
        self.setup_handlers()

    def setup_handlers(self) -> None:
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(ChatMemberHandler(self.track_chats, ChatMemberHandler.MY_CHAT_MEMBER))
        channel_post_filter = filters.UpdateType.CHANNEL_POST
        group_msg_filter = (filters.ChatType.GROUP | filters.ChatType.SUPERGROUP) & ~filters.COMMAND
        self.application.add_handler(MessageHandler(channel_post_filter | group_msg_filter, self.handle_message))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            chat = update.effective_chat
            if chat and chat.type == "private":
                await update.message.reply_text("أهلاً بك\nسيتم إرسال الأذكار للمجموعات المحددة")
        except Exception:
            pass

    def get_next_zikr(self, chat_id: int) -> str:
        if chat_id not in self.chat_states:
            self.chat_states[chat_id] = 0
        idx = self.chat_states[chat_id]
        zikr = AZKAR_LIST[idx]
        self.chat_states[chat_id] = (idx + 1) % len(AZKAR_LIST)
        return zikr

    async def send_zikr(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        job = context.job
        chat_id: Optional[int] = getattr(job, "chat_id", None)
        if chat_id is None:
            return
        last_msg_id = job.data.get("last_message_id") if getattr(job, "data", None) else None
        try:
            if last_msg_id:
                try:
                    await context.bot.delete_message(chat_id=chat_id, message_id=last_msg_id)
                except Exception:
                    pass
            zikr = self.get_next_zikr(chat_id)
            sent = await context.bot.send_message(chat_id=chat_id, text=f"📿 ذكر ودعاء\n\n{zikr}", parse_mode=ParseMode.HTML)
            job.data = {"last_message_id": sent.message_id}
        except Exception as e:
            msg = str(e).lower()
            if "bot was kicked" in msg or "chat not found" in msg or "forbidden" in msg:
                for j in context.job_queue.get_jobs_by_name(str(chat_id)):
                    j.schedule_removal()

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat = update.effective_chat
        if not chat:
            return
        chat_id = chat.id
        existing = context.job_queue.get_jobs_by_name(str(chat_id))
        if not existing:
            title = getattr(chat, "title", str(chat_id))
            logger.info(f"بدء مهمة جديدة للدردشة {title} id={chat_id}")
            self.start_zikr_job(context, chat_id, title)

    async def track_chats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.chat_member:
            return
        chat = update.chat_member.chat
        if not chat:
            return
        new_member = update.chat_member.new_chat_member
        if not new_member:
            return
        try:
            bot_id = context.bot.id
        except Exception:
            return
        if new_member.user.id != bot_id:
            return
        new_status = new_member.status
        if new_status in ("member", "administrator"):
            title = getattr(chat, "title", str(chat.id))
            self.start_zikr_job(context, chat.id, title)

    def start_zikr_job(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, chat_title: str) -> None:
        logger.info(f"بدء/تحديث مهمة الأذكار للدردشة {chat_title} ({chat_id})")
        for job in context.job_queue.get_jobs_by_name(str(chat_id)):
            job.schedule_removal()
        context.job_queue.run_repeating(callback=self.send_zikr, interval=30, first=1, name=str(chat_id), chat_id=chat_id, data={})

    def run(self) -> None:
        # بدء مهام الأذكار مباشرة لكل Chat ID ثابت
        for chat_id in FIXED_CHAT_IDS:
            self.start_zikr_job(self.application.bot_data, chat_id, str(chat_id))
        logger.info("تشغيل بوت الأذكار بالـ polling")
        self.application.run_polling()

def main() -> None:
    if not BOT_TOKEN or BOT_TOKEN.strip() == "":
        logger.error("لم يتم تهيئة التوكن BOT_TOKEN داخل الملف")
        return
    bot = SimpleAzkarBot(BOT_TOKEN)
    bot.run()

if __name__ == "__main__":
    main()
