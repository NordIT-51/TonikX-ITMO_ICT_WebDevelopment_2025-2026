import multiprocessing
import requests
from bs4 import BeautifulSoup
import time
from database import init_db, clear_pages, save_page

URLS = [
    "https://www.google.com",
    "https://www.youtube.com",
    "https://www.facebook.com",
    "https://www.instagram.com",
    "https://www.chatgpt.com",
    "https://www.wikipedia.org",
    "https://www.reddit.com",
    "https://www.x.com",
    "https://www.whatsapp.com",
    "https://www.bing.com",
    "https://www.amazon.com",
    "https://www.yahoo.com",
    "https://www.temu.com",
    "https://www.duckduckgo.com",
    "https://www.yahoo.co.jp",
    "https://www.tiktok.com",
    "https://www.yandex.ru",
    "https://www.weather.com",
    "https://www.microsoftonline.com",
    "https://www.msn.com",
    "https://www.microsoft.com",
    "https://www.live.com",
    "https://www.fandom.com",
    "https://www.linkedin.com",
    "https://www.twitter.com",
    "https://www.netflix.com",
    "https://www.pinterest.com",
    "https://www.twitch.tv",
    "https://www.openai.com",
    "https://www.naver.com",
    "https://www.office.com",
    "https://www.canva.com",
    "https://www.vk.com",
    "https://www.paypal.com",
    "https://www.aliexpress.com"
]

def parse_and_save(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string.strip() if soup.title else "No title"
        save_page(url, title)
        return url, title
    except Exception:
        return url, None

def run():
    init_db()
    clear_pages()
    with multiprocessing.Pool(processes=min(4, len(URLS))) as pool:
        results = pool.map(parse_and_save, URLS)
    return len(results)

def main():
    start_time = time.time()
    count = run()
    elapsed = time.time() - start_time
    print(f"Обработано {count} URL-адресов")
    print(f"Время выполнения (multiprocessing): {elapsed:.4f} секунд")

if __name__ == "__main__":
    main()