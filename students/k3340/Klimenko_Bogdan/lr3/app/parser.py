import aiohttp
from bs4 import BeautifulSoup

async def parse_url_async(url: str) -> dict:
    """
    Асинхронно загружает страницу, извлекает заголовок и первые 500 символов текста.
    Возвращает словарь с результатом.
    """
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                title = soup.title.string.strip() if soup.title and soup.title.string else "No title"
                text = soup.get_text(separator=' ', strip=True)
                content = text[:500] if text else ""
                return {
                    "url": url,
                    "title": title,
                    "content": content,
                    "status": "success"
                }
    except Exception as e:
        return {
            "url": url,
            "title": None,
            "content": None,
            "status": "error",
            "error": str(e)
        }