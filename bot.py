import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

from db import init_db, add_listing, get_recent_listings
from profit import estimate_profit
from sources import scan_olx

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN", "").strip()
router = Router()

@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🛵 OLX Scooter Hunter запущен!\n\n"
        "Настройки: Львовская область · прибыль от 1500 грн.\n\n"
        "Команды:\n"
        "/add URL | цена | ремонт | доставка — добавить объявление вручную\n"
        "/profit цена_покупки цена_продажи ремонт доставка — расчёт прибыли\n"
        "/latest — последние сохранённые объявления\n"
        "/scan — проверить подключённый источник (пока демонстрационный режим)\n\n"
        "Важно: автоматический сбор OLX подключается отдельным адаптером "
        "после проверки доступного разрешённого источника."
    )

@router.message(Command("help"))
async def help_cmd(message: Message):
    await start(message)

@router.message(Command("profit"))
async def profit_cmd(message: Message):
    parts = (message.text or "").split()
    if len(parts) != 5:
        await message.answer(
            "Формат: /profit цена_покупки цена_продажи ремонт доставка\n"
            "Пример: /profit 5000 8000 1000 300"
        )
        return
    try:
        buy, sell, repair, delivery = map(float, parts[1:])
        result = estimate_profit(buy, sell, repair, delivery)
    except ValueError:
        await message.answer("Укажи четыре числа. Например: /profit 5000 8000 1000 300")
        return
    status = "✅ Проходит твой фильтр" if result["net"] >= 1500 else "⚠️ Ниже минимальной прибыли 1500 грн"
    await message.answer(
        f"📊 Расчёт\nПокупка: {buy:.0f} грн\n"
        f"Перепродажа: {sell:.0f} грн\nРемонт: {repair:.0f} грн\n"
        f"Доставка: {delivery:.0f} грн\n\n"
        f"Ориентировочная прибыль: {result['net']:.0f} грн\n{status}\n\n"
        "Не забудь заложить резерв на скрытые дефекты и торг."
    )

@router.message(Command("add"))
async def add_cmd(message: Message):
    raw = (message.text or "").partition(" ")[2].strip()
    parts = [p.strip() for p in raw.split("|")]
    if len(parts) != 4:
        await message.answer(
            "Формат:\n/add URL | цена | ремонт | доставка\n"
            "Пример:\n/add https://www.olx.ua/ | 5000 | 1000 | 300"
        )
        return
    url, buy_s, repair_s, delivery_s = parts
    try:
        buy, repair, delivery = map(float, (buy_s, repair_s, delivery_s))
    except ValueError:
        await message.answer("Цена, ремонт и доставка должны быть числами.")
        return
    if not url.startswith(("https://", "http://")):
        await message.answer("Ссылка должна начинаться с https:// или http://")
        return
    await add_listing(url=url, buy_price=buy, repair_cost=repair, delivery_cost=delivery)
    await message.answer(
        f"Сохранил объявление.\nПокупка: {buy:.0f} грн\n"
        f"Ремонт: {repair:.0f} грн\nДоставка: {delivery:.0f} грн\n"
        "Чтобы оценить прибыль, сначала укажи реалистичную цену перепродажи командой /profit."
    )

@router.message(Command("latest"))
async def latest_cmd(message: Message):
    rows = await get_recent_listings(10)
    if not rows:
        await message.answer("Пока нет сохранённых объявлений. Добавь первое через /add.")
        return
    lines = ["🗂 Последние объявления:"]
    for row in rows:
        lines.append(f"• {row['buy_price']:.0f} грн — {row['url']}")
    await message.answer("\n".join(lines), disable_web_page_preview=True)

@router.message(Command("scan"))
async def scan_cmd(message: Message):
    await message.answer(
        "🔎 Источник объявлений ещё не подключён.\n"
        "Сейчас бот готов принимать ссылки и считать прибыль. "
        "Для полноценного мониторинга нужно подключить источник данных OLX, "
        "доступный и разрешённый для автоматизированного использования."
    )
    results = await scan_olx()
    if results:
        await message.answer(f"Источник вернул {len(results)} объявлений.")

async def main():
    if not TOKEN:
        raise RuntimeError("Не задан BOT_TOKEN. Скопируй .env.example в .env и добавь токен BotFather.")
    logging.basicConfig(level=logging.INFO)
    await init_db()
    bot = Bot(TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
