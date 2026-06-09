#!/usr/bin/env python3
"""
Бот для Подслушано
Поддерживает: публикацию постов + ответы в ЛС (Callback API)
"""

import os
import sys
import threading
from dotenv import load_dotenv

load_dotenv()

def main():
    # Определяем режим по переменным окружения
    use_webhook = bool(os.getenv("CONFIRMATION_CODE") and os.getenv("PORT"))
    
    if use_webhook:
        print("🚀 Запуск: ПУБЛИКАТОР + ЛС БОТ (Callback API)")
        print("=" * 50)
        
        from modules.publisher import run_publisher
        from modules.messenger import start_webhook
        
        # Публикатор в фоновом потоке
        publisher_thread = threading.Thread(target=run_publisher, daemon=True)
        publisher_thread.start()
        print("✅ Публикатор запущен в фоне")
        
        # Вебхук в главном потоке
        start_webhook()
    else:
        print("🚀 Запуск: ТОЛЬКО ПУБЛИКАТОР (без ЛС)")
        print("=" * 50)
        print("💡 Для включения ЛС бота добавьте CONFIRMATION_CODE и включите домен")
        print("=" * 50)
        
        from modules.publisher import run_publisher
        run_publisher()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
