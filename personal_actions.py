from aiogram import Bot
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import re
from dotenv import load_dotenv
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import os
from db import BotDB
from aiogram.fsm.state import State, StatesGroup


load_dotenv("dev.env")
db = BotDB(os.getenv("DB_NAME"))


class RegisterState(StatesGroup):
    regName = State()
    regPhone = State()


register_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text='🟢СТАРТ БОТУ🟢'
            )
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Для продовження натисни кнопку нижче 👇"
)

async def get_start(message: Message, bot: Bot):
    await bot.send_message(
        message.from_user.id,
        text=(
            f"Вітаємо в Боті! Дякуємо за бажання підтримати нас❤️!\n"
            f"Бот допоможе тобі приєднатися до збору \n\n\n"
        ), reply_markup=register_keyboard
    )

async def start_register(message: Message, state: FSMContext):
    await message.answer(
        f"⭐ Почнемо реєстрацію! ⭐\n"
        f"Спершу напиши як до тебе можна звертатися?",
        reply_markup=ReplyKeyboardRemove()  # Видаляємо клавіатуру
    )
    await state.set_state(RegisterState.regName)

async def name_register(message: Message, state: FSMContext):
    await message.answer(
        f"😊 Приємно познайомитися, {message.text}\n"
        f"📱 Тепер вкажи свій номер телефону, або поділися своїм контактом, щоб завершити реєстрацію \n"
        f"✅ Це допоможе підтвердити, що ти не бот, а справжній Янгол, готовий творити дива \n\n"
        f"⚠️ Увага! Формат телефону виглядає так: +380********* \n\n",
        reply_markup=share_phone_keyboard  # Додаємо клавіатуру з кнопкою "Поділитися номером"
    )
    await state.update_data(regname=message.text)
    await state.set_state(RegisterState.regPhone)

# Клавіатура для кнопки "Поділитися номером"
share_phone_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="📱 Поділитися номером",
                request_contact=True
            )
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Введи номер або поділися контактом"
)

# Функція для введення або надсилання контакту
async def ask_for_phone(message: Message, state: FSMContext):
    await message.answer(
        text="Будь ласка, поділися своїм номером телефону або введи його у форматі +380XXXXXXXXX:",
        reply_markup=share_phone_keyboard  # Додаємо клавіатуру
    )
    await state.set_state(RegisterState.regPhone)


# Обробник для текстового номера або контакту
async def register_phone(message: Message, state: FSMContext):
    db = BotDB(os.getenv("DB_NAME"))  # Ініціалізуємо підключення до БД
    try:
        # Якщо користувач поділився контактом
        if message.contact:
            phone_number = message.contact.phone_number
            await state.update_data(regphone=phone_number)
        # Якщо користувач ввів номер вручну
        elif re.match(r"^\+380\d{9}$", message.text):
            await state.update_data(regphone=message.text)
        else:
            await message.answer("❌ Неправильний формат номера. Спробуйте ще раз або скористайтесь кнопкою.")
            return  # Повертаємося без завершення реєстрації

        # Отримання збережених даних
        reg_data = await state.get_data()
        reg_name = reg_data.get('regname')
        reg_phone = reg_data.get('regphone')

        # Додаємо користувача у базу даних
        db.add_user(message.from_user.id, reg_name, reg_phone)

        # Повідомлення про успішну реєстрацію
        msg = f"✅ Реєстрація завершена успішно! Ти вже частина нашої різдвяної історії!\n🌟 Твоя участь змінює світ\nІм'я: {reg_name}, Телефон: {reg_phone}"
        await message.answer(msg)

        # Очищення стану
        await state.clear()

        # DEBUG: Діагностика для перевірки виклику
        print("DEBUG: Викликається функція about_collection")

        # Відправляємо нову клавіатуру з трьома кнопками
        await message.answer(
            "Обери один із варіантів нижче для подальшої інформації 👇",
            reply_markup=collection_keyboard
        )

    except ValueError:
        await message.answer("❗Ти вже зареєстрований.")
    except Exception as e:
        await message.answer(f"❌ Сталася помилка: {e}")
    finally:
        db.close()
        

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Клавіатура з кнопками "Про збір", "Партнери" та "Долучитись до підсилення збору"
collection_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📢Про збір")],
        [KeyboardButton(text="🤝Партнери")],
        [KeyboardButton(text="✨ Ставай частиною дива! ✨")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

# Обробник для кнопки "Про збір"
async def about_collection(message: Message):
    await message.answer(
        text=(
            "📢 *Про збір*\n\n"
            '''*Оберіг на Новий рік 🎁* – це масштабна благодійна ініціатива, організована студентами Києва. До команди ініціативи входять представники:

    📌Ради студентів ННІМВ
    📌Студентського парламенту ФІТ
    📌Студентського парламенту ННІЖ
    📌Студентського парламенту ННІПУДС
    📌Студентського парламенту ЕФ
    📌Студентського парламенту ННІП
    📌Студентського парламенту ННЦ «ІБМ»
    📌ГО “Студентське Братство Києва”

💙💛 *Ціль збору: 1 000 000 гривень*

    ✨ Кошти будуть спрямовані на підтримку наступних підрозділів:

    📌101-ша окрема бригада охорони ГШ (2 батальйон)
    📌1-ша бригада оперативного призначення НГУ “Буревій”
    📌4-та бригада оперативного призначення НГУ “Рубіж”
    📌Третя окрема штурмова бригада
    📌Головне управління розвідки

✨ *Потреби, на які збираються кошти:*

    📌Ретранслятор ELRS/Crossfire з кріпленням на Mavic – 2 одиниці
    📌Щогла – 2 одиниці
    📌Наземна станція “T-Bone V4”
    📌Ремонт автівки VW T5
    📌Балістичний шолом Sestan-Busch Helmet BK-ACH-HC 
    📌Активні навушники Sordin Supreme Pro-X Neckband
    📌Полегшений бронежилет "Сармат" із балістичним протиуламковим пакетом (1 класу захисту, ММ-14)
    📌Mavic 3T
    📌Volkswagen Touareg 1 - 2 одиниці
    📌Зарядна станція EcoFlow DELTA 2 Max (EFDELTA2Max-AU) AU
    📌Портативна зарядна станція OUKITEL P2001E PLUS (2400W 2048Wh)\n\n'''
        ),
        parse_mode="Markdown"
    )

# Обробник для кнопки "Партнери"
async def about_partners(message: Message):
    await message.answer(
        text=(
            "🤝 *Партнери:*\n\n"
            '''🔹*Різдвяні історії*: Ялинкові прикраси від бренду Різдвяні історії це щось, що наповнює серце теплом та приємними спогадами. Щось, чим захочеться ділитися з рідними. Про що, захочеться розповідати Щось, що захочеться берегти довгі роки.\n\n'''
            '''🔹*FIRERABBIT*: Ідея бренду FIRERABBIT зародилася восени 2022 року, у період надзвичайних викликів для України. Засновниця, Віта, приймала та допомагала переселенцям із тимчасово окупованих територій, розміщуючи їх у Києві та Славутичі. Перші блекаути підштовхнули до створення яскравих, кольорових свічок, що не тільки дарують світло, але й теплоту та надію в темні часи. Цей бренд символізує адаптацію та творчість навіть у найскладніших умовах.\n\n'''
            '''🔹*GST candles*: Бренд GST candles створений Тетяною та Софією Хлевич у 2022 році. Він вирізняється ексклюзивним дизайном і використовує екологічні матеріали для своїх свічок. GST candles поєднує стиль та турботу про довкілля, пропонуючи естетичні рішення для дому та створюючи атмосферу затишку. Їхні вироби є чудовим поєднанням сучасного підходу та етичного виробництва.\n\n'''
            '''🔹*ZUKHVALO*: ZUKHVALO — тут можна віднайти тишу. Кожна сторінка допомагає уповільнити ритм, заспокоїти думки й насолодитися моментом тиші. Малюючи, ви поринаєте в світ українських традицій і теплих спогадів з дитинства, які повертають у безтурботні часи.\n\n'''
            '''🔹*Hutsul Authentica*: Hutsul Authentica — бренд, заснований майстрами, які віддані мистецтву Гуцульщини та прагнуть зберегти її багатовікові традиції. Вони відновлюють автентичні техніки виконання, використовуючи давні прийоми та стилі, характерні для гірського регіону. Місія бренду — відродити декоративно-прикладне мистецтво гуцулів, популяризувати його серед нових поколінь та зробити його доступним для світу. Кожен виріб Hutsul Authentica є унікальним відображенням багатої культури та історії Гуцульщини.\n\n'''
            "❤️Кожен партнер — це ще один крок до перемоги!\n\n"
        ),
        parse_mode="Markdown"
    )
# Клавіатури
# Клавіатура для "Долучитись до підсилення збору"
join_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✨ Ставай частиною дива! ✨")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Клавіатура для вибору "Янгол" або "Оберіг"
angel_guardian_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Янгол"), KeyboardButton(text="Оберіг")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Обробник для кнопки "✨ Ставай частиною дива! ✨"\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
async def choose_role(message: Message):
    await message.answer(
        text=(
            "✨ *Обери свою роль та допоможи досягти мети:*\n\n"
            "1️⃣ *🕊 Янгол: очольте свій збір та ведіть інших до благодійної мети*\n"
            "🔹 Бере на себе роль наставника та мотиватора.\n"
            "🔹 Створює свою команду і збирає від 50 тисяч гривень, залучаючи інших до участі, створюючи свою команду підсилювачів.\n\n"
            "2️⃣ *🪄 Оберіг: підтримайте одного з Янголів та станьте частиною його команди.*\n"
            "🔹 Обирає команду одного з Янголів.\n"
            "🔹 Відкриває допоміжну банку від 1 до 50 тисяч гривень.\n\n"
            "Вибери свою роль, натиснувши на відповідну кнопку:"
        ),
        reply_markup=angel_guardian_keyboard,
        parse_mode="Markdown"
    )


# Клавіатура для вибору "Янгол" або "Оберіг"
angel_guardian_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Янгол"), KeyboardButton(text="Оберіг")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

#################################################################################################ЯНГОЛ/////////////////
class AngelState(StatesGroup):
    select_region = State()
    input_amount = State()
    input_instagram = State()
    input_wish = State()
    upload_photo = State()
    input_jar_link = State()

async def angel_selected(message: Message, state: FSMContext):
    db = BotDB(os.getenv("DB_NAME"))
    try:
        # Оновлюємо роль користувача у БД
        db.update_role(message.from_user.id, "Янгол")
        await message.answer("😇 Ти обрав роль *Янгола*! Твій вибір збережено.", parse_mode="Markdown")

        # Надсилаємо контакт адміністратора
        admin_name = os.getenv("ADMIN_NAME")
        admin_name_2 = os.getenv("ADMIN_NAME_2")
        admin_phone = os.getenv("ADMIN_PHONE")
        admin_phone_2 = os.getenv("ADMIN_PHONE_2")

        await message.answer(
            f"⚠ Якщо виникнуть запитання, звертайся до адміністрації:\n\n"
            f"🔸 **{admin_name}**\n"
            f"📞 **Телефон**: {admin_phone}\n\n"
            f"🔸 **{admin_name_2}**\n"
            f"📞 **Телефон**: {admin_phone_2}",
            parse_mode="Markdown",
            reply_markup=support_keyboard
        )

        # Перехід до вибору області
        await message.answer(
            "Обери свого Янгола серед областей України, вибери рідну або близьку твоєму серцю область:",
            reply_markup=regions_keyboard
        )
        await state.set_state(AngelState.select_region)

    finally:
        db.close()

# Список областей України
regions = [
    "Вінницька", "Волинська", "Дніпропетровська", "Донецька", "Житомирська",
    "Закарпатська", "Запорізька", "Івано-Франківська", "Київська", "Кіровоградська",
    "Луганська", "Львівська", "Миколаївська", "Одеська", "Полтавська",
    "Рівненська", "Сумська", "Тернопільська", "Харківська", "Херсонська",
    "Хмельницька", "Черкаська", "Чернігівська", "Чернівецька", "АР Крим"
]

region_cases = {
    "Вінницька": "Вінницької області",
    "Волинська": "Волинської області",
    "Дніпропетровська": "Дніпропетровської області",
    "Донецька": "Донецької області",
    "Житомирська": "Житомирської області",
    "Закарпатська": "Закарпатської області",
    "Запорізька": "Запорізької області",
    "Івано-Франківська": "Івано-Франківської області",
    "Київська": "Київської області",
    "Кіровоградська": "Кіровоградської області",
    "Луганська": "Луганської області",
    "Львівська": "Львівської області",
    "Миколаївська": "Миколаївської області",
    "Одеська": "Одеської області",
    "Полтавська": "Полтавської області",
    "Рівненська": "Рівненської області",
    "Сумська": "Сумської області",
    "Тернопільська": "Тернопільської області",
    "Харківська": "Харківської області",
    "Херсонська": "Херсонської області",
    "Хмельницька": "Хмельницької області",
    "Черкаська": "Черкаської області",
    "Чернігівська": "Чернігівської області",
    "Чернівецька": "Чернівецької області",
    "АР Крим": "АР Крим"
}

regions_genitive_1 = [
    "Вінницької області", "Волинської області", "Дніпропетровської області", "Донецької області", "Житомирської області",
    "Закарпатської області", "Запорізької області", "Івано-Франківської області", "Київської області", "Кіровоградської області",
    "Луганської області", "Львівської області", "Миколаївської області", "Одеської області", "Полтавської області",
    "Рівненської області", "Сумської області", "Тернопільської області", "Харківської області", "Херсонської області",
    "Хмельницької області", "Черкаської області", "Чернігівської області", "Чернівецької області", "АР Крим"
]

# Клавіатура для вибору області
regions_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=region)] for region in regions],
    resize_keyboard=True,
    one_time_keyboard=True
)

async def choose_region(message: Message, state: FSMContext):
    region = message.text  # Отримуємо обрану область
    db = BotDB(os.getenv("DB_NAME"))
    db.update_region(message.from_user.id, region)  # Оновлюємо поле region у БД
    db.close()

    # Оновлюємо дані стану
    await state.update_data(region=region)

    # Відповідь користувачу
    await message.answer(
        f"✨ Янгол *{region} області* ✨\n\n"
        f"Дякуємо за готовність стати провідником добра у *{region} області*!\n"
        f"Вкажіть суму збору для вашого Янгола (50 000 — 100 000 грн):",
        reply_markup=ReplyKeyboardRemove(),  # Видаляємо клавіатуру
        parse_mode="Markdown"
    )
    # Переходимо до наступного стану
    await state.set_state(AngelState.input_amount)

# Логіка запиту введення посилання
async def input_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text)  # Спроба перетворити введене значення на число
        if 50000 <= amount <= 100000:  # Перевірка діапазону
            await state.update_data(amount=amount)  # Зберігаємо суму в стані
            await message.answer(
                "📎 Надішли посилання на свою банку Monobank для підтвердження (наприклад, https://send.monobank.ua/jar/...):",
                reply_markup=ReplyKeyboardRemove()  # Видаляємо клавіатуру
            )
            await state.set_state(AngelState.input_jar_link)  # Встановлюємо стан для введення посилання
        else:
            await message.answer("❌ Сума повинна бути між 50 000 та 100 000 грн. Спробуйте ще раз.")
    except ValueError:
        await message.answer("❌ Будь ласка, введіть числове значення.")

# Логіка введення та збереження посилання
async def input_jar_link(message: Message, state: FSMContext):
    jar_link = message.text
    if jar_link.startswith("https://send.monobank.ua/jar/"):  # Простий валідаційний чек
        db = BotDB(os.getenv("DB_NAME"))
        db.update_jar_link(message.from_user.id, jar_link)
        db.close()

        await state.update_data(jar_l=jar_link)
        await message.answer(
            "📸 Надішліть свій Instagram для підтвердження та комунікації:"
        )
        await state.set_state(AngelState.input_instagram)
    else:
        await message.answer("❌ Неправильний формат посилання. Спробуй ще раз.")

async def input_wish(message: Message, state: FSMContext):
    await state.update_data(instagram=message.text)
    await message.answer(
        "🎄 Твоє Різдвяне бажання 🎄\n"
        "Що мрієш отримати або здійснити на Новий рік? Напиши свої думки:"
    )
    await state.set_state(AngelState.input_wish)

async def upload_photo(message: Message, state: FSMContext):
    await state.update_data(wish=message.text)
    await message.answer("🖼 Додай фотографію для створення твоєї Янгольської картки:")
    await state.set_state(AngelState.upload_photo)

async def confirm_and_save(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("❌ Будь ласка, надішли саме фото.")
        return

    data = await state.get_data()

    ########################################################### Зберігаємо файл локально
    local_file_path = await save_photo_locally(message, message.from_user.id)

    # Збереження у базу даних
    db = BotDB(os.getenv("DB_NAME"))
    db.save_angel_details(
        user_id=message.from_user.id,
        region=data['region'],
        amount=data['amount'],
        instagram=data['instagram'],
        wish=data['wish'],
        photo_path=local_file_path,
        jar_l=data['jar_l']
    )
    db.close()

    await message.answer(
        f"🌟 Вітаємо! Ти — Янгол *{region_cases.get(data['region'], data['region'])}*.\n"
        f"Твій збір на *{data['amount']} грн* відправлено на опрацювання, очікуй…",
        parse_mode="Markdown",
        reply_markup=support_keyboard  # Додаємо клавіатуру з кнопкою
    )
    await state.clear()

support_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💙ПІДТРИМАТИ ЗБІР💛")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

async def send_payment_details_(message: Message):
    payment_details = (
        "💳 **Реквізити для підтримки** 💳\n\n"
    "**💳Номер картки банки**: 4441 1111 2852 4877\n"
    "**🔗Посилання на банку**: https://send.monobank.ua/jar/7KZbgabdGK\n\n"
        "Дякуємо за вашу підтримку! 💙💛"
    )

    await message.answer(payment_details, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())

#################################################################################################ЗБЕРЕЖЕННЯ ФОТО/////////////////
async def save_photo_locally(message: Message, user_id: int):
    # Отримуємо фото з повідомлення
    photo = message.photo[-1]
    file_info = await message.bot.get_file(photo.file_id)
    file_path = file_info.file_path

    # Локальна директорія для збереження фото
    save_directory = "photos"
    os.makedirs(save_directory, exist_ok=True)

    # Створюємо шлях до файлу
    local_file_path = os.path.join(save_directory, f"user_{user_id}.jpg")

    # Завантажуємо фото
    await message.bot.download_file(file_path, local_file_path)
    return local_file_path


#################################################################################################ОБЕРІГ/////////////////
# Клавіатура для списку Янголів
def build_angel_keyboard(angels):
    """Будує клавіатуру зі списком Янголів."""
    keyboard = [
        [KeyboardButton(text=f"{angel['name']} ({angel['region']})")] for angel in angels
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)

class GuardianState(StatesGroup):
    choose_angel = State()
    input_amount = State()
    input_instagram = State()
    input_wish = State()
    upload_photo = State()

async def guardian_selected(message: Message, state: FSMContext):
    db = BotDB(os.getenv("DB_NAME"))
    try:
        # Оновлюємо роль користувача
        db.update_role(message.from_user.id, "Оберіг")
        await message.answer("🛡️ Ти обрав роль *Оберіг*! Твій вибір збережено.", parse_mode="Markdown")

        # Отримуємо список Янголів із БД
        angels = db.get_angels()  # Метод отримання Янголів
        if not angels:
            await message.answer("❌ Наразі немає доступних Янголів для підтримки.")
            return

        # Надсилаємо список Янголів
        await message.answer(
            "🕊 *Обери Янгола, якого хочеш підтримати 🕊*\n\n"
            "Список Янголів, які вже очолили збір у різних областях:",
            reply_markup=build_angel_keyboard(angels),
            parse_mode="Markdown"
        )
        await state.set_state(GuardianState.choose_angel)

    finally:
        db.close()

async def choose_angel(message: Message, state: FSMContext):
    chosen_angel = message.text  # Текст кнопки (ім'я Янгола та область)
    db = BotDB(os.getenv("DB_NAME"))
    angels = db.get_angels()
    db.close()

    # Знаходимо обраного Янгола
    angel = next((angel for angel in angels if f"{angel['name']} ({angel['region']})" == chosen_angel), None)

    if not angel:
        await message.answer("❌ Не вдалося знайти інформацію про обраного Янгола. Спробуйте ще раз.")
        return

    await state.update_data(
    chosen_angel={
        'name': angel['name'],
        'region': angel['region'],
        'jar_link': angel['jar_link']
    }
)
    # Відправляємо інформацію про Янгола разом із банкою
    await message.answer(
        f"🌟 *Команда Янгола {angel['name']} із {angel['region']} області* 🌟\n\n"
        f"📎 Посилання на банку:({angel['jar_link']})\n\n"
        "🎯 Вкажи свою цільову суму підтримки (1 000 — 20 000 грн):",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )

    await state.set_state(GuardianState.input_amount)
async def input_guardian_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
        if 1000 <= amount <= 20000:
            await state.update_data(amount=amount)
            await message.answer("📸 Надішли свій Instagram для підтвердження та комунікації:")
            await state.set_state(GuardianState.input_instagram)
        else:
            await message.answer("❌ Сума повинна бути між 1 000 та 20 000 грн. Спробуйте ще раз:")
    except ValueError:
        await message.answer("❌ Будь ласка, введи числове значення (1 000 – 20 000 грн).")

async def input_guardian_instagram(message: Message, state: FSMContext):
    instagram = message.text
    await state.update_data(instagram=instagram)

    # Запит на різдвяне побажання
    await message.answer(
        "🎄 Твоє Різдвяне побажання 🎄\n\n"
        "Поділись мрією або теплим бажанням на Новий рік:"
    )
    await state.set_state(GuardianState.input_wish)

async def input_guardian_wish(message: Message, state: FSMContext):
    wish = message.text
    await state.update_data(wish=wish)

    # Запит на завантаження фото
    await message.answer("🖼 Додай фото для створення Оберегу:")
    await state.set_state(GuardianState.upload_photo)

async def upload_guardian_photo(message: Message, state: FSMContext, bot: Bot):
    if not message.photo:
        await message.answer("❌ Будь ласка, надішли саме фото.")
        return

    # Збереження фото локально
    photo_path = await save_photo_locally(message, message.from_user.id)

    # Отримання даних зі стану
    data = await state.get_data()

    # Збереження у базу даних
    db.save_guardian_details(
        user_id=message.from_user.id,
        chosen_angel=data['chosen_angel']['name'],  # Передаємо ім'я янгола
        amount=data['amount'],                      # Передаємо суму
        instagram=data['instagram'],                # Instagram оберега
        wish=data['wish'],                          # Побажання
        photo_path=photo_path,                      # Шлях до фото
        jar_link=data['chosen_angel']['jar_link']   # Посилання на банку
    )

    # Підтвердження
# Підтвердження
    await message.answer(
        f"🎁 Вітаємо у команді Янгола *{data['chosen_angel']['name']} ({data['chosen_angel']['region']} область)*!\n"
        f"Твій збір на *{data['amount']} грн* відправлено на опрацювання, очікуй…",
        parse_mode="Markdown",
        reply_markup=support_keyboard  # Додаємо клавіатуру з кнопкою
    )
    await state.clear()

#################################################################################################/////////////////
# Клавіатура з кнопкою "Підтримати"
support_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💙ПІДТРИМАТИ ЗБІР💛")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

async def send_payment_details(message: Message):
    payment_details = (
        "💳 **Реквізити для підтримки** 💳\n\n"
    "**💳Номер картки банки**: 4441 1111 2852 4877\n"
    "**🔗Посилання на банку**: https://send.monobank.ua/jar/7KZbgabdGK\n\n"
        "Дякуємо за вашу підтримку! 💙💛"
    )

    await message.answer(payment_details, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
