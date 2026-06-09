import re
import json
from datetime import datetime, timedelta

import vk_api

from core import config

def load_json_file(filepath, default=None):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default if default is not None else {}

def save_json_file(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_published():
    return load_json_file(config.PUBLISHED_FILE, {"published": []})

def save_published(data):
    save_json_file(config.PUBLISHED_FILE, data)

def load_bans():
    return load_json_file(config.BAN_FILE, {})

def save_bans(bans):
    save_json_file(config.BAN_FILE, bans)

def is_user_banned(user_id):
    bans = load_bans()
    if str(user_id) not in bans:
        return False
    ban_info = bans[str(user_id)]
    ban_until = datetime.fromisoformat(ban_info["until"])
    if datetime.now() > ban_until:
        del bans[str(user_id)]
        save_bans(bans)
        return False
    return True

def ban_user(user_id, reason):
    bans = load_bans()
    ban_until = datetime.now() + timedelta(hours=config.BAN_HOURS)
    bans[str(user_id)] = {
        "until": ban_until.isoformat(),
        "reason": reason,
        "banned_at": datetime.now().isoformat()
    }
    save_bans(bans)
    print(f"⚠️ Пользователь {user_id} забанен на {config.BAN_HOURS}ч. Причина: {reason}")

def contains_anonymous_keyword(text):
    for keyword in config.ANONYMOUS_KEYWORDS:
        if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
            return True
    return False

def remove_keywords(text):
    cleaned = text
    for keyword in config.ANONYMOUS_KEYWORDS:
        cleaned = re.sub(r'\b' + re.escape(keyword) + r'\b', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
    return cleaned

def is_spam(text):
    if not text:
        return False, None
    text_lower = text.lower()
    for word in config.FORBIDDEN_WORDS:
        if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
            return True, "запрещенные слова"
    for link in config.FORBIDDEN_LINKS:
        if link in text_lower:
            return True, "ссылки на сторонние ресурсы"
    return False, None

def build_attachments(post):
    attachments = []
    for a in post.get("attachments", []):
        t = a["type"]
        obj = a[t]
        owner_id = obj.get("owner_id")
        item_id = obj.get("id")
        access_key = obj.get("access_key", "")
        if owner_id and item_id:
            attachment = f"{t}{owner_id}_{item_id}"
            if access_key:
                attachment += f"_{access_key}"
            attachments.append(attachment)
    return ",".join(attachments) if attachments else None

def get_user_full_name(vk, user_id):
    try:
        user = vk.users.get(user_ids=user_id, fields="first_name,last_name")
        if user and len(user) > 0:
            return user[0].get('first_name', ''), user[0].get('last_name', '')
    except:
        pass
    return "", ""

def make_profile_link(user_id, first_name, last_name):
    return f"[id{user_id}|{first_name} {last_name}]"

def delete_suggestion(vk, suggestion_id):
    try:
        vk.wall.delete(owner_id=-config.GROUP_ID, post_id=suggestion_id)
        return True
    except:
        return False
