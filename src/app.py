import asyncio
import logging
from dotenv import load_dotenv

from pydantic_settings import BaseSettings

from urllib.parse import quote
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from bs4 import BeautifulSoup


class BotConfig(BaseSettings):
    token: str

    class Config:
        env_file = ".env"
        env_prefix = "BOT_"


dp = Dispatcher()


async def get_weather(city) -> str:
    result = ""
    url = "https://www.google.com/search?q=" + quote("погода в " + city)
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}, ssl=False) as response:
            soup = await response.text()
            bs = BeautifulSoup(soup, "html.parser")
            taw = bs.find("div", {"id": "taw"})
            if taw:
                start_index = taw.text.find("Результаты: ") + len("Результаты: ")
                end_index = taw.text.find("∙ ")
                target = taw.text[start_index:end_index].strip()
                result = f"{hbold(target)}, температура: "
            temperature = bs.find("span", {"id": "wob_tm"})
            if temperature:
                if temperature.text.startswith("-"):
                    result += hbold(temperature.text + "°C")
                else:
                    result += hbold("+" + temperature.text + "°C")
            else:
                return "No temperature"
            return result


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")


@dp.message()
async def message_handler(message: types.Message) -> None:
    try:
        weather = await get_weather(message.text)
        await message.answer(weather)
    except Exception:
        await message.answer("Error getting weather")


async def main() -> None:
    load_dotenv()
    config = BotConfig()
    bot = Bot(config.token, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
