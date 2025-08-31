# bot.py
# Telegram Adhkar Bot - Single file (Telethon)
# تثبيت: pip install telethon aiohttp

import os, json, asyncio, re, hashlib
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Dict
from collections import defaultdict

from telethon import TelegramClient, events, Button
from telethon.errors.rpcerrorlist import MessageNotModifiedError

# =====================[ مفاتيح الوصول ]=====================
API_ID    = 10057010
API_HASH  = "fd3b72f8cc70b1cdfc6339536f7990e5"
BOT_TOKEN = "8390591699:AAH4IPdrYDSBXRQx-uqN-i-JxvYA0CCa75I"

# =====================[ إعدادات عامة ]=====================
tz = ZoneInfo(os.getenv("TZ", "Asia/Riyadh"))   # توقيت مكة
STATE_FILE = "state.json"
DEFAULT_INTERVAL_MIN = 30                        # يدعم 15/30/60
ENABLE_WEB = os.getenv("ENABLE_WEB", "0") == "1" # افتراضيًا معطل على Railway worker
WEB_PORT   = int(os.getenv("PORT", "8080"))

# =====================[ بيانات الأذكار/الأدعية ]=====================
# بدون فواصل/خطوط في الرسالة. إيموجيات هادئة. مصادر صحيحة فقط.
MORNING_DHIKR = [
    {"t": "﴿ أذكار الصباح ﴾\n🌿 سيد الاستغفار:\n"
          "«اللهم أنت ربي لا إله إلا أنت، خلقتني وأنا عبدك، وأنا على عهدك ووعدك ما استطعت، "
          "أعوذ بك من شر ما صنعت، أبوء لك بنعمتك عليّ، وأبوء بذنبي، "
          "فاغفر لي فإنه لا يغفر الذنوب إلا أنت».",
     "src": "صحيح البخاري"},
    {"t": "﴿ أذكار الصباح ﴾\n🕊️ «أصبحنا وأصبح الملك لله… ربِّ أسألك خير ما في هذا اليوم… "
          "وأعوذ بك من عذاب في النار وعذاب في القبر».",
     "src": "صحيح مسلم"},
    {"t": "﴿ أذكار الصباح ﴾\n"
          "«لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير» (100).",
     "hukm": "متفق عليه"},
    {"t": "﴿ أذكار الصباح ﴾\n«سبحان الله وبحمده» (100).", "src": "صحيح مسلم"},
    {"t": "﴿ أذكار الصباح ﴾\n«أعوذ بكلمات الله التامات من شر ما خلق».", "src": "صحيح مسلم"},
    {"t": "﴿ أذكار الصباح ﴾\n«اللهم ما أصبح بي من نعمةٍ فمنك وحدك لا شريك لك، فلك الحمد ولك الشكر».",
     "src": "صحيح مسلم"},
    {"t": "﴿ أذكار الصباح ﴾\n«حَسْبِيَ اللهُ لا إله إلا هو، عليه توكلتُ وهو رب العرش العظيم» (7).",
     "src": "صحيح مسلم"},
]

EVENING_DHIKR = [
    {"t": "﴿ أذكار المساء ﴾\n🌿 سيد الاستغفار:\n"
          "«اللهم أنت ربي لا إله إلا أنت… فاغفر لي فإنه لا يغفر الذنوب إلا أنت».",
     "src": "صحيح البخاري"},
    {"t": "﴿ أذكار المساء ﴾\n🕊️ «أمسينا وأمسى الملك لله… ربّ أسألك خير ما في هذه الليلة… "
          "وأعوذ بك من عذاب في النار وعذاب في القبر».",
     "src": "صحيح مسلم"},
    {"t": "﴿ أذكار المساء ﴾\n"
          "«لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير» (100).",
     "hukm": "متفق عليه"},
    {"t": "﴿ أذكار المساء ﴾\n«سبحان الله وبحمده» (100).", "src": "صحيح مسلم"},
    {"t": "﴿ أذكار المساء ﴾\n«أعوذ بكلمات الله التامات من شر ما خلق».", "src": "صحيح مسلم"},
    {"t": "﴿ أذكار المساء ﴾\n«اللهم بك أمسينا وبك أصبحنا، وبك نحيا وبك نموت وإليك المصير».",
     "src": "صحيح مسلم"},
]

GENERAL_DHIKR = [
    {"t": "﴿ من جوامع الذِّكر ﴾\n🌿 «سبحان الله، والحمد لله، ولا إله إلا الله، والله أكبر».",
     "hukm": "متفق عليه"},
    {"t": "﴿ من جوامع الذِّكر ﴾\n🕊️ «لا حول ولا قوة إلا بالله».", "hukm": "متفق عليه"},
    {"t": "﴿ من جوامع الذِّكر ﴾\n✨ «سبحان الله وبحمده، سبحان الله العظيم».", "src": "صحيح مسلم"},
    {"t": "﴿ من جوامع الدعاء ﴾\n"
          "«اللهم إني أعوذ بك من الهمّ والحَزَن، وأعوذ بك من العجز والكسل، "
          "وأعوذ بك من الجبن والبخل، وأعوذ بك من غلبة الدَّين وقهر الرجال».",
     "src": "صحيح البخاري"},
    {"t": "﴿ من جوامع الدعاء ﴾\n"
          "«اللهم اغسلني من خطاياي بالماء والثلج والبرد، ونقِّ قلبي من الخطايا كما يُنقّى الثوب الأبيض من الدنس».",
     "hukm": "متفق عليه"},
    {"t": "﴿ من جوامع الدعاء ﴾\n"
          "«اللهم إني ظلمتُ نفسي ظلمًا كثيرًا، ولا يغفر الذنوب إلا أنت، "
          "فاغفر لي مغفرةً من عندك وارحمني، إنك أنت الغفور الرحيم».",
     "src": "صحيح مسلم"},
    {"t": "﴿ من جوامع الدعاء ﴾\n«يا مصرف القلوب صرّف قلوبنا على طاعتك».", "src": "صحيح مسلم"},
    {"t": "﴿ من جوامع الذِّكر ﴾\n«سبحان الله وبحمده عدد خلقه، ورضا نفسه، وزنة عرشه، ومداد كلماته».",
     "src": "صحيح مسلم"},
    {"t": "﴿ من جوامع الدعاء ﴾\n«اللهم إنك عفوٌّ تحب العفو فاعفُ عني».", "src": "صحيح مسلم"},
]

# =====================[ عميل تليجرام والحالة ]=====================
client = TelegramClient("adhkar-bot", API_ID, API_HASH)

# هيكل الحالة لكل مجموعة:
# enabled / next_at / interval_min / cursors / last_key / start_cooldown_until
state: Dict = {"chats": {}}

# قفل لكل مجموعة + حارس المجدول
chat_locks: Dict[int, asyncio.Lock] = defaultdict(asyncio.Lock)
SCHEDULER_STARTED = False

def load_state():
    global state
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
    except FileNotFoundError:
        state = {"chats": {}}
    except Exception:
        state = {"chats": {}}

def save_state():
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def ensure_chat(cid: int):
    s = state["chats"].get(str(cid))
    if not s:
        now = datetime.now(tz)
        interval = DEFAULT_INTERVAL_MIN if DEFAULT_INTERVAL_MIN in (15, 30, 60) else 30
        state["chats"][str(cid)] = {
            "enabled": True,
            "next_at": (now + timedelta(seconds=1)).isoformat(),  # يبدأ سريعًا
            "interval_min": interval,
            "cursors": {"morning": 0, "evening": 0, "general": 0},
            "last_key": None,
            "start_cooldown_until": None,
        }
        save_state()

def segment_of_day(now: datetime) -> str:
    h = now.hour
    if 4 <= h < 11:  return "morning"
    if 17 <= h < 24: return "evening"
    return "general"

def _key_for_item(text: str) -> str:
    # مفتاح ازدواج يعتمد على نص الذكر فقط
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

    # خزّن المفتاح الجديد واحفظ الحالة
    chat["last_key"] = _key_for_item(text)
    save_state()
    return text

def pretty_status(cid: int) -> str:
    s = state["chats"].get(str(cid), {})
    enabled = s.get("enabled", True)
    interval = s.get("interval_min", 30)
    seg = segment_of_day(datetime.now(tz))
    seg_ar = {"morning":"الصباح","evening":"المساء","general":"الوقت العام"}[seg]
    return (
        f"الحالة: {'يعمل ✅' if enabled else 'متوقّف ⏸️'}\n"
        f"الوضع الزمني الآن: {seg_ar}\n"
        f"الفاصل الزمني: كل {interval} دقيقة"
    )

# =====================[ الواجهات ]=====================
def main_menu_kb(cid: int):
    enabled = state["chats"].get(str(cid), {}).get("enabled", True)
    toggle_text = "إيقاف البوت ⏸️" if enabled else "تشغيل البوت ▶️"
    toggle_val  = b"off" if enabled else b"on"
    return [
        [Button.inline(toggle_text, b"toggle:" + toggle_val)],
        [Button.inline("ضبط الفاصل (15/30/60)", b"menu:interval")],
        [Button.inline("ابدأ الآن 🔔", b"start:now")],
        [Button.inline("تحديث الحالة ↻", b"refresh")],
    ]

def interval_menu_kb():
    return [
        [Button.inline("كل 15 دقيقة", b"setint:15"),
         Button.inline("كل 30 دقيقة", b"setint:30"),
         Button.inline("كل 60 دقيقة", b"setint:60")],
        [Button.inline("رجوع ↩️", b"menu:main")]
    ]

# =====================[ صلاحيات الأدمن ]=====================
async def user_is_admin(chat_id: int, user_id: int) -> bool:
    try:
        perm = await client.get_permissions(chat_id, user_id)
        return bool(getattr(perm, "is_admin", False) or getattr(perm, "is_creator", False))
    except Exception:
        return False

# =====================[ الجدولة مع منع التكرار ]=====================
async def safe_send(cid: int, text: str):
    """إرسال آمن برسالة واحدة فقط مع قفل المجموعة."""
    lock = chat_locks[cid]
    async with lock:
        # تحقّق من عدم تكرار نفس النص للتو
        s = state["chats"].get(str(cid), {})
        last_key = s.get("last_key")
        this_key = _key_for_item(text)
        if last_key == this_key:
            return  # نص مطابق تم إرساله آخر مرة
        # مرّر المفتاح الجديد واحفظ
        s["last_key"] = this_key
        save_state()
        await client.send_message(cid, text, link_preview=False)

async def scheduler():
    global SCHEDULER_STARTED
    if SCHEDULER_STARTED:
        return  # منع تشغيل مجدول مزدوج
    SCHEDULER_STARTED = True

    load_state()
    while True:
        now = datetime.now(tz)
        for cid_str, chat in list(state["chats"].items()):
            try:
                if not chat.get("enabled", True):
                    continue

                # جدول الإرسال
                next_at = chat.get("next_at")
                if not next_at:
                    chat["next_at"] = (now + timedelta(minutes=chat.get("interval_min", 30))).isoformat()
                    save_state()
                    continue

                nxt = datetime.fromisoformat(next_at).astimezone(tz)
                if now >= nxt:
                    # التقط الذكر واحجز المفتاح داخل الدالة
                    text = pick_and_advance(int(cid_str), now)
                    await safe_send(int(cid_str), text)

                    interval = chat.get("interval_min", 30)
                    chat["next_at"] = (now + timedelta(minutes=interval)).isoformat()
                    save_state()
            except Exception as e:
                print(f"Send loop error in {cid_str}: {e}")
                continue
        await asyncio.sleep(15)  # تكرار أسرع بدرجة آمنة

# =====================[ الأحداث ]=====================
# (1) لا ترحيب عند الانضمام؛ فقط تأكيد الحالة
@client.on(events.ChatAction)
async def on_new_members(event: events.ChatAction.Event):
    try:
        me = await client.get_me()
        if event.user_added:
            for u in event.users:
                if u.id == me.id:
                    ensure_chat(event.chat_id)  # بدون أي رسالة
                    break
    except Exception:
        pass

# (2) فتح الإعدادات: "اعدادات البوت" أو /bot — للأدمن فقط
# يدعم مسافات متعددة وهمزات مختلفة
AR_SETTINGS = re.compile(r'^\s*[اإٱآ]?عدادات\s*البوت\s*$', re.IGNORECASE)
@client.on(events.NewMessage)
async def on_cmds(event: events.NewMessage.Event):
    if not event.is_group:
        return

    txt = (event.raw_text or "").strip()
    if txt == "/bot" or AR_SETTINGS.match(txt):
        ensure_chat(event.chat_id)
        if not await user_is_admin(event.chat_id, event.sender_id):
            return await event.reply("هذا الأمر مخصص للإدمن فقط.")
        return await event.reply(pretty_status(event.chat_id), buttons=main_menu_kb(event.chat_id))

# (3) الأزرار
@client.on(events.CallbackQuery)
async def on_cb(event: events.CallbackQuery.Event):
    cid = event.chat_id
    ensure_chat(cid)
    if not await user_is_admin(cid, event.sender_id):
        return await event.answer("للإدمن فقط.", alert=True)

    data = event.data.decode("utf-8") if isinstance(event.data, (bytes, bytearray)) else str(event.data)
    changed = False

    if data.startswith("toggle:"):
        val = data.split(":")[1]
        state["chats"][str(cid)]["enabled"] = (val == "on")
        if val == "on":
            state["chats"][str(cid)]["next_at"] = (datetime.now(tz) + timedelta(seconds=1)).isoformat()
        save_state(); changed = True
        await event.answer("تم التحديث.")

    elif data == "start:now":
        now = datetime.now(tz)
        chat = state["chats"][str(cid)]
        # تبريد ضغط زر "ابدأ الآن" لعدم التكرار
        cooldown_until = chat.get("start_cooldown_until")
        if cooldown_until and datetime.fromisoformat(cooldown_until) > now:
            return await event.answer("انتظر ثوانٍ من فضلك.", alert=False)

        text = pick_and_advance(cid, now)
        await safe_send(cid, text)
        interval = chat.get("interval_min", 30)
        chat["next_at"] = (now + timedelta(minutes=interval)).isoformat()
        chat["start_cooldown_until"] = (now + timedelta(seconds=10)).isoformat()
        save_state(); changed = True
        await event.answer("بدأنا الآن.")

    elif data == "refresh":
        await event.answer("تم التحديث.")

    elif data == "menu:interval":
        text = "اختر الفاصل الزمني للإرسال:"
        try:
            msg = await event.get_message()
            if msg.message != text:
                await event.edit(text, buttons=interval_menu_kb())
            else:
                await event.edit(buttons=interval_menu_kb())
        except MessageNotModifiedError:
            pass
        return

    elif data == "menu:main":
        # رجوع للقائمة الرئيسية
        changed = True

    elif data.startswith("setint:"):
        mins = int(data.split(":")[1])
        state["chats"][str(cid)]["interval_min"] = mins
        state["chats"][str(cid)]["next_at"] = (datetime.now(tz) + timedelta(seconds=1)).isoformat()
        save_state(); changed = True
        await event.answer(f"تم ضبط الفاصل: كل {mins} دقيقة.")

    # عرض الحالة والقائمة الرئيسية دائماً بعد أي تغيير/رجوع
    text = pretty_status(cid)
    try:
        msg = await event.get_message()
        if msg.message != text or changed:
            await event.edit(text, buttons=main_menu_kb(cid))
        else:
            await event.edit(buttons=main_menu_kb(cid))
    except MessageNotModifiedError:
        pass

# =====================[ Keep-Alive (اختياري) ]=====================
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

# =====================[ تشغيل ]=====================
async def main():
    load_state()
    if ENABLE_WEB:
        asyncio.get_running_loop().create_task(start_web())
    await client.start(bot_token=BOT_TOKEN)

    # شغّل مجدول واحد فقط مهما حصل
    asyncio.get_running_loop().create_task(scheduler())

    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
