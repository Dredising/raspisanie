import asyncio
import datetime
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# === 1. ДАННЫЕ РАСПИСАНИЯ ===
SCHEDULE = {
    "mon": {
        "upper": {
            1: "08:30–10:00 | Основы проектирования БД (л.р) | Подшивалова Е. А. | 2-211б",
            4: "14:00–15:30 | Основы проектирования БД (л.р) | Подшивалова Е. А. | 2-211б",
            5: "15:40–17:10 | Основы проектирования БД (л.р) | Подшивалова Е. А. | 2-211б",
        },
        "lower": {
            1: "08:30–10:00 | Основы проектирования БД (л.р) | Подшивалова Е. А. | 2-211б",
        },
    },
    "tue": {
        "both": {
            1: "08:30–10:00 | Дискретная математика (прак.) | Тунгускова А. М. | 2-211а",
            2: "10:10–11:40 | Администрирование сетевых ОС (л.р) | Жуйков В. Н. | 5-301/5-302",
            3: "12:20–13:50 | Администрирование сетевых ОС (л.р) | Жуйков В. Н. | 5-301/5-302",
            4: "14:00–15:30 | Администрирование сетевых ОС (лек) | Жуйков В. Н. | 5-304",
            5: "15:40–17:10 | Организация, принципы построения и функц. КС (лек.) | Степанова В. А. | 2-211а",
        }
    },
    "wed": {
        "both": {
            4: "14:00–15:30 | Дискретная математика (лек.) | Тунгускова А. М. | 7-316",
        }
    },
    "thu": {
        "upper": {
            2: "10:10–11:40 | Организация, принципы построения и функц. КС (л.р.) | Степанова В. А. | 2-211а",
            3: "12:20–13:50 | Организация, принципы построения и функц. КС (л.р.) | Степанова В. А. | 2-211а",
            4: "14:00–15:30 | Физкультура | Турлаков С. В. | Стадион Буревестник",
        },
        "lower": {
            2: "10:10–11:40 | Основы проектирования БД (л.р) | Подшивалова Е. А. | 2-211б",
            3: "12:20–13:50 | Основы проектирования БД (л.р) | Подшивалова Е. А. | 2-211б",
            4: "14:00–15:30 | Физкультура | Турлаков С. В. | Стадион Буревестник",
        },
    },
    "fri": {
        "upper": {
            3: "12:20–13:50 | Иностранный язык в проф. деятельности | Токарева Е. М. | 2-122",
            4: "14:00–15:30 | Иностранный язык в проф. деятельности | Токарева Е. М. | 2-122",
            5: "15:40–17:10 | Основы проектирования БД (лек) | Подшивалова Е. А. | 2-211а",
        },
        "lower": {
            5: "15:40–17:10 | Основы проектирования БД (лек) | Подшивалова Е. А. | 2-211а",
        },
    },
    "sat": {},
    "sun": {},
}

DAYS_RU = {
    "mon": "Понедельник",
    "tue": "Вторник",
    "wed": "Среда",
    "thu": "Четверг",
    "fri": "Пятница",
    "sat": "Суббота",
    "sun": "Воскресенье",
}

# === 2. НАСТРОЙКИ БОТА (Берутся из переменных окружения или значения по умолчанию) ===
BOT_TOKEN = os.getenv("BOT_TOKEN", "8999667322:AAEdJB4o3rvETcOz7qeKZsKVts5QlU6RM0s")
CHAT_ID = int(os.getenv("CHAT_ID", "1160070078"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

# === 3. ЛОГИКА ===
def is_upper_week(date_obj: datetime.date) -> bool:
    week_num = date_obj.isocalendar().week
    # Настроено под ваш вуз (четные недели = НАД ЧЕРТОЙ)
    return week_num % 2 == 0

def get_day_schedule(date_obj: datetime.date) -> str:
    day_code = date_obj.strftime("%a").lower()[:3]
    is_upper = is_upper_week(date_obj)
    week_type_str = "НАД ЧЕРТОЙ" if is_upper else "ПОД ЧЕРТОЙ"
    
    day_name = DAYS_RU.get(day_code, "")
    date_str = date_obj.strftime("%d.%m")

    day_data = SCHEDULE.get(day_code, {})
    lessons = {}

    if "both" in day_data:
        lessons.update(day_data["both"])

    week_key = "upper" if is_upper else "lower"
    if week_key in day_data:
        lessons.update(day_data[week_key])

    if not lessons:
        return f"📅 <b>{day_name} ({date_str})</b>\nНеделя: <i>{week_type_str}</i>\n\n🎉 Выходной! Пар нет."

    msg = f"📅 <b>{day_name} ({date_str})</b>\nНеделя: <i>{week_type_str}</i>\n\n"
    for num in sorted(lessons.keys()):
        msg += f"<b>{num}.</b> {lessons[num]}\n"

    return msg

async def send_daily():
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    text = get_day_schedule(tomorrow)
    await bot.send_message(CHAT_ID, text, parse_mode=ParseMode.HTML)

async def send_weekly():
    today = datetime.date.today()
    next_monday = today + datetime.timedelta(days=(0 - today.weekday() + 7))
    is_upper = is_upper_week(next_monday)
    week_type_str = "НАД ЧЕРТОЙ" if is_upper else "ПОД ЧЕРТОЙ"

    msg = f"🗓 <b>РАСПИСАНИЕ НА СЛЕДУЮЩУЮ НЕДЕЛЮ</b>\nНеделя: <u>{week_type_str}</u>\n\n"
    for i in range(6):
        day_date = next_monday + datetime.timedelta(days=i)
        msg += get_day_schedule(day_date) + "\n\n"

    await bot.send_message(CHAT_ID, msg, parse_mode=ParseMode.HTML)

# === 4. ТОЧКА ВХОДА И ЗАПУСК ===
async def main():
    # Еженедельная рассылка в воскресенье в 18:00
    scheduler.add_job(send_weekly, 'cron', day_of_week='sun', hour=18, minute=0)
    # Ежедневная рассылка с воскресенья по четверг в 20:00
    scheduler.add_job(send_daily, 'cron', day_of_week='sun,mon,tue,wed,thu', hour=20, minute=0)
    scheduler.start()

    print("Бот успешно запущен на сервере!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())