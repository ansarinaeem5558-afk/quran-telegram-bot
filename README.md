# quran-telegram-bot
Telegram Qur'an Bot
import requests
import time
import difflib

# ================= CONFIG =================
TOKEN = "8263091770:AAHG7eWTTxAnvaVedKvhpxOLVceWHAWpbgQ"
BASE = f"https://api.telegram.org/bot{TOKEN}"

SURAH_LIST_API = "https://api.alquran.cloud/v1/surah"
SURAH_API = "https://api.alquran.cloud/v1/surah/{}"

BISMILLAH = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"

offset = None
SURAH_NAME_MAP = {}
SURAH_CACHE = {}

# ================= BASIC =================
def send_message(chat_id, text):
    requests.post(BASE + "/sendMessage", data={
        "chat_id": chat_id,
        "text": text
    })

def typing(chat_id):
    requests.post(BASE + "/sendChatAction", data={
        "chat_id": chat_id,
        "action": "typing"
    })

# ================= NORMALIZE =================
def normalize(text):
    return (
        text.lower()
        .replace("al-", "")
        .replace("-", "")
        .replace(" ", "")
    )

# ================= CLEAR OLD UPDATES =================
def clear_old_updates():
    global offset
    r = requests.get(BASE + "/getUpdates").json()
    res = r.get("result", [])
    if res:
        offset = res[-1]["update_id"] + 1

# ================= LOAD SURAH NAMES =================
def load_surah_names():
    r = requests.get(SURAH_LIST_API).json()
    for s in r["data"]:
        key = normalize(s["englishName"])
        SURAH_NAME_MAP[key] = s["number"]

# ================= FUZZY MATCH =================
def find_closest_surah(query):
    query = normalize(query)
    names = list(SURAH_NAME_MAP.keys())
    match = difflib.get_close_matches(query, names, n=1, cutoff=0.6)
    if match:
        return SURAH_NAME_MAP[match[0]]
    return None

# ================= GET SURAH =================
def get_surah(num):
    if num in SURAH_CACHE:
        return SURAH_CACHE[num]

    r = requests.get(SURAH_API.format(num)).json()
    if r.get("status") != "OK":
        return None

    SURAH_CACHE[num] = r["data"]
    return r["data"]

# ================= START =================
print("🤖 Qur'an Bot Started...")
clear_old_updates()
load_surah_names()

# ================= MAIN LOOP =================
while True:
    r = requests.get(BASE + "/getUpdates", params={
        "offset": offset,
        "timeout": 5
    }).json()

    for update in r.get("result", []):
        offset = update["update_id"] + 1

        if "message" not in update:
            continue

        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "").strip()

        # Only /surah command allowed
        if not text.lower().startswith("/surah"):
            continue

        typing(chat_id)

        parts = text.split(maxsplit=1)
        if len(parts) != 2:
            send_message(chat_id, "❌ Use like:\n/surah mulk\n/surah 1")
            continue

        query = parts[1]

        # number or fuzzy name
        if query.isdigit():
            surah_no = int(query)
        else:
            surah_no = find_closest_surah(query)

        if not surah_no or surah_no < 1 or surah_no > 114:
            send_message(chat_id, "❌ Surah samajh nahi aayi")
            continue

        data = get_surah(surah_no)
        if not data:
            send_message(chat_id, "❌ Error loading surah")
            continue

        ayahs = data["ayahs"]
        header = f"📖 {data['name']} ({data['englishName']})\n\n"

        msg = header
        num = 1

        # ❗ Surah 9 (At-Tawbah) me Bismillah nahi
        if data["number"] != 9:
            msg += f"{num}. {BISMILLAH}\n"
            num += 1

        for ayah in ayahs:
            msg += f"{num}. {ayah['text']}\n"
            num += 1

        send_message(chat_id, msg)

    time.sleep(0.5)
