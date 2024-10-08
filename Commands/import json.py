import asyncio
import json
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import BOT_TOKEN

TOKEN = BOT_TOKEN

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Шлях до файлу
file_path = "Updated_EVI.json"
if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        exams_data = json.load(f)
else:
    print(f"Файл {file_path} не знайдено")
    exams_data = None

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
    5: 100, 6: 108, 7: 116, 8: 124, 9: 130, 10: 134, 11: 137, 12: 140, 13: 143,
    14: 146, 15: 148, 16: 150, 17: 152, 18: 154, 19: 157, 20: 160, 21: 162,
    22: 164, 23: 167, 24: 170, 25: 174, 26: 177, 27: 182, 28: 188, 29: 194,
    30: 200
}

rating_messages = {
    "не склав": "Ooops, може спробуєш ще раз? Рекомендуємо повчитися ще 🙃",
    (100, 120): "Congratulations, поріг пройдено 🤗",
    (121, 160): "Well done, непоганий результат 😍",
    (161, 180): "AMAZING, чудовий результат 🤝",
    (181, 199): "OMG YOUR RESULT IS REALLY COOL 😯",
    200: "This is the highest score, we are so proud of you! 🥳"
}


# Команда /обробник запуску
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("2022/2023", callback_data='2022')],
        [InlineKeyboardButton("2021", callback_data='2021')],
        [InlineKeyboardButton("2020", callback_data='2020')],
        [InlineKeyboardButton("2019", callback_data='2019')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text('Який рік хочеш пропрацювати?:', reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text('Який рік хочеш пропрацювати?:', reply_markup=reply_markup)


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
    keyboard.append([InlineKeyboardButton("Словнич🆗", url='https://www.vocabulary.com/dictionary/')])
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


# Обробка завершення тесту
async def finish_test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    part_score = context.user_data.get('part_score', 0)
    context.user_data['total_score'] += part_score
    context.user_data['current_task_index'] += 1

    if context.user_data['current_task_index'] < len(context.user_data['tasks']):
        await send_task(update, context)
    else:
        await show_results(update, context)


# Відображення результатів
async def show_results(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    total_score = context.user_data['total_score']
    selected_year = context.user_data['selected_year']
    score_conversion = score_conversion_2022 if selected_year == '2022' else score_conversion_2019_2021

    for key in sorted(score_conversion.keys(), reverse=True):
        if total_score >= key:
            rating = score_conversion[key]
            break

    rating_message = rating_messages.get(rating, "Оцінка не визначена")

    result_text = f"Тест завершено. Ваш результат за {selected_year} рік:\n"
    for part_name, part_score in context.user_data.items():
        if part_name.endswith('_score'):
            result_text += f"{part_name.capitalize()}: {part_score}\n"
    result_text += f"\n📍Загальний результат: {total_score}\nВаша рейтингова оцінка: {rating}\n{rating_message}"

    keyboard = [
        [InlineKeyboardButton("Пройти новий тест", callback_data='restart')],
        [InlineKeyboardButton("Корисні ресурси📖", url='https://example.com/resources')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(text=result_text, reply_markup=reply_markup)


# Налаштування бота та обробники
async def main() -> None:
    app = Application(TOKEN)
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(year_choice, pattern=r'^\d{4}$'))
    app.add_handler(CallbackQueryHandler(part_choice, pattern=r'^part_.+'))
    app.add_handler(CallbackQueryHandler(handle_answer, pattern=r'^answer_.+'))
    app.add_handler(CallbackQueryHandler(finish_test, pattern=r'^finish$'))
    app.add_handler(CallbackQueryHandler(restart, pattern=r'^restart$'))
    await app.run_polling()


if __name__ == '__main__':
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
