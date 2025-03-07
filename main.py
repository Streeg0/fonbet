import asyncio
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import telegram

# Настройка Telegram
bot_token = '8144105397:AAFr-2-evpF3dMj2w5D70mqJG8xUNAB0QUQ'
chat_id = '-1002444610604'
bot = telegram.Bot(token=bot_token)

# Настройка Selenium для облака
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-background-timer-throttling")
options.add_argument("--disable-backgrounding-occluded-windows")
options.add_argument("--disable-renderer-backgrounding")
options.add_argument("--user-data-dir=/tmp/chrome-data")  # Исправление ошибки

driver = webdriver.Chrome(options=options)

url = "https://fon.bet/sports/football/category/118/116441"
driver.get(url)
asyncio.run(asyncio.sleep(5))

last_score = None

async def send_message(message):
    try:
        await bot.send_message(chat_id=chat_id, text=message)
        print(f"Сообщение отправлено: {message}")
    except telegram.error.TelegramError as e:
        print(f"Ошибка отправки: {e}")

def find_element_safe(match, selector, by=By.CLASS_NAME, fallback_text="неизвестно"):
    try:
        return match.find_element(by, selector).text
    except:
        print(f"Элемент {selector} не найден, использую: {fallback_text}")
        return fallback_text

async def main():
    global last_score
    driver.execute_script("setInterval(() => { window.focus(); }, 10000);")
    while True:
        try:
            matches = driver.find_elements(By.CSS_SELECTOR, "[class*='sport-base-event-wrap']")
            if not matches:
                print("Матчи не найдены, жду...")
                last_score = None
                await asyncio.sleep(5)
                continue

            match = matches[0]
            try:
                teams = find_element_safe(match, "[data-testid='event']", By.CSS_SELECTOR, None)
                if teams == "неизвестно":
                    teams = find_element_safe(match, "table-component-text", By.CLASS_NAME, "Команды неизвестны")

                score = find_element_safe(match, "[class*='event-block-score__score']", By.CSS_SELECTOR, "0:0")
                game_time = find_element_safe(match, "[class*='event-block-current-time__time']", By.CSS_SELECTOR, "неизвестно")

                if score == "0:0" or game_time == "неизвестно":
                    print("Отладка: HTML первого матча:")
                    html = match.get_attribute("innerHTML")
                    print(html[:2000])

                if last_score is None:
                    print(f"Новый матч начался: {teams} - {score} (время: {game_time})")
                    last_score = score
                elif last_score != score and score != "0:0":
                    message = f"Гол! {teams} - {score} на {game_time}"
                    print(message)
                    await send_message(message)
                    last_score = score
                elif last_score != score and score == "0:0":
                    print(f"Новый матч начался: {teams} - {score} (время: {game_time})")
                    last_score = score

                print(f"Отслеживаю: {teams} - {score} (время: {game_time})")

            except Exception as e:
                print(f"Ошибка обработки первого матча: {e}")
                last_score = None

            await asyncio.sleep(5)

        except Exception as e:
            print(f"Ошибка в цикле: {e}")
            last_score = None
            await asyncio.sleep(5)

    driver.quit()

if __name__ == "__main__":
    asyncio.run(main())