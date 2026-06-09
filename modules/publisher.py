import time
import vk_api

from core import config, utils, database

def publish_post(vk, post):
    post_id = post["id"]
    from_id = post.get("from_id")
    original_text = post.get("text", "")
    
    # Проверки
    if utils.is_user_banned(from_id):
        utils.delete_suggestion(vk, post_id)
        return None
    
    is_spam_post, spam_reason = utils.is_spam(original_text)
    if is_spam_post:
        utils.delete_suggestion(vk, post_id)
        utils.ban_user(from_id, spam_reason)
        return None
    
    # Формируем пост
    is_anonymous = utils.contains_anonymous_keyword(original_text)
    cleaned_text = utils.remove_keywords(original_text)
    
    if is_anonymous:
        final_text = f"{cleaned_text}\n\n— Анонимно"
    else:
        first_name, last_name = utils.get_user_full_name(vk, from_id)
        if first_name and last_name:
            profile_link = utils.make_profile_link(from_id, first_name, last_name)
            final_text = f"{cleaned_text}\n\n© {profile_link}"
        else:
            final_text = f"{cleaned_text}\n\n— Анонимно"
    
    # Публикуем
    attachments = utils.build_attachments(post)
    result = vk.wall.post(
        owner_id=-config.GROUP_ID,
        message=final_text,
        attachments=attachments,
        from_group=1
    )
    
    # Сохраняем
    utils.delete_suggestion(vk, post_id)
    database.add_post(from_id, result['post_id'], cleaned_text)
    
    return result['post_id']

def run_publisher():
    vk_session = vk_api.VkApi(token=config.USER_TOKEN)
    vk = vk_session.get_api()
    published = utils.load_published()
    last_publish_time = None
    
    print("=" * 50)
    print("🚀 ПУБЛИКАТОР ЗАПУЩЕН")
    print(f"📌 Группа: -{config.GROUP_ID}")
    print(f"⏱ Интервал: {config.PUBLISH_INTERVAL // 60} мин.")
    print("=" * 50)
    
    while True:
        try:
            response = vk.wall.get(owner_id=-config.GROUP_ID, filter="suggests", count=100)
            items = response.get("items", [])
            
            pending = [p for p in items if p["id"] not in published["published"]]
            
            if pending and (last_publish_time is None or 
                           (time.time() - last_publish_time) >= config.PUBLISH_INTERVAL):
                
                post = pending[0]
                post_id = publish_post(vk, post)
                
                if post_id:
                    print(f"✅ Пост #{post_id} опубликован")
                    last_publish_time = time.time()
                    published["published"].append(post["id"])
                    utils.save_published(published)
            
            time.sleep(config.CHECK_INTERVAL)
            
        except Exception as e:
            print(f"❌ Ошибка публикатора: {e}")
            time.sleep(60)

def main():
    database.init_db()
    run_publisher()

if __name__ == "__main__":
    main()
