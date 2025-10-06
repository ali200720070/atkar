# -*- coding: utf-8 -*-
# Azkar Telegram Bot — Telethon (BOT SAFE: no GetDialogs)
# يرسل ذكراً كل ساعتين لكل هدف محدد أو يُضاف إليه
# قبل كل إرسال يحذف رسالته السابقة في تلك الدردشة

import os, json, asyncio, signal
from telethon import TelegramClient, events, errors

# ===== مفاتيح الوصول (حسب طلبك) =====
API_ID   = 29789809
API_HASH = "0de38c2562a2b5a6bef9047db3d681de"
BOT_TOKEN = "8402234547:AAEoQZWPToTRkdHUc5qvy91JQB5619QUG9U"

# ===== الإعدادات =====
STATE_PATH = "state.json"            # حالة آخر رسالة + موضع الذكر + الأهداف
PERIOD_SECONDS = 60*60*2             # كل ساعتين
PURGE_ON_START = True                # تنظيف رسائل البوت القديمة عند الإقلاع

# ضع هنا القنوات/المجاميع التي تريد النشر لها (اختياري للكروبات، مُستحسن للقنوات)
# أمثلة: "@your_channel", -1001234567890
TARGETS = []  # مثال: ["@my_channel", -100222333444]
# استبدل كل الأسطر المتكررة بهذا السطر فقط
TARGETS = [-1003067786221, -1002979008450, -1002986847855, -1003100385381]

# ===== قائمة الأذكار =====
AZKAR_LIST = [
"🌸 اللَّهُمَّ بِكَ أَصْبَحْنَا وَبِكَ أَمْسَيْنَا وَبِكَ نَحْيَا وَبِكَ نَمُوتُ وَإِلَيْكَ النُّشُورُ. (متفق عليه)",
"🍃 اللّهُمَّ أَنْتَ رَبِّي لَا إِلَهَ إِلَّا أَنْتَ خَلَقْتَنِي وَأَنَا عَبْدُكَ وَأَنَا عَلَى عَهْدِكَ وَوَعْدِكَ مَا اسْتَطَعْتُ أَعُوذُ بِكَ مِنْ شَرِّ مَا صَنَعْتُ أَبُوءُ لَكَ بِنِعْمَتِكَ عَلَيَّ وَأَبُوءُ بِذَنْبِي فَاغْفِرْ لِي فَإِنَّهُ لَا يَغْفِرُ الذُّنُوبَ إِلَّا أَنْتَ. (متفق عليه)",
"🌿 لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ وَهُوَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ. (متفق عليه)",
"📖 ﴿اللَّهُ لَا إِلَهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ ۚ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ ۚ لَهُ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ ۗ مَنْ ذَا الَّذِي يَشْفَعُ عِنْدَهُ إِلَّا بِإِذْنِهِ ۚ يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ ۖ وَلَا يُحِيطُونَ بِشَيْءٍ مِنْ عِلْمِهِ إِلَّا بِمَا شَاءَ ۚ وَسِعَ كُرْسِيُّهُ السَّمَاوَاتِ وَالْأَرْضَ ۖ وَلَا يَئُودُهُ حِفْظُهُمَا ۚ وَهُوَ الْعَلِيُّ الْعَظِيمُ﴾ (البقرة:255)",
"🌸 يَا حَيُّ يَا قَيُّومُ بِرَحْمَتِكَ أَسْتَغِيثُ أَصْلِحْ لِي شَأْنِي كُلَّهُ وَلَا تَكِلْنِي إِلَى نَفْسِي طَرْفَةَ عَيْنٍ. (متفق عليه)",
"🍃 بِسْمِ اللَّهِ الَّذِي لَا يَضُرُّ مَعَ اسْمِهِ شَيْءٌ فِي الْأَرْضِ وَلَا فِي السَّمَاءِ وَهُوَ السَّمِيعُ الْعَلِيمُ. (ثلاث مرات) (رواه مسلم)",
"🌿 اللّهُمَّ إِنِّي أَسْأَلُكَ مِنَ الْخَيْرِ كُلِّهِ عَاجِلِهِ وَآجِلِهِ مَا عَلِمْتُ مِنْهُ وَمَا لَمْ أَعْلَمْ وَأَعُوذُ بِكَ مِنَ الشَّرِّ كُلِّهِ عَاجِلِهِ وَآجِلِهِ مَا عَلِمْتُ مِنْهُ وَمَا لَمْ أَعْلَمْ. (رواه مسلم)",
"🌸 اللّهُمَّ أَصْلِحْ لِي دِينِي الَّذِي هُوَ عِصْمَةُ أَمْرِي وَأَصْلِحْ لِي دُنْيَايَ الَّتِي فِيهَا مَعَاشِي وَأَصْلِحْ لِي آخِرَتِي الَّتِي فِيهَا مَعَادِي. (متفق عليه)",
"🍃 اللّهُمَّ رَبَّنَا آتِنَا فِي الدُّنْيَا حَسَنَةً وَفِي الْآخِرَةِ حَسَنَةً وَقِنَا عَذَابَ النَّارِ. (متفق عليه)",
"🌿 يَا مُقَلِّبَ الْقُلُوبِ ثَبِّتْ قَلْبِي عَلَى دِينِكَ. (رواه مسلم)",
"🌸 رَبِّ اغْفِرْ لِي وَتُبْ عَلَيَّ إِنَّكَ أَنْتَ التَّوَّابُ الغَفُورُ. (متفق عليه)",
"🍃 اللّهُمَّ صَلِّ وَسَلِّمْ عَلَى نَبِيِّنَا مُحَمَّدٍ ﷺ وَعَلَى آلِهِ وَصَحْبِهِ أَجْمَعِينَ. (متفق عليه)",
]

# ===== حالة التشغيل =====
state = {"index": 0, "last_ids": {}, "targets": []}

def load_state():
    global state
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            s = json.load(f)
            # دمج الحالة القديمة مع القيم الافتراضية
            state.update({**{"index": 0, "last_ids": {}, "targets": []}, **s})
    except Exception:
        pass
    # أضف الأهداف الثابتة (إن وجدت) مرة واحدة
    for t in TARGETS:
        if t not in state["targets"]:
            state["targets"].append(t)

def save_state():
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, STATE_PATH)

def next_zekr():
    i = state["index"] % len(AZKAR_LIST)
    text = AZKAR_LIST[i]
    state["index"] = (i + 1) % len(AZKAR_LIST)
    return text

async def delete_last_if_any(client, chat_id):
    mid = state["last_ids"].get(str(chat_id))
    if not mid:
        return
    try:
        await client.delete_messages(chat_id, int(mid))
    except errors.rpcerrorlist.MessageDeleteForbiddenError:
        pass  # ما عنده صلاحية حذف هنا
    except Exception:
        pass
    finally:
        state["last_ids"][str(chat_id)] = None

async def purge_my_messages(client, chat_id, limit=1000):
    # تنظيف شامل لرسائل البوت القديمة
    ids = []
    async for m in client.iter_messages(chat_id, from_user="me", limit=limit):
        ids.append(m.id)
        if len(ids) >= 100:
            try:
                await client.delete_messages(chat_id, ids)
            except Exception:
                pass
            ids.clear()
    if ids:
        try:
            await client.delete_messages(chat_id, ids)
        except Exception:
            pass

async def send_zekr(client, chat_id):
    await delete_last_if_any(client, chat_id)
    text = next_zekr()
    try:
        msg = await client.send_message(chat_id, text, link_preview=False)
        state["last_ids"][str(chat_id)] = msg.id
        save_state()
    except Exception as e:
        print(f"[WARN] إرسال فشل chat={chat_id}: {e}")

async def post_cycle(client):
    if not state["targets"]:
        return
    for chat_id in list(state["targets"]):
        await send_zekr(client, chat_id)

async def setup_event_handlers(client):
    me = await client.get_me()
    my_id = me.id

    @client.on(events.ChatAction)
    async def _(event):
        # إذا أُضيف البوت إلى مجموعة/سوبرگروب
        try:
            if event.user_added and event.user_id == my_id:
                cid = event.chat_id
                if cid not in state["targets"]:
                    state["targets"].append(cid)
                    save_state()
                if PURGE_ON_START:
                    try:
                        await purge_my_messages(client, cid)
                    except Exception:
                        pass
                await send_zekr(client, cid)  # يرسل فوراً أول ذكر
        except Exception as e:
            print(f"[WARN] ChatAction handler: {e}")

    @client.on(events.NewMessage(pattern=r'^/(add|enable|start)$'))
    async def _(event):
        # أمر يدوي لإضافة الدردشة الحالية
        cid = event.chat_id
        if cid not in state["targets"]:
            state["targets"].append(cid)
            save_state()
        await event.reply("✅ تم التفعيل هنا، وسيُنشر الذكر دوريّاً.")
        await send_zekr(client, cid)

    @client.on(events.NewMessage(pattern=r'^/(stop|disable)$'))
    async def _(event):
        cid = event.chat_id
        if cid in state["targets"]:
            state["targets"].remove(cid)
            save_state()
        await event.reply("⏹️ تم الإيقاف هنا.")

async def run():
    load_state()
    client = TelegramClient("azkarbot", API_ID, API_HASH)
    await client.start(bot_token=BOT_TOKEN)

    stop_evt = asyncio.Event()

    # إشارات الإيقاف (قد لا تعمل على ويندوز، نتجاهل بأمان)
    def _stop(*_):
        stop_evt.set()
    for sig in (getattr(signal, "SIGINT", None), getattr(signal, "SIGTERM", None)):
        if sig:
            try:
                asyncio.get_running_loop().add_signal_handler(sig, _stop)
            except NotImplementedError:
                pass

    # فعّل الاستماعات
    await setup_event_handlers(client)

    # تنظيف أولي للأهداف المُعرّفة مسبقاً
    if PURGE_ON_START and state["targets"]:
        for cid in list(state["targets"]):
            try:
                await purge_my_messages(client, cid)
            except Exception:
                pass
        save_state()

    # أول إرسال فور التشغيل (للأهداف المُعرّفة فقط)
    await post_cycle(client)

    # حلقة عمل: ننتظر حتى الإيقاف
    await stop_evt.wait()
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(run())
