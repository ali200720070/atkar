# bot.py
# Telegram Adhkar Bot - Single file (Telethon)
# install: pip install telethon aiohttp

import os, asyncio, re, hashlib, time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Dict
from collections import defaultdict

from telethon import TelegramClient, events, Button
from telethon.errors.rpcerrorlist import MessageNotModifiedError, MessageIdInvalidError

# =====================[ ACCESS KEYS ]=====================
API_ID    = 10057010
API_HASH  = "fd3b72f8cc70b1cdfc6339536f7990e5"
BOT_TOKEN = "8390591699:AAH4IPdrYDSBXRQx-uqN-i-JxvYA0CCa75I"

# =====================[ SETTINGS ]=====================
TZ = os.getenv("TZ", "Asia/Riyadh")   # توقيت مكة
tz = ZoneInfo(TZ)

DEFAULT_INTERVAL_MIN = 30             # يدعم 15/30/60
MIN_SEND_COOLDOWN = 5                 # ثوان تهدئة لمنع إرسالين متتاليين لنفس المجموعة
SCHEDULER_TICK = 10                   # كل كم ثانية يتفقد المجدول

ENABLE_WEB = os.getenv("ENABLE_WEB", "0") == "1"
WEB_PORT   = int(os.getenv("PORT", "8080"))

# =====================[ DHIKR DATA ]=====================
MORNING_DHIKR = [
    {"t": "﴿ أذكار الصباح ﴾\n🌿 سيد الاستغفار:\n"
          "«اللهم أنت ربي لا إله إلا أنت، خلقتني وأنا عبدك، وأنا على عهدك ووعدك ما استطعت، "
          "أعوذ بك من شر ما صنعت، أبوء لك بنعمتك عليّ، وأبوء بذنبي، "
          "فاغفر لي فإنه لا يغفر الذنوب إلا أنت».", "src": "صحيح البخاري"},
    {"t": "﴿ أذكار الصباح ﴾\n🕊️ «أصبحنا وأصبح الملك لله… ربِّ أسألك خير ما في هذا اليوم… "
          "وأعوذ بك من عذاب في النار وعذاب في القبر».", "src": "صحيح مسلم"},
    {"t": "﴿ أذكار الصباح ﴾\n«لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير» (100).", "hukm": "متفق عليه"},
    {"t": "﴿ أذكار الصباح ﴾\n«سبحان الله وبحمده» (100).", "src": "صحيح مسلم"},
    {"t": "﴿ أذكار الصباح ﴾\n«أعوذ بكلمات الله التامات من شر ما خلق».", "src": "صحيح مسلم"},
]
EVENING_DHIKR = [
    {"t": "﴿ أذكار المساء ﴾\n🌿 سيد الاستغفار:\n"
          "«اللهم أنت ربي لا إله إلا أنت… فاغفر لي فإنه لا يغفر الذنوب إلا أنت».", "src": "صحيح البخاري"},
    {"t": "﴿ أذكار المساء ﴾\n🕊️ «أمسينا وأمسى الملك لله… ربّ أسألك خير ما في هذه الليلة… "
          "وأعوذ بك من عذاب في النار وعذاب في القبر».", "src": "صحيح مسلم"},
    {"t": "﴿ أذكار المساء ﴾\n«لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير» (100).", "hukm": "متفق عليه"},
    {"t": "﴿ أذكار المساء ﴾\n«سبحان الله وبحمده» (100).", "src": "صحيح مسلم"},
    {"t": "﴿ أذكار المساء ﴾\n«أعوذ بكلمات الله التامات من شر ما خلق».", "src": "صحيح مسلم"},
    {"t": "﴿ أذكار المساء ﴾\n«اللهم بك أمسينا وبك أصبحنا، وبك نحيا وبك نموت وإليك المصير».", "src": "صحيح مسلم"},
]
GENERAL_DHIKR = [
    {"t": "﴿ من جوامع الذِّكر ﴾\n🌿 «سبحان الله، والحمد لله، ولا إله إلا الله، والله أكبر».", "hukm": "متفق عليه"},
    {"t": "﴿ من جوامع الذِّكر ﴾\n🕊️ «لا حول ولا قوة إلا بالله».", "hukm": "متفق عليه"},
    {"t": "﴿ من جوامع الذِّكر ﴾\n✨ «سبحان الله وبحمده، سبحان الله العظيم».", "src": "صحيح مسلم"},
    {"t": "﴿ من جوامع الدعاء ﴾\n«اللهم إني أعوذ بك من الهمّ والحَزَن، وأعوذ بك من العجز والكسل، "
          "وأعوذ بك من الجبن والبخل، وأعوذ بك من غلبة الدَّين وقهر الرجال».", "src": "صحيح البخاري"},
    {"t": "﴿ من جوامع الدعاء ﴾\n«اللهم اغسلني من خطاياي بالماء والثلج والبرد، ونقِّ قلبي من الخطايا كما يُنقّى الثوب الأبيض من الدنس».", "hukm": "متفق عليه"},
    {"t": "﴿ من جوامع الدعاء ﴾\n«اللهم إني ظلمتُ نفسي ظلمًا كثيرًا، ولا يغفر الذنوب إلا أنت، فاغفر لي مغفرةً من عندك وارحمني، إنك أنت الغفور الرحيم».", "src": "صحيح مسلم"},
    {"t": "﴿ من جوامع الدعاء ﴾\n«يا مصرف القلوب صرّف قلوبنا على طاعتك».", "src": "صحيح مسلم"},
    {"t": "﴿ من جوامع الذِّكر ﴾\n«سبحان الله وبحمده عدد خلقه، ورضا نفسه، وزنة عرشه، ومداد كلماته».", "src": "صحيح مسلم"},
    {"t": "﴿ من جوامع الدعاء ﴾\n«اللهم إنك عفوٌّ تحب العفو فاعفُ عني».", "src": "صحيح مسلم"},
]

# =====================[ TELEGRAM + IN-MEMORY STATE ]=====================
client = TelegramClient("adhkar-bot", API_ID, API_HASH)

# هيكل الحالة داخل الذاكرة فقط
# لكل مجموعة:
# enabled/next_at/interval_min/cursors/last_key/last_ts/panel_msg_id/panel_inflight
state: Dict = {"chats": {}}

# أقفال لمنع السباقات/التكرار
chat_locks: Dict[int, asyncio.Lock]  = defaultdict(asyncio.Lock)  # قفل الإرسال لكل مجموعة
panel_locks: Dict[int, asyncio.Lock] = defaultdict(asyncio.Lock)  # قفل لوحة /bot لكل مجموعة

SCHEDULER_STARTED = False
SCHEDULER_TASK: asyncio.Task | None = None

# =====================[ HELPERS ]=====================
def ensure_chat(cid: int):
    """تهيئة الحالة لمجموعة ما (مرة واحدة)."""
    s = state["chats"].get(str(cid))
    if s is None:
        state["chats"][str(cid)] = {
            "enabled": False,  # لا يبدأ تلقائيًا
            "next_at": None,
            "interval_min": DEFAULT_INTERVAL_MIN if DEFAULT_INTERVAL_MIN in (15, 30, 60) else 30,
            "cursors": {"morning": 0, "evening": 0, "general": 0},
            "last_key": None,
            "last_ts": 0.0,
            "panel_msg_id": None,
            "panel_inflight": False,
        }

def segment_of_day(now: datetime) -> str:
    h = now.hour
    if 4 <= h < 11:  return "morning"
    if 17 <= h < 24: return "evening"
    return "general"

def _key_for_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:24]

def pick_and_advance(cid: int, now: datetime) -> str:
    seg = segment_of_day(now)
    chat = state["chats"][str(cid)]
    pool = MORNING_DHIKR if seg == "morning" else EVENING_DHIKR if seg == "evening" else GENERAL_DHIKR
    key = seg if seg in ("morning", "evening") else "general"

    cur = chat["cursors"].get(key, 0) % len(pool)
    item = pool[cur]
    chat["cursors"][key] = (cur + 1) % len(pool)

    meta = f"الحكم: {item['hukm']}" if "hukm" in item else f"المصدر: {item.get('src','')}"
    text = f"{item['t']}\n\n{meta}"

    chat["last_key"] = _key_for_text(text)
    return text

def pretty_status(cid: int) -> str:
    s = state["chats"].get(str(cid), {})
    enabled = s.get("enabled", False)
    interval = s.get("interval_min", 30)
    return (
        f"الحالة: {'يعمل ✅' if enabled else 'متوقّف ⏸️'}\n"
        f"الفاصل الزمني الحالي: كل {interval} دقيقة"
    )

# =====================[ KEYBOARDS ]=====================
def main_menu_kb(cid: int):
    enabled = state["chats"].get(str(cid), {}).get("enabled", False)
    toggle_text = "إيقاف البوت ⏸️" if enabled else "تشغيل البوت ▶️"
    toggle_val  = b"off" if enabled else b"on"
    return [
        [Button.inline("كل 15", b"setint:15"),
         Button.inline("كل 30", b"setint:30"),
         Button.inline("كل 60", b"setint:60")],
        [Button.inline("ابدأ الآن 🔔", b"start:now"), Button.inline(toggle_text, b"toggle:" + toggle_val)],
        [Button.inline("تحديث المعلومات ↻", b"refresh"), Button.inline("🗑️ حذف الرسالة", b"panel:close")],
    ]

# =====================[ ADMIN CHECK ]=====================
async def user_is_admin(chat_id: int, user_id: int) -> bool:
    try:
        perm = await client.get_permissions(chat_id, user_id)
        return bool(getattr(perm, "is_admin", False) or getattr(perm, "is_creator", False))
    except Exception:
        return False

# =====================[ SAFE SEND ]=====================
async def safe_send(cid: int, text: str):
    """إرسال آمن: قفل للمجموعة + منع نص مكرر لحظي + تهدئة زمنية."""
    lock = chat_locks[cid]
    async with lock:
        s = state["chats"].get(str(cid), {})
        last_key = s.get("last_key")
        this_key = _key_for_text(text)
        now_ts = time.time()
        if last_key == this_key and (now_ts - s.get("last_ts", 0.0)) < MIN_SEND_COOLDOWN:
            return
        s["last_key"] = this_key
        s["last_ts"]  = now_ts
        await client.send_message(cid, text, link_preview=False)

# =====================[ SCHEDULER ]=====================
async def scheduler():
    global SCHEDULER_STARTED
    if SCHEDULER_STARTED:
        return
    SCHEDULER_STARTED = True

    while True:
        now = datetime.now(tz)
        for cid_str, chat in list(state["chats"].items()):
            try:
                if not chat.get("enabled", False):
                    continue
                next_at = chat.get("next_at")
                if not next_at:
                    interval = chat.get("interval_min", 30)
                    chat["next_at"] = (now + timedelta(minutes=interval)).isoformat()
                    continue
                nxt = datetime.fromisoformat(next_at).astimezone(tz)
                if now >= nxt:
                    text = pick_and_advance(int(cid_str), now)
                    await safe_send(int(cid_str), text)
                    interval = chat.get("interval_min", 30)
                    chat["next_at"] = (now + timedelta(minutes=interval)).isoformat()
            except Exception as e:
                print(f"Send loop error in {cid_str}: {e}")
        await asyncio.sleep(SCHEDULER_TICK)

# =====================[ EVENTS ]=====================
# 1) عند إضافة البوت: لا ترحيب – فقط جهّز الحالة (ولا يبدأ تلقائيًا)
@client.on(events.ChatAction)
async def on_added(event: events.ChatAction.Event):
    try:
        me = await client.get_me()
        if event.user_added:
            for u in event.users:
                if u.id == me.id:
                    ensure_chat(event.chat_id)
                    break
    except Exception:
        pass

# 2) فتح الإعدادات: /bot أو "اعدادات البوت" — للأدمن فقط، لوحـة واحدة فقط
AR_SETTINGS = re.compile(r'^\s*[اإٱآ]?عدادات\s*البوت\s*$', re.IGNORECASE)

@client.on(events.NewMessage(incoming=True))
async def on_cmds(event: events.NewMessage.Event):
    if not event.is_group:
        return
    txt = (event.raw_text or "").strip()
    if not (txt == "/bot" or AR_SETTINGS.match(txt)):
        return

    cid = event.chat_id
    ensure_chat(cid)

    if not await user_is_admin(cid, event.sender_id):
        return await event.reply("هذا الأمر مخصص للإدمن فقط.")

    plock = panel_locks[cid]
    async with plock:
        s = state["chats"][str(cid)]
        if s.get("panel_inflight", False):
            return
        s["panel_inflight"] = True
        try:
            text = pretty_status(cid)
            pmid = s.get("panel_msg_id")
            if pmid:
                try:
                    await client.edit_message(cid, pmid, text, buttons=main_menu_kb(cid))
                    return
                except (MessageIdInvalidError, MessageNotModifiedError):
                    pmid = None
                except Exception:
                    pmid = None
            m = await client.send_message(cid, text, buttons=main_menu_kb(cid))
            s["panel_msg_id"] = m.id
        finally:
            s["panel_inflight"] = False

# 3) أزرار الإعدادات
@client.on(events.CallbackQuery)
async def on_cb(event: events.CallbackQuery.Event):
    cid = event.chat_id
    ensure_chat(cid)

    if not await user_is_admin(cid, event.sender_id):
        return await event.answer("للإدمن فقط.", alert=True)

    data = event.data.decode("utf-8") if isinstance(event.data, (bytes, bytearray)) else str(event.data)
    s = state["chats"].get(str(cid), {})
    pmid = s.get("panel_msg_id")

    if data == "panel:close":
        try:
            if pmid:
                await client.delete_messages(cid, pmid)
        except Exception:
            pass
        s["panel_msg_id"] = None
        return await event.answer("تم حذف الرسالة.")

    if data.startswith("toggle:"):
        val = data.split(":")[1]
        s["enabled"] = (val == "on")
        if s["enabled"] and not s.get("next_at"):
            s["next_at"] = (datetime.now(tz) + timedelta(minutes=s.get("interval_min", 30))).isoformat()
        await event.answer("تم التحديث.")

    elif data == "start:now":
        now = datetime.now(tz)
        text = pick_and_advance(cid, now)
        await safe_send(cid, text)
        s["enabled"] = True
        interval = s.get("interval_min", 30)
        s["next_at"] = (now + timedelta(minutes=interval)).isoformat()
        await event.answer("بدأنا الآن.")

    elif data == "refresh":
        await event.answer("تم التحديث.")

    elif data.startswith("setint:"):
        mins = int(data.split(":")[1])
        s["interval_min"] = mins
        if s.get("enabled", False):
            s["next_at"] = (datetime.now(tz) + timedelta(minutes=mins)).isoformat()
        await event.answer(f"تم ضبط الفاصل: كل {mins} دقيقة.")

    # بعد أي إجراء، اعرض اللوحة الرئيسية (رسالة واحدة فقط)
    try:
        await event.edit(pretty_status(cid), buttons=main_menu_kb(cid))
    except MessageNotModifiedError:
        pass

# =====================[ Keep-Alive (optional) ]=====================
async def start_web():
    try:
        from aiohttp import web
    except Exception:
        return
    async def ping(_): return web.Response(text="OK")
    app = web.Application()
    app.add_routes([web.get("/", ping), web.get("/health", ping)])
    runner = web.AppRunner(app); await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", WEB_PORT)
    await site.start()

# =====================[ MAIN ]=====================
async def main():
    global SCHEDULER_TASK, SCHEDULER_STARTED
    if ENABLE_WEB:
        asyncio.get_running_loop().create_task(start_web())

    await client.start(bot_token=BOT_TOKEN)

    # مجدول واحد فقط
    if not SCHEDULER_STARTED:
        SCHEDULER_TASK = asyncio.get_running_loop().create_task(scheduler())

    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
