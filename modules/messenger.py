import os
import json
import vk_api
from flask import Flask, request, Response

from core import config, utils, database, keyboards

app = Flask(__name__)

# Множество для отслеживания ожидания поддержки
waiting_for_support = set()

def send_message(vk, user_id, message, keyboard=None):
    try:
        vk.messages.send(
            user_id=user_id,
            message=message,
            random_id=0,
            keyboard=keyboard.get_keyboard() if keyboard else None
        )
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")

def check_subscription(vk, user_id):
    try:
        return vk.groups.isMember(group_id=config.GROUP_ID, user_id=user_id)
    except:
        return False

def process_message(vk, user_id, text, payload):
    global waiting_for_support
    
    # Проверка подписки
    if not check_subscription(vk, user_id):
        send_message(vk, user_id, 
            f"❌ Вы не подписаны на сообщество!\nhttps://vk.com/club{config.GROUP_ID}",
            keyboards.get_back_keyboard())
        return
    
    # Проверка бана
    if utils.is_user_banned(user_id):
        send_message(vk, user_id, "🚫 Вы забанены за нарушение правил.", keyboards.get_back_keyboard())
        return
    
    # Режим поддержки
    if user_id in waiting_for_support:
        if text == "/cancel":
            waiting_for_support.discard(user_id)
            send_message(vk, user_id, "❌ Отменено.", keyboards.get_main_keyboard())
        else:
            waiting_for_support.discard(user_id)
            try:
                user_info = vk.users.get(user_ids=user_id)[0]
                admin_msg = f"📨 Поддержка\nОт: {user_info['first_name']} (id{user_id})\nТекст: {text}"
                send_message(vk, config.ADMIN_ID, admin_msg)
                send_message(vk, user_id, "✅ Сообщение отправлено администратору!", keyboards.get_main_keyboard())
            except Exception as e:
                send_message(vk, user_id, "❌ Ошибка отправки.", keyboards.get_main_keyboard())
        return
    
    # Обработка команд
    if text in ["начать", "меню", "start"]:
        stats = database.get_user_stats(user_id)
        send_message(vk, user_id,
            f"👋 Добро пожаловать!\n\n📊 Постов: {stats['posts_count']}\n📝 Символов: {stats['total_chars']}",
            keyboards.get_main_keyboard())
    
    elif text == "📊 моя статистика":
        stats = database.get_user_stats(user_id)
        send_message(vk, user_id,
            f"📊 Ваша статистика\n\nПостов: {stats['posts_count']}\nСимволов: {stats['total_chars']}",
            keyboards.get_main_keyboard())
    
    elif text == "🗑 удалить мой пост":
        posts = database.get_user_posts(user_id)
        if not posts:
            send_message(vk, user_id, "📭 Нет постов для удаления", keyboards.get_main_keyboard())
        else:
            send_message(vk, user_id, "🗑 Выберите пост:", keyboards.get_posts_keyboard(posts))
    
    elif text == "🆘 написать в поддержку":
        waiting_for_support.add(user_id)
        send_message(vk, user_id, "📝 Напишите сообщение администратору. /cancel для отмены", keyboards.get_back_keyboard())
    
    elif text == "🔙 назад в меню":
        send_message(vk, user_id, "Главное меню:", keyboards.get_main_keyboard())
    
    elif payload:
        if payload.get("action") == "back":
            send_message(vk, user_id, "Главное меню:", keyboards.get_main_keyboard())
        elif payload.get("action") == "confirm_delete":
            post_id = payload.get("post_id")
            if database.get_post_author(post_id) == user_id:
                try:
                    vk.wall.delete(owner_id=-config.GROUP_ID, post_id=post_id)
                    database.delete_user_post(user_id, post_id)
                    send_message(vk, user_id, f"✅ Пост #{post_id} удален!", keyboards.get_main_keyboard())
                except Exception as e:
                    send_message(vk, user_id, f"❌ Ошибка удаления: {e}", keyboards.get_main_keyboard())
            else:
                send_message(vk, user_id, "❌ Это не ваш пост!", keyboards.get_main_keyboard())
        elif payload.get("post_id"):
            send_message(vk, user_id, 
                f"⚠️ Удалить пост #{payload['post_id']}?", 
                keyboards.get_confirm_keyboard(payload['post_id']))
    else:
        send_message(vk, user_id, "❌ Неизвестная команда. Нажмите на кнопки.", keyboards.get_main_keyboard())

@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return 'OK', 200
    
    data = request.json
    print(f"📨 Получен тип: {data.get('type') if data else 'None'}")
    
    if data and data.get('type') == 'confirmation':
        print("🔑 Отправляем код подтверждения")
        return Response(config.CONFIRMATION_CODE, content_type='text/plain; charset=utf-8')
    
    if data and data.get('type') == 'message_new':
        message = data['object']['message']
        user_id = message['from_id']
        text = message.get('text', '').lower().strip()
        payload = message.get('payload')
        
        payload_data = None
        if payload:
            try:
                payload_data = json.loads(payload) if isinstance(payload, str) else payload
            except:
                pass
        
        # Создаем сессию для ответа
        vk_session = vk_api.VkApi(token=config.GROUP_TOKEN, api_version='5.131')
        vk = vk_session.get_api()
        
        process_message(vk, user_id, text, payload_data)
    
    return 'ok'

def start_webhook():
    """Запуск Flask для Callback API"""
    port = int(os.environ.get("PORT", 3000))
    print(f"🌐 Запуск веб-сервера на порту {port}")
    app.run(host='0.0.0.0', port=port)

def main():
    database.init_db()
    print("=" * 50)
    print("🤖 ЛС БОТ ЗАПУЩЕН")
    print("=" * 50)
    start_webhook()

if __name__ == "__main__":
    main()
