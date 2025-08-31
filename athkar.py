# bot.py
# Telegram Adhkar Bot - Single file (Telethon)
# تثبيت: pip install telethon aiohttp

import os, json, asyncio, re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Dict
from telethon import TelegramClient, events, Button
from telethon.errors.rpcerrorlist import MessageNotModifiedError

# =====================[ مفاتيح الوصول ]=====================
# وضع القيم داخل الكود لتسهيل التشغيل كما طلبت.
API_ID    = 10057010
API_HASH  = "fd3b72f8cc70b1cdfc6339536f7990e5"
BOT_TOKEN = "8390591699:AAH4IPdrYDSBXRQx-uqN-i-JxvYA0CCa75I"

# =====================[ إعدادات عامة ]=====================
tz = ZoneInfo(os.getenv("TZ", "Asia/Riyadh"))  # توقيت مكة
STATE_FILE = "state.json"
DEFAULT_INTERVAL_MIN = 30                      # يدعم 15/30/60
ENABLE_WEB = os.getenv("ENABLE_WEB", "1") == "1"
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

    # إضافات صباحية صحيحة
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

    # إضافات مسائية صحيحة
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

    # إضافات صحيحة مختصرة
    {"t": "﴿ من جوامع الذِّكر ﴾\n«سبحان الله وبحمده عدد خلقه، ورضا نفسه، وزنة عرشه، ومداد كلماته».",
     "src": "صحيح مسلم"},
    {"t": "﴿ من جوامع الدعاء ﴾\n«اللهم إنك عفوٌّ تحب العفو فاعفُ عني».", "src": "صحيح مسلم"},
]

# =====================[ تهيئة العميل والحالة ]=====================
client = TelegramClient("adhkar-bot", API_ID, API_HASH)

# هيكل الحالة لكل مجموعة:
# enabled/next_at/interval_min/cursors
state: Dict = {"chats": {}}

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
    if str(cid) not in state["chats"]:
        now = datetime.now(tz)
        interval = DEFAULT_INTERVAL_MIN if DEFAULT_INTERVAL_MIN in (15, 30, 60) else 30
        state["chats"][str(cid)] = {
            "enabled": True,
            "next_at": (now + timedelta(seconds=1)).isoformat(),  # يبدأ سريعًا
            "interval_min": interval,
            "cursors": {"morning": 0, "evening": 0, "general": 0},
        }
        save_state()

def segment_of_day(now: datetime) -> str:
    h = now.hour
    if 4 <= h < 11:  return "morning"
    if 17 <= h < 24: return "evening"
    return "general"

def pick_and_advance(cid: int, now: datetime) -> str:
    seg = segment_of_day(now)
    chat = state["chats"][str(cid)]
    pool = MORNING_DHIKR if seg == "morning" else EVENING_DHIKR if seg == "evening" else GENERAL_DHIKR
    key = seg if seg in ("morning", "evening") else "general"

    cur = chat["cursors"].get(key, 0) % len(pool)
    item = pool[cur]
    chat["cursors"][key] = (cur + 1) % len(pool)
    save_state()

    meta = f"الحكم: {item['hukm']}" if "hukm" in item else f"المصدر: {item.get('src','')}"
    return f"{item['t']}\n\n{meta}"

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

# =====================[ الجدولة ]=====================
async def scheduler():
    load_state()
    while True:
        now = datetime.now(tz)
        for cid_str, chat in list(state["chats"].items()):
            try:
                if not chat.get("enabled", True):
                    continue
                next_at = chat.get("next_at")
                if not next_at:
                    chat["next_at"] = (now + timedelta(minutes=chat.get("interval_min", 30))).isoformat()
                    save_state()
                    continue
                nxt = datetime.fromisoformat(next_at).astimezone(tz)
                if now >= nxt:
                    text = pick_and_advance(int(cid_str), now)
                    await client.send_message(int(cid_str), text, link_preview=False)
                    interval = chat.get("interval_min", 30)
                    chat["next_at"] = (now + timedelta(minutes=interval)).isoformat()
                    save_state()
            except Exception as e:
                print(f"Send loop error in {cid_str}: {e}")
                continue
        await asyncio.sleep(30)

# =====================[ معالجات الأحداث ]=====================
# 1) عدم إرسال أي رسالة ترحيب عند إضافة البوت للمجموعة
@client.on(events.ChatAction)
async def on_new_members(event: events.ChatAction.Event):
    try:
        me = await client.get_me()
        if event.user_added:
            for u in event.users:
                if u.id == me.id:
                    ensure_chat(event.chat_id)   # إعداد الحالة فقط بلا ترحيب
                    break
    except Exception:
        pass

# 2) فتح الإعدادات بكتابة "اعدادات البوت" أو الأمر /bot — للأدمن فقط
@client.on(events.NewMessage(pattern=r'^(?:/bot|[اإإؤء]*عدادات\s*البوت)$'))
async def on_bot_cmd(event: events.NewMessage.Event):
    if not event.is_group:
        return
    ensure_chat(event.chat_id)
    if not await user_is_admin(event.chat_id, event.sender_id):
        return await event.reply("هذا الأمر مخصص للإدمن فقط.")
    await event.reply(pretty_status(event.chat_id), buttons=main_menu_kb(event.chat_id))

# 3) الأزرار التفاعلية
@client.on(events.CallbackQuery)
async def on_cb(event: events.CallbackQuery.Event):
    cid = event.chat_id
    ensure_chat(cid)
    if not await user_is_admin(cid, event.sender_id):
        return await event.answer("للإدمن فقط.", alert=True)

    data = event.data.decode("utf-8") if isinstance(event.data, (bytes, bytearray)) else str(event.data)

    if data.startswith("toggle:"):
        val = data.split(":")[1]
        state["chats"][str(cid)]["enabled"] = (val == "on")
        if val == "on":
            state["chats"][str(cid)]["next_at"] = (datetime.now(tz) + timedelta(seconds=1)).isoformat()
        save_state()
        await event.answer("تم التحديث.")

    elif data == "start:now":
        now = datetime.now(tz)
        text = pick_and_advance(cid, now)
        await client.send_message(cid, text, link_preview=False)
        interval = state["chats"][str(cid)].get("interval_min", 30)
        state["chats"][str(cid)]["next_at"] = (now + timedelta(minutes=interval)).isoformat()
        save_state()
        await event.answer("بدأنا الآن.")

    elif data == "refresh":
        await event.answer("تم التحديث.")

    elif data == "menu:interval":
        text = "اختر الفاصل الزمني للإرسال:"
        try:
            if (await event.get_message()).message != text:
                await event.edit(text, buttons=interval_menu_kb())
            else:
                await event.edit(buttons=interval_menu_kb())
        except MessageNotModifiedError:
            pass
        return

    elif data == "menu:main":
        pass  # رجوع للقائمة الرئيسية

    elif data.startswith("setint:"):
        mins = int(data.split(":")[1])
        state["chats"][str(cid)]["interval_min"] = mins
        state["chats"][str(cid)]["next_at"] = (datetime.now(tz) + timedelta(seconds=1)).isoformat()
        save_state()
        await event.answer(f"تم ضبط الفاصل: كل {mins} دقيقة.")

    text = pretty_status(cid)
    try:
        if (await event.get_message()).message != text:
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
    asyncio.get_running_loop().create_task(scheduler())
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())