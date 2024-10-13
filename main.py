import nest_asyncio

nest_asyncio.apply()
import logging
import os
import json
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

from config import BOT_TOKEN

# Налаштування логування
logging.basicConfig(level=logging.INFO)

# Встановлення змінної оточення для локального тестування
if 'ENV' not in os.environ:
    os.environ['ENV'] = 'local'  # Для локального тестування

# Логування значення ENV
logging.info(f"Значення ENV: {os.environ.get('ENV')}")

TOKEN = BOT_TOKEN

# Шлях до файлу
try:
    with open("Updated_EVI.json", 'r', encoding='utf-8') as f:
        exams_data = json.load(f)
except FileNotFoundError:
    logging.error("Файл Updated_EVI.json не знайдено.")
    exams_data = {}
except json.JSONDecodeError:
    logging.error("Помилка декодування JSON.")
    exams_data = {}

# Системи оцінювання для 2019-2021 та 2022 років
score_conversion_2019_2021 = {
    0: "не склав", 1: "не склав", 2: "не склав", 3: "не склав", 4: "не склав",
    5: "не склав", 6: "не склав", 7: "не склав", 8: "не склав", 9: "не склав",
    10: "не склав", 11: "не склав", 12: 100, 13: 106, 14: 111, 15: 116, 16: 121,
    17: 125, 18: 128, 19: 132, 20: 135, 21: 138, 22: 141, 23: 144, 24: 147,
    25: 150, 26: 153, 27: 156, 28: 159, 29: 162, 30: 165, 31: 168, 32: 170,
    33: 173, 34: 177, 35: 180, 36: 183, 37: 186, 38: 189, 39: 192, 40: 195,
    41: 197, 42: 200
}

score_conversion_2022 = {
    0: "не склав", 1: "не склав", 2: "не склав", 3: "не склав", 4: "не склав",
    5: 100, 6: 108, 7: 116, 8: 124, 9: 130, 10: 134, 11: 137, 12: 140, 13: 143, 14: 146, 15: 148, 16: 150, 17: 152,
    18: 154, 19: 157, 20: 160, 21: 162, 22: 164, 23: 167,
    24: 170, 25: 174, 26: 177, 27: 182, 28: 188, 29: 194, 30: 200
}

rating_messages = {
    "не склав": "Ooops, може спробуєш ще раз? Рекомендуємо повчитися ще🙃",
    (100, 120): "Congratulations, поріг пройдено🤗",
    (121, 160): "Well done, непоганий результат😍",
    (161, 180): "AMAZING, чудовий результат🤝",
    (181, 199): "OMG YOUR RESULT IS REALLY COOL😯",
    200: "This is the highest score, we are so proud of you!🥳"
}


def convert_score_to_200_scale(year, score):
    if year in ['2019', '2020', '2021']:
        conversion = score_conversion_2019_2021
    else:
        conversion = score_conversion_2022
    return conversion.get(score, "не склав")


# Команда /обробник запуску
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("2022/2023", callback_data='2022')],
        [InlineKeyboardButton("2021", callback_data='2021')],
        [InlineKeyboardButton("2020", callback_data='2020')],
        [InlineKeyboardButton("2019", callback_data='2019')],
        [InlineKeyboardButton(
            "Усе про ЄВІ📝(процедура реєстрації, календар проведення та ін.)",
            url='https://testportal.gov.ua/yedynyj-vstupnyj-ispyt-2/')],
        [InlineKeyboardButton("Корисні ресурси📖", callback_data='resources')],
        [InlineKeyboardButton("Залиште Feedback 📣", callback_data='leave_feedback')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text(
            '🎓Вітаю Вас в боті для підготовки до ЄВІ! Допоможу Вам успішно скласти іспит з англійської✍️! Який рік хочеш пропрацювати?📅:',
            reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text(
            '🎓Вітаю Вас в боті для підготовки до ЄВІ! Допоможу Вам успішно скласти іспит з англійської✍️! Який рік хочеш пропрацювати?📅:',
            reply_markup=reply_markup)

        context.user_data['text'] = 'Текст, який потрібно зберегти'


# Аналогічно для функції resources
async def resources(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    resource_message = (
        "Корисні ресурси📖:\n"
        "- Вебінар «ЄВІ-2024: Стратегії і лайфхаки» (стратегії і лайфхаки проходження тесту ЄВІ: з англійської мови, частини ТЗНК) (https://www.youtube.com/watch?v=u3is1GuWWVk)\n"
        "- Розбір демо тесту ЄВІ 2022/2023 з англійської мови: завдання №4 (1) (http://www.youtube.com/watch?v=KwUEPw5GtgA)\n"
        "- ЄВІ англійська 2023 розбір завдання 1 ДЕМО тесту УЦОЯО (https://www.youtube.com/watch?v=NOj2yZP4rCc)\n"
        "- Не починай готуватися до ЄВІ, поки не подивишся це відео і логіка (ТЗНК) 2024 (https://www.youtube.com/watch?v=BZWPmlZRZb8)\n"
        "- Як успішно скласти ЄВІ-2024 (лайфхаки, структура ЄВІ з англійської) (https://grade.ua/uk/blog/uk-how-to-hack-evi/)\n"
        "- ЄВІ: лайфхаки для підготовки до тесту з англійської мови (https://onlinelawschool.pro/znoenglish?gad_source=1&gclid=Cj0KCQjw1qO0BhDwARIsANfnkv9G1yd_ROTHW8PiVNPqnwjopsRgYrK3F6g1cGY-K6M42POmNmh6KnYaApbeEALw_wcB)\n"
        "- Розбір ЄВІ слів, які полегшать вступ до магістратури | єдиний вступний іспит (за тестом 2020 року) (https://www.youtube.com/watch?v=wWbAO5s7goE)\n"
    )
    keyboard = [
        [InlineKeyboardButton("Повернутися до головного меню🏠", callback_data='back_to_main_menu')]
    ]

    if update.message:
        await update.message.reply_text(resource_message, reply_markup=InlineKeyboardMarkup(keyboard))
    elif update.callback_query:
        await update.callback_query.message.reply_text(resource_message, reply_markup=InlineKeyboardMarkup(keyboard))

    # Зберігаємо текст у context.user_data без зміни update.message
    context.user_data['text'] = 'Текст, який потрібно зберегти'


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    await start(update, context)


# Вибір року
async def year_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    selected_year = query.data
    context.user_data['selected_year'] = selected_year
    context.user_data['total_score'] = 0
    context.user_data['scores'] = {'Reading': 0, 'Use of English': 0}

    if exams_data:
        parts = next(part['parts'] for part in exams_data['exam_years'] if str(part['year']) == selected_year)
        keyboard = [
            [InlineKeyboardButton(part.get('name', 'Без назви'), callback_data=f"part_{part.get('name', 'unknown')}")]
            for part in parts]
        keyboard.append([InlineKeyboardButton("Повернутися до головного меню🏠", callback_data='back_to_main_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"Виберіть частину для {selected_year} року📚:", reply_markup=reply_markup)


# Обробка вибору
async def part_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    selected_part = query.data.split('_')[1]
    context.user_data['selected_part'] = selected_part
    context.user_data['part_score'] = 0

    selected_year = context.user_data['selected_year']
    if exams_data:
        parts = next(part['parts'] for part in exams_data['exam_years'] if str(part['year']) == selected_year)
        tasks = next(part['tasks'] for part in parts if part.get('name', 'unknown') == selected_part)
        context.user_data['tasks'] = tasks
        context.user_data['current_task_index'] = 0

        await send_task(update, context)


# Надсилання повідомлень користувачу
async def send_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tasks = context.user_data['tasks']
    current_task_index = context.user_data['current_task_index']
    task = tasks[current_task_index]

    text = f"Завдання {task['task_number']}:\n{task['instructions']}\n\n"
    for t in task['texts']:
        text += f"{t}\n\n"

    for i, choice in enumerate(task['choices']):
        text += f"{chr(65 + i)}. {choice}\n"

    keyboard = [
        [InlineKeyboardButton(chr(65 + i), callback_data=f"answer_{chr(65 + i)}")] for i in range(len(task['choices']))
    ]
    keyboard.append([InlineKeyboardButton("Закінчити тест❌", callback_data='finish')])
    keyboard.append(
        [InlineKeyboardButton("Словнич🆗", url='https://www.dictionary.cambridge.org/uk/dictionary/english-ukrainian/')])
    keyboard.append([InlineKeyboardButton("Назад до частин цього року◀️", callback_data='back_to_parts')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text=text, reply_markup=reply_markup)


# Обробка відповідей користувача
# Обробка відповідей користувача
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_answer = query.data.split('_')[1]
    tasks = context.user_data['tasks']
    current_task_index = context.user_data['current_task_index']
    task = tasks[current_task_index]
    correct_answer = task['answers'][0]

    if user_answer == correct_answer:
        context.user_data['part_score'] += int(task['other_option']['score'])
        response = "✅Правильно, молодець, так тримати😊!"
        next_button = [
            [InlineKeyboardButton("ДАЛІ▶️", callback_data='next_task')]  # Додаємо обробник для "ДАЛІ"
        ]
    else:
        response = f"❌Неправильно, треба бути уважніше😞! Правильна відповідь: {correct_answer}"
        next_button = [
            [InlineKeyboardButton("Назад до завдання◀️", callback_data='retry_task')],
            [InlineKeyboardButton("ДАЛІ▶️", callback_data='next_task')]  # Додаємо обробник для "ДАЛІ"
        ]

    reply_markup = InlineKeyboardMarkup(next_button)
    await query.edit_message_text(text=response, reply_markup=reply_markup)


# Функція для обробки "Назад до завдання"
async def handle_retry_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # Отримуємо індекс поточного завдання
    current_task_index = context.user_data['current_task_index']
    tasks = context.user_data['tasks']

    if 0 <= current_task_index < len(tasks):  # Перевірка наявності завдання
        task = tasks[current_task_index]

        # Форматування тексту завдання
        task_number = f"Завдання {task['task_number']}:"  # Форматування номера завдання
        instructions = task.get('instructions', "Текст завдання не знайдено.")
        texts = "\n\n".join(task.get('texts', ["Текст не знайдено."]))
        choices = "\n".join([f"{chr(65+i)}. {choice}" for i, choice in enumerate(task.get('choices', []))])

        # Формуємо відповідь
        response = f"{task_number}\n{instructions}\n\n{texts}\n\nВаріанти:\n{choices}"

        # Кнопка тільки "ДАЛІ" для продовження
        next_button = [
            [InlineKeyboardButton("ДАЛІ▶️", callback_data='next_task')]
        ]

        reply_markup = InlineKeyboardMarkup(next_button)
        await query.edit_message_text(text=response, reply_markup=reply_markup)
    else:
        await query.edit_message_text(text="Завдання не знайдено.")


# Функція для обробки переходу до наступного завдання
async def handle_next_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    current_task_index = context.user_data['current_task_index']
    tasks = context.user_data['tasks']

    # Переходьте до наступного завдання
    if current_task_index + 1 < len(tasks):
        context.user_data['current_task_index'] += 1
        await send_task(update, context)  # Відправити наступне завдання
    else:
        # Якщо це було останнє завдання, покажіть результати
        await send_part_results(update, context)


# Надсилання результатів за розділом
async def send_part_results(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    part_score = context.user_data['part_score']
    selected_part = context.user_data['selected_part']
    total_tasks = len(context.user_data['tasks'])  # Припущення: кожне завдання дає один бал

    # Оновлюємо загальний рахунок
    context.user_data['total_score'] += part_score

    # Створення списку кнопок для частини Reading
    part_buttons = []

    if selected_part == 'Reading':
        part_buttons.append([InlineKeyboardButton("ПЕРЕЙТИ до Use of English🚀", callback_data='go_to_use_of_english')])
        part_buttons.append([InlineKeyboardButton("Назад до частин цього року◀️", callback_data='back_to_parts')])
        part_buttons.append([InlineKeyboardButton("Повернутися до головного меню🏠", callback_data='back_to_main_menu')])

        # Створення інтерфейсу для кнопок
        reply_markup = InlineKeyboardMarkup(part_buttons)

        # Відправлення повідомлення з результатом та кнопками для Reading
        await update.callback_query.message.reply_text(
            f"Ви закінчили цю частину✔️: {selected_part}.\n\nВаш результат📈: {part_score}/{total_tasks} балів.",
            reply_markup=reply_markup
        )

    # Якщо частина 'Use of English', показуємо тільки main_buttons
    elif selected_part == 'Use of English':
        main_buttons = [
            [InlineKeyboardButton("Назад до частин цього року◀️", callback_data='back_to_parts')],
            [InlineKeyboardButton("Повернутися до головного меню🏠", callback_data='back_to_main_menu')],
            [InlineKeyboardButton("Дізнатися результат проходження тесту🏆", callback_data='finish')],
            [InlineKeyboardButton("Словнич🆗",
                                  url='https://www.dictionary.cambridge.org/uk/dictionary/english-ukrainian/')],
            [InlineKeyboardButton("Корисні ресурси📖", callback_data='resources')]
        ]

        # Створення інтерфейсу для кнопок
        main_reply_markup = InlineKeyboardMarkup(main_buttons)

        # Відправлення повідомлення з результатом та кнопками для Use of English
        await update.callback_query.message.reply_text(
            f"Ви закінчили цю частину✔️: {selected_part}.\n\nВаш результат📈: {part_score}/{total_tasks} балів.",
            reply_markup=main_reply_markup
        )


def calculate_results():
    # Приклад логіки для підрахунку результатів
    total_score = 'total_score'  # Задайте вашу логіку підрахунку
    max_score = 'max_score'  # Максимальний можливий бал
    return {'total_score': total_score, 'max_score': max_score}


async def handle_next_button(update: Update) -> None:
    query = update.callback_query
    # Збір результатів тесту
    # Якщо 'user_id' не потрібен, можна видалити цей рядок
    results = calculate_results()  # Якщо не використовуєте 'user_id', приберіть його з функції

    total_score = results['total_score']
    max_score = results['max_score']

    # Формування тексту для відправки
    result_text = f"Ви закінчили цей тест✔️\nВаш результат: {total_score}/{max_score} балів."

    # Оновлення повідомлення
    await query.message.edit_text(result_text)


async def handle_go_to_use_of_english(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    selected_year = context.user_data['selected_year']
    if exams_data:
        parts = next(part['parts'] for part in exams_data['exam_years'] if str(part['year']) == selected_year)
        use_of_english_part = next((part for part in parts if part.get('name') == 'Use of English'), None)

        if use_of_english_part:
            context.user_data['selected_part'] = 'Use of English'
            context.user_data['part_score'] = 0
            context.user_data['tasks'] = use_of_english_part['tasks']
            context.user_data['current_task_index'] = 0

            await send_task(update, context)
        else:
            await query.edit_message_text(text="Частина 'Use of English' не знайдена.")


async def handle_resources(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await resources(update, context)


# Функція для відображення результату після завершення тесту
async def finish_test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    selected_year = context.user_data['selected_year']
    total_score = context.user_data['total_score']

    # Конвертуємо результат за 200-бальною шкалою
    converted_score = convert_score_to_200_scale(selected_year, total_score)

    # Підбираємо відповідне повідомлення для рейтингу
    for key, message in rating_messages.items():
        if isinstance(key, tuple) and key[0] <= converted_score <= key[1]:
            rating_message = message
            break
        elif converted_score == key:
            rating_message = message
            break
    else:
        rating_message = rating_messages["не склав"]

    # Показуємо користувачу фінальний результат
    result_message = (
        f"Вітаємо👏! Тест завершено✔️ {selected_year} рік.\n"
        f"Ваш загальний бал🎯: {total_score} балів з можливих.\n"
        f"Ваш результат за 200-бальною системою оцінювання 🏅: {converted_score}.\n"
        f"{rating_message}"
    )

    # Створюємо клавіатуру
    keyboard = [
        [InlineKeyboardButton("Назад до частин цього року◀️", callback_data='back_to_parts')],
        [InlineKeyboardButton("Повернутися до головного меню🏠", callback_data='back_to_main_menu')],
        [InlineKeyboardButton(
            "Усе про ЄВІ📝 (процедура реєстрації, календар проведення та ін.)",
            url='https://testportal.gov.ua/yedynyj-vstupnyj-ispyt-2/')],
        [InlineKeyboardButton("Корисні ресурси📖", callback_data='resources')],
    ]

    # Показати результат і передати клавіатуру
    await query.edit_message_text(result_message, reply_markup=InlineKeyboardMarkup(keyboard))


async def back_to_parts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    selected_year = context.user_data['selected_year']
    if exams_data:
        parts = next(part['parts'] for part in exams_data['exam_years'] if str(part['year']) == selected_year)
        keyboard = [
            [InlineKeyboardButton(part.get('name', 'Без назви'), callback_data=f"part_{part.get('name', 'unknown')}")]
            for part in parts]
        keyboard.append([InlineKeyboardButton("Повернутися до головного меню🏠", callback_data='back_to_main_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"Виберіть частину для {selected_year} року📚:", reply_markup=reply_markup)


async def handle_back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start(update, context)


# Функція для читання відгуків з feedback.json
def read_feedbacks():
    if os.path.exists("feedback.json"):
        with open("feedback.json", "r", encoding="utf-8") as feedback_file:
            return json.load(feedback_file)
    return {"feedbacks": []}


# Функція для ініціалізації початкового feedback.json, якщо файл не існує
def initialize_feedback_file():
    initial_data = {"feedbacks": []}
    if not os.path.exists("feedback.json"):
        with open("feedback.json", "w", encoding="utf-8") as feedback_file:
            json.dump(initial_data, feedback_file, ensure_ascii=False, indent=4)


# Функція для додавання відгуку та оновлення статистики
def add_feedback(user_id, feedback, rating):
    feedback_data = {
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        "feedback": feedback,
        "rating": rating
    }

    try:
        data = read_feedbacks()
        data["feedbacks"].append(feedback_data)

        with open("feedback.json", "w", encoding="utf-8") as feedback_file:
            json.dump(data, feedback_file, ensure_ascii=False, indent=4)

        # Оновлення статистики після додавання відгуку
        increment_statistics(rating)  # rating може бути "positive", "negative", "simple_yes" або "simple_no"
    except Exception as e:
        logging.error(f"Помилка при додаванні відгуку: {e}")


# Функція для завантаження або ініціалізації статистики
def load_statistics():
    if os.path.exists("statistics.json"):
        with open("statistics.json", "r", encoding="utf-8") as file:
            stats_data = json.load(file)
            print("Статистика завантажена:", stats_data)
            return stats_data
    else:
        print("Файл statistics.json не знайдено. Ініціалізація...")
        initialize_statistics()
        return load_statistics()  # Перезапустимо функцію після ініціалізації


def initialize_statistics():
    print("Ініціалізація статистики...")
    stats_data = {
        "with_positive_comments": 0,
        "with_negative_comments": 0,
        "yes": 0,
        "no": 0
    }
    with open("statistics.json", "w", encoding="utf-8") as stats_file:
        json.dump(stats_data, stats_file, ensure_ascii=False, indent=4)
    print("Файл statistics.json ініціалізовано з початковими значеннями:", stats_data)


# Функція для оновлення статистики на основі типу відгуку
def increment_statistics(feedback_type):
    stats_data = load_statistics()
    if feedback_type == "positive":
        stats_data["with_positive_comments"] += 1
    elif feedback_type == "negative":
        stats_data["with_negative_comments"] += 1
    elif feedback_type == "yes":
        stats_data["yes"] += 1
    elif feedback_type == "no":
        stats_data["no"] += 1

    save_statistics(stats_data)  # Викликаємо функцію збереження


def save_statistics(stats_data):
    with open("statistics.json", "w", encoding="utf-8") as stats_file:
        json.dump(stats_data, stats_file, ensure_ascii=False, indent=4)


# Обробник для запиту відгуку
async def leave_feedback(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    feedback_keyboard = [
        [InlineKeyboardButton("ТАК", callback_data='feedback_yes')],
        [InlineKeyboardButton("НІ", callback_data='feedback_no')]
    ]
    reply_markup = InlineKeyboardMarkup(feedback_keyboard)
    await query.edit_message_text("Чи сподобався Вам бот🤔💭?", reply_markup=reply_markup)


# Обробник для кнопки "ТАК"
async def handle_feedback_yes(update: Update, context):
    increment_statistics("yes")  # Оновлення статистики для простого "так"

    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "Дякую за Ваш відгук🫶🏻🙏💬! Якщо хочете, залиште короткий коментар про ваше враження:"
    )
    context.user_data['awaiting_comment'] = True

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Повернення до головного меню🏠", callback_data='back_to_main_menu')]]
    )
    await query.message.reply_text("Ваш коментар:", reply_markup=reply_markup)


async def handle_feedback_no(update, context):
    increment_statistics("no")  # Оновлення статистики для простого "ні"

    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "Дякую за чесність, залиште вашу пропозицію😊📝:"
    )
    context.user_data['awaiting_feedback'] = True

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Повернення до головного меню🏠", callback_data='back_to_main_menu')]]
    )
    await query.message.reply_text("Ваш коментар:", reply_markup=reply_markup)


async def back_to_main_menu(update: Update) -> None:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Вітаємо в головному меню! Що ви хочете зробити далі?")

    # Додайте тут ваші основні варіанти меню


# Обробник для коментарів користувачів після відгуку
async def handle_user_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    feedback = update.message.text

    if context.user_data.get('awaiting_feedback'):
        add_feedback(user_id, feedback, 'negative')  # Відгук з коментарем
        context.user_data['awaiting_feedback'] = False

        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Повернення до головного меню🏠", callback_data='back_to_main_menu')]]
        )
        await update.message.reply_text(
            "Дякую за вашу пропозицію! 🫶🏻💖",
            reply_markup=reply_markup
        )

    elif context.user_data.get('awaiting_comment'):
        add_feedback(user_id, feedback, 'positive')  # Відгук з коментарем
        context.user_data['awaiting_comment'] = False

        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Повернення до головного меню🏠", callback_data='back_to_main_menu')]]
        )
        await update.message.reply_text(
            "Дякую за ваш коментар! 🫶🏻💖",
            reply_markup=reply_markup
        )


# Функція для скидання статистики
async def reset_statistics(update: Update) -> None:
    logging.info("Скидання статистики...")
    stats_data = {
        "with_positive_comments": 0,
        "with_negative_comments": 0,
        "yes": 0,
        "no": 0
    }
    with open("statistics.json", "w", encoding="utf-8") as stats_file:
        json.dump(stats_data, stats_file, ensure_ascii=False, indent=4)
    await update.message.reply_text("Статистика була скинута!")

    # Приклад використання context
    logging.info(f"User {update.effective_user.id} скинув статистику.")


async def set_webhook(application) -> None:
    webhook_url = "https://yourdomain.com/your_webhook_path"  # Заміни на ваш URL
    await application.bot.set_webhook(webhook_url)


async def handle_reset_command(update: Update) -> None:
    await reset_statistics(update)  # Виклик скидання статистики


async def clear_feedback(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Виконується команда /clear_feedback")
    initial_data = {"feedbacks": []}
    try:
        with open("feedback.json", "w", encoding="utf-8") as feedback_file:
            json.dump(initial_data, feedback_file, ensure_ascii=False, indent=4)
        await update.message.reply_text("Всі відгуки були очищені!")
    except Exception as e:
        logging.error(f"Помилка при очищенні відгуків: {e}")
        await update.message.reply_text("Виникла помилка при очищенні відгуків.")


# Функція для отримання статистики
async def stats(update: Update) -> None:
    stats_data = load_statistics()
    response_message = (
        f"Позитивні відгуки: {stats_data['with_positive_comments']}\n"
        f"Негативні відгуки: {stats_data['with_negative_comments']}\n"
        f"Прості так: {stats_data['yes']}\n"
        f"Прості ні: {stats_data['no']}"
    )
    await update.message.reply_text(response_message)


async def main() -> None:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )

    # Ініціалізація файлів, якщо їх немає
    initialize_feedback_file()  # Викликаємо функцію
    initialize_statistics()

    application = Application.builder().token(TOKEN).build()

    # Налаштування вебхука
    await set_webhook(application)

    application.add_handler(CommandHandler("reset", handle_reset_command))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CallbackQueryHandler(leave_feedback, pattern='leave_feedback'))
    application.add_handler(CallbackQueryHandler(handle_feedback_yes, pattern='feedback_yes'))
    application.add_handler(CallbackQueryHandler(handle_feedback_no, pattern='feedback_no'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_feedback))
    application.add_handler(CallbackQueryHandler(handle_retry_task, pattern='^retry_task$'))
    application.add_handler(CallbackQueryHandler(handle_next_task, pattern='^next_task$'))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(year_choice, pattern='^2022$|^2021$|^2020$|^2019$'))
    application.add_handler(CallbackQueryHandler(part_choice, pattern='^part_'))
    application.add_handler(CallbackQueryHandler(handle_answer, pattern='^answer_'))
    application.add_handler(CallbackQueryHandler(handle_go_to_use_of_english, pattern='^go_to_use_of_english$'))
    application.add_handler(CallbackQueryHandler(handle_resources, pattern='^resources$'))
    application.add_handler(CallbackQueryHandler(finish_test, pattern='^finish$'))
    application.add_handler(CallbackQueryHandler(back_to_parts, pattern='^back_to_parts$'))
    application.add_handler(CallbackQueryHandler(restart, pattern='^restart$'))
    application.add_handler(CallbackQueryHandler(lambda u, c: start(u, c), pattern='^back_to_main_menu$'))
    application.add_handler(CallbackQueryHandler(lambda u, c: resources(u, c), pattern='^back_to_main_menu$'))
    application.add_handler(CallbackQueryHandler(back_to_main_menu, pattern='back_to_main_menu'))
    application.add_handler(CommandHandler("clear_feedback", clear_feedback))
    application.add_handler(CallbackQueryHandler(back_to_parts, pattern='^back_to_parts$'))
    application.add_handler(CallbackQueryHandler(handle_back_to_main_menu, pattern='back_to_main_menu'))

    # Видалення вебхука (якщо є)
    await application.bot.delete_webhook()

    application.run_polling()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
