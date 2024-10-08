import nest_asyncio

nest_asyncio.apply()
import json
import logging

import os
from datetime import datetime

from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

from config import BOT_TOKEN

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
def create_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("2022/2023", callback_data='2022')],
        [InlineKeyboardButton("2021", callback_data='2021')],
        [InlineKeyboardButton("2020", callback_data='2020')],
        [InlineKeyboardButton("2019", callback_data='2019')],
        [InlineKeyboardButton("Усе про ЄВІ📝", url='https://testportal.gov.ua/yedynyj-vstupnyj-ispyt-2')],
        [InlineKeyboardButton("Корисні ресурси📖", callback_data='resources')],
        [InlineKeyboardButton("Залиште Feedback 📣", callback_data='leave_feedback')]
    ]
    return InlineKeyboardMarkup(keyboard)


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


from telegram import InlineKeyboardButton, InlineKeyboardMarkup


async def handle_retry_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    await send_task(update, context)  # Знову надішліть те саме завдання

    # Додайте кнопку "Далі"
    keyboard = [
        [
            InlineKeyboardButton("Далі", callback_data='next_task')
            ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Відправте повідомлення з новою клавіатурою
    await query.message.edit_reply_markup(reply_markup)


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
            [InlineKeyboardButton("Дізнатися результат проходження тесту🏆", callback_data='finish')],
            [InlineKeyboardButton("Назад до частин цього року◀️", callback_data='back_to_parts')],
            [InlineKeyboardButton("Повернутися до головного меню🏠", callback_data='back_to_main_menu')],
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

    # Формування тексту для відправлення
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
        [InlineKeyboardButton("Залиште Feedback 📣", callback_data='leave_feedback')]
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


async def leave_feedback(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    feedback_keyboard = [
        [InlineKeyboardButton("ТАК", callback_data='feedback_yes')],
        [InlineKeyboardButton("НІ", callback_data='feedback_no')]
    ]
    reply_markup = InlineKeyboardMarkup(feedback_keyboard)

    await query.edit_message_text("Чи сподобався Вам бот🤔💭?", reply_markup=reply_markup)


async def handle_feedback_yes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Дякую за Ваш відгук🫶🏻🙏💬! Якщо хочете, залиште короткий коментар про ваше враження:"
    )
    context.user_data['awaiting_comment'] = True  # Стан для коментаря

    reply_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Повернення до головного меню🏠", callback_data='back_to_main_menu')]
        ]
    )
    await query.message.reply_text("Ваш коментар:", reply_markup=reply_markup)


async def handle_feedback_no(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Дякую за чесність, залиште вашу пропозицію😊📝:"
    )
    context.user_data['awaiting_feedback'] = True

    reply_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Повернення до головного меню🏠", callback_data='back_to_main_menu')]
        ]
    )
    await query.message.reply_text("Ваш коментар:", reply_markup=reply_markup)


async def back_to_main_menu(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    reply_markup = create_main_menu_keyboard()  # Виклик функції для створення клавіатури
    await query.edit_message_text("Вітаємо у головному меню! Виберіть опцію:", reply_markup=reply_markup)


async def handle_user_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('awaiting_feedback'):
        feedback = update.message.text
        rating = context.user_data.get('feedback_rating', 'negative')

        # Зберегти відгук
        add_feedback(update.message.from_user.id, feedback, rating)

        context.user_data['awaiting_feedback'] = False
        await update.message.reply_text("Дякую за вашу пропозицію! 🫶🏻💖", reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Повернення до головного меню🏠", callback_data='back_to_main_menu')]]))

    elif context.user_data.get('awaiting_comment'):
        comment = update.message.text
        add_feedback(update.message.from_user.id, comment, "positive")  # Вважаємо коментар позитивним

        context.user_data['awaiting_comment'] = False
        await update.message.reply_text("Дякую за ваш коментар! 🫶🏻💖", reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Повернення до головного меню🏠", callback_data='back_to_main_menu')]]))


# Створюємо початковий файл feedback.json, якщо він не існує
initial_data = {"feedbacks": []}

with open("feedback.json", "w", encoding="utf-8") as f:
    json.dump(initial_data, f, ensure_ascii=False, indent=4)


def add_feedback(user_id, feedback, rating):
    feedback_data = {"user_id": user_id, "timestamp": datetime.now().isoformat(), "feedback": feedback,
                     "rating": rating}

    # Перевірка, чи існує файл
    if os.path.exists("feedback.json"):
        with open("feedback.json", "r", encoding="utf-8") as feedback_file:  # Renamed 'f' to 'feedback_file'
            data = json.load(feedback_file)
    else:
        data = {"feedbacks": []}

    # Додаємо новий відгук
    data["feedbacks"].append(feedback_data)

    # Записуємо оновлені дані у файл
    with open("feedback.json", "w", encoding="utf-8") as feedback_file:  # Renamed 'f' to 'feedback_file'
        json.dump(data, feedback_file, ensure_ascii=False, indent=4)


def count_positive_feedbacks():
    if os.path.exists("feedback.json"):
        with open("feedback.json", "r", encoding="utf-8") as file:  # Renamed 'f' to 'file'
            data = json.load(file)

        positive_feedbacks = [feedback for feedback in data["feedbacks"] if feedback.get("rating") == "positive"]
        return len(positive_feedbacks)
    return 0


def count_negative_feedbacks():
    if os.path.exists("feedback.json"):
        with open("feedback.json", "r", encoding="utf-8") as file:  # Renamed 'f' to 'file'
            data = json.load(file)

        negative_feedbacks = [feedback for feedback in data["feedbacks"] if feedback.get("rating") == "negative"]
        return len(negative_feedbacks)
    return 0


async def stats(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    positive_count = count_positive_feedbacks()
    negative_count = count_negative_feedbacks()
    await update.message.reply_text(
        f"Кількість позитивних відгуків: {positive_count}\nКількість негативних відгуків: {negative_count}"
    )


def save_statistics(positive_count, negative_count):
    stats_data = {
        "positive_feedbacks": positive_count,
        "negative_feedbacks": negative_count
    }

    with open("statistics.json", "w", encoding="utf-8") as file:  # Renamed 'f' to 'file'
        json.dump(stats_data, file, ensure_ascii=False, indent=4)


async def main() -> None:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )

    application = Application.builder().token(TOKEN).build()
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
    application.add_handler(CallbackQueryHandler(leave_feedback, pattern='^leave_feedback$'))
    application.add_handler(CallbackQueryHandler(handle_feedback_yes, pattern='^feedback_yes$'))
    application.add_handler(CallbackQueryHandler(handle_feedback_no, pattern='^feedback_no$'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_feedback))
    application.add_handler(CommandHandler("stats", stats))

    application.run_polling()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
