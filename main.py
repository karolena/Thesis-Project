import json
import os

# Ваш код
from config import BOT_TOKEN

# Використання токену
BOT_TOKEN = BOT_TOKEN


# Токен бота
TOKEN = os.getenv('BOT_TOKEN')
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# шлях до файлу

file_path = "Updated_EVI.json"
if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        exams_data = json.load(f)
else:
    print(f"Файл {file_path} не знайдено")
    exams_data = None

# Токен бота
TOKEN = '6357800099:AAH_9f1kk14c629YAbsyvAXVmSkNgfApdqU'

# оцінка результатів
score_conversion = {
    0: "не склав", 1: "не склав", 2: "не склав", 3: "не склав", 4: "не склав", 5: "не склав", 6: "не склав",
    7: "не склав", 8: "не склав", 9: "не склав", 10: "не склав", 11: "не склав",
    12: 100, 13: 106, 14: 111, 15: 116, 16: 121, 17: 125, 18: 128, 19: 132, 20: 135, 21: 138, 22: 141, 23: 144, 24: 147,
    25: 150, 26: 153, 27: 156, 28: 159, 29: 162, 30: 165,
    31: 168, 32: 170, 33: 173, 34: 177, 35: 180, 36: 183, 37: 186, 38: 189, 39: 192, 40: 195, 41: 197, 42: 200
}

# повідомлення про оцінку
rating_messages = {
    "не склав": "Ooops, може спробуєш ще раз? рекомендуємо повчити ще🙃",
    (100, 120): "congratulations, поріг пройдено🤗 ",
    (121, 160): "well done, непоганий результат 😍",
    (161, 180): "AMAZING, чудовий результат 🤝 ",
    (181, 199): "OMG YOUR RESULT IS REALLY COOL 😯",
    200: "This is the highest score, we are so proud of you!🥳"
}

# оцінка результатів
score_conversion = {
    0: "не склав", 1: "не склав", 2: "не склав", 3: "не склав", 4: "не склав",
    5: 100, 6: 108, 7: 116, 8: 124, 9: 130, 10: 134, 11: 137, 12: 140, 13: 143, 14: 146, 15: 148, 16: 150, 17: 152,
    18: 154, 19: 157, 20: 160, 21: 162, 22: 164, 23: 167,
    24: 170, 25: 174, 26: 177, 27: 182, 28: 188, 29: 194, 30: 200
}



# Команда /обробник запуску
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("2023", callback_data='2023')],
        [InlineKeyboardButton("2022", callback_data='2022')],
        [InlineKeyboardButton("2021", callback_data='2021')],
        [InlineKeyboardButton("2020", callback_data='2020')],
        [InlineKeyboardButton("2019", callback_data='2019')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text('Вітаю Вас в боті для підготовки до ЄВІ! Допоможу Вам успішно скласти іспит з англійської! Який рік хочеш пропрацювати?:', reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text('Вітаю Вас в боті для підготовки до ЄВІ! Допоможу Вам успішно скласти іспит з англійської! Який рік хочеш пропрацювати?:', reply_markup=reply_markup)


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

    if exams_data:
        parts = next(part['parts'] for part in exams_data['exam_years'] if str(part['year']) == selected_year)
        keyboard = [
            [InlineKeyboardButton(part.get('name', 'Без назви'), callback_data=f"part_{part.get('name', 'unknown')}")]
            for part in parts]
        keyboard.append([InlineKeyboardButton("Назад", callback_data='back_to_years')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"Виберіть розділ для {selected_year} року:", reply_markup=reply_markup)


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
    keyboard.append([InlineKeyboardButton("Словнич🆗", url='https://www.dictionary.cambridge.org/uk/dictionary/english-ukrainian/')])
    keyboard.append([InlineKeyboardButton("Назад◀️", callback_data='back_to_parts')])
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
        response = f"✅ Правильно, продовжуй!"
    else:
        response = f"❌ Неправильно. Правильна відповідь: {correct_answer}"

    await query.edit_message_text(text=response)

    context.user_data['current_task_index'] += 1
    if context.user_data['current_task_index'] < len(tasks):
        keyboard = [
            [InlineKeyboardButton("Далі➡️", callback_data='next')],
            [InlineKeyboardButton("Завершити тест❌", callback_data='finish')],
            [InlineKeyboardButton("Словнич🆗", url='https://www.dictionary.cambridge.org/uk/dictionary/english-ukrainian/')],
            [InlineKeyboardButton("Назад◀️", callback_data='back_to_parts')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(text=f"Ви відповіли на завдання.", reply_markup=reply_markup)
    else:
        context.user_data['total_score'] += context.user_data['part_score']
        await finish_part(update, context)


# Наступне завдання
async def next_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_task(update, context)


# Фінальні результати
async def finish_part(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    selected_part = context.user_data['selected_part']

    context.user_data['total_score'] += context.user_data['part_score']

    if selected_part == "Reading":
        result_text = f"Частина Reading завершена✔️. Ваш результат: {context.user_data['part_score']} балів."
        keyboard = [[InlineKeyboardButton("Перейти до Use of English ➡️", callback_data='next_part')]]
    else:
        total_score = context.user_data['total_score']
        part_scores = context.user_data['part_score']
        reading_score = total_score - part_scores  # считаем

        rating = score_conversion.get(total_score, "не склав")
        rating_message = None

        if rating == "не склав":
            rating_message = rating_messages["не склав"]
        else:
            for range_key, message in rating_messages.items():
                if isinstance(range_key, tuple) and range_key[0] <= rating <= range_key[1]:
                    rating_message = message
                    break
                elif rating == range_key:
                    rating_message = message
                    break

        result_text = (f"Тест завершено. Ваш результат: Reading {reading_score}/22 Use of English {part_scores}/20.\n"
                       f"\n📍Загальний результат: {total_score} \n Ваша рейтингова оцінка: {rating}\n{rating_message}📍")

        keyboard = [[InlineKeyboardButton("Пройти новий тест", callback_data='restart')],
                    [InlineKeyboardButton("Корисні ресурси📖",
                                          url='https://testportal.gov.ua/yedynyj-vstupnyj-ispyt-2/')],
                    [InlineKeyboardButton("Знайти викладача👩🏻‍🏫",
                                          url='https://buki.com.ua/blogs/layfkhaky-z-yevi-yedynyj-vstupnyj-ispyt-z-anhliyskoyi-movy/')]
                    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(text=result_text, reply_markup=reply_markup)


# Обробка запуску наступної частини тесту
async def next_part(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    selected_year = context.user_data['selected_year']
    if exams_data:
        parts = next(part['parts'] for part in exams_data['exam_years'] if str(part['year']) == selected_year)
        part = next(part for part in parts if part['name'] == 'Use of English')
        tasks = part['tasks']
        context.user_data['selected_part'] = 'Use of English'
        context.user_data['tasks'] = tasks
        context.user_data['current_task_index'] = 0
        context.user_data['part_score'] = 0

        await send_task(update, context)


# Обробка кнопки "Назад" до вибору року
async def back_to_years(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await start(update, context)


# Обробка кнопки "Назад" до вибору частини
async def back_to_parts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    selected_year = context.user_data['selected_year']
    if exams_data:
        parts = next(part['parts'] for part in exams_data['exam_years'] if str(part['year']) == selected_year)
        keyboard = [
            [InlineKeyboardButton(part.get('name', 'Без назви'), callback_data=f"part_{part.get('name', 'unknown')}")]
            for part in parts]
        keyboard.append([InlineKeyboardButton("Назад◀️", callback_data='back_to_years')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"Виберіть розділ для {selected_year} року:", reply_markup=reply_markup)


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(year_choice, pattern='^\\d{4}$'))
    application.add_handler(CallbackQueryHandler(part_choice, pattern='^part_'))
    application.add_handler(CallbackQueryHandler(handle_answer, pattern='^answer_'))
    application.add_handler(CallbackQueryHandler(next_task, pattern='^next$'))
    application.add_handler(CallbackQueryHandler(finish_part, pattern='^finish$'))
    application.add_handler(CallbackQueryHandler(next_part, pattern='^next_part$'))
    application.add_handler(CallbackQueryHandler(restart, pattern='^restart$'))
    application.add_handler(CallbackQueryHandler(back_to_years, pattern='^back_to_years$'))
    application.add_handler(CallbackQueryHandler(back_to_parts, pattern='^back_to_parts$'))

    application.run_polling()


if __name__ == '__main__':
    main()
