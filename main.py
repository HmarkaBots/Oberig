from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
import asyncio
from dotenv import load_dotenv
import os
from markup import set_commands
from personal_actions import RegisterState, get_start, start_register, name_register, register_phone, AngelState, GuardianState
from aiogram.filters import Command
from personal_actions import (
    register_phone, choose_role, angel_selected, guardian_selected, send_payment_details, about_collection, about_partners, choose_region,
    input_amount, input_wish, upload_photo, confirm_and_save, choose_angel, input_guardian_amount, input_guardian_instagram,
    input_guardian_wish, upload_guardian_photo, input_jar_link
)

# Load .env file
load_dotenv("dev.env")
# Retrieve config variables
try:
    TOKEN = os.getenv('TOKEN')
    BOT_OWNERS = [int(x.strip()) for x in os.getenv('BOT_OWNERS', "").split(",") if x.strip().isdigit()]
except (TypeError, ValueError) as ex:
    print("Error while reading config:", ex)

# Initialize bot and dispatcher
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# Start bot notification
async def start_bot(bot: Bot):
    await bot.send_message(BOT_OWNERS[0], text='Вітаємо в Боті "Оберіг на Новий Рік🎄"!')

dp.startup.register(start_bot)
dp.message.register(get_start, Command(commands="start"))

dp.message.register(start_register, F.text=='🟢СТАРТ БОТУ🟢')
dp.message.register(name_register, RegisterState.regName)
dp.message.register(register_phone, RegisterState.regPhone)
dp.message.register(about_collection, F.text == "📢Про збір")
dp.message.register(about_partners, F.text == "🤝Партнери")
dp.message.register(choose_role, F.text == "✨ Ставай частиною дива! ✨")

dp.message.register(angel_selected, F.text == "Янгол")
dp.message.register(choose_region, AngelState.select_region)
dp.message.register(input_amount, AngelState.input_amount)
dp.message.register(input_jar_link, AngelState.input_jar_link)
dp.message.register(input_wish, AngelState.input_instagram)
dp.message.register(upload_photo, AngelState.input_wish)
dp.message.register(confirm_and_save, AngelState.upload_photo)

dp.message.register(guardian_selected, F.text == "Оберіг")
dp.message.register(choose_angel, GuardianState.choose_angel)
dp.message.register(input_guardian_amount, GuardianState.input_amount)
dp.message.register(input_guardian_instagram, GuardianState.input_instagram)
dp.message.register(input_guardian_wish, GuardianState.input_wish)
dp.message.register(upload_guardian_photo, GuardianState.upload_photo)
dp.message.register(send_payment_details, F.text == "💙ПІДТРИМАТИ ЗБІР💛")

async def start():
    await set_commands(bot)
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(start())