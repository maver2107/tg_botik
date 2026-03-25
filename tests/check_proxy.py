# simple_proxy_test.py
import requests

proxy = {"http": "http://mdWZTj:jFdzWz@152.232.72.104:9263", "https": "http://mdWZTj:jFdzWz@152.232.72.104:9263"}

try:
    # Простой запрос, не Телеграм
    r = requests.get("https://ifconfig.co/ip", proxies=proxy, timeout=10)
    print("✅ Прокси работает!")
    print("Твой IP через прокси:", r.text.strip())
except requests.exceptions.ProxyError as e:
    print(f"❌ ProxyError: {e}")
except requests.exceptions.ConnectTimeout:
    print("❌ Таймаут подключения к прокси")
except Exception as e:
    print(f"❌ Другая ошибка: {type(e).__name__}: {e}")
