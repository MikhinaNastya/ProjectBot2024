import telebot
from telebot.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
import time
from messages import start_message, help_message
from quiz_data import question_list

TOKEN = '5105079731:AAH8upaZMOklbcOctiFtpOiGAulr5HSET78'
bot = telebot.TeleBot(TOKEN)

user_results = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, start_message)

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, help_message)

@bot.message_handler(commands=['start_quiz'])
def handle_start_quiz(message):
    user_id = message.from_user.id
    user_results[user_id] = {"correct_answers": 0, "start_time": time.time()}
    send_question(message.chat.id, user_id)

def send_question(chat_id, user_id):
    current_question = user_results[user_id].get("current_question", 0)
    question_data = question_list[current_question]
    markup = InlineKeyboardMarkup()
    for option in question_data["options"]:
        button = InlineKeyboardButton(text=option, callback_data=option)
        markup.add(button)
    bot.send_message(chat_id, question_data["question"], reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user_id = call.from_user.id
    current_question = user_results[user_id].get("current_question", 0)
    question_data = question_list[current_question]

    if call.data == question_data["correct_option"]:
        user_results[user_id]["correct_answers"] += 1

    user_results[user_id]["current_question"] = current_question + 1

    if current_question + 1 < len(question_list):
        send_question(call.message.chat.id, user_id)
    else:
        end_quiz(call.message.chat.id, user_id)

def end_quiz(chat_id, user_id):
    end_time = time.time()
    start_time = user_results[user_id]["start_time"]
    elapsed_time = round(end_time - start_time) // 60

    correct_answers = user_results[user_id]["correct_answers"]
    bot.send_message(chat_id, f"Викторина завершена! Правильных ответов: {correct_answers}, Затраченное время: {elapsed_time} минут.")
    record_result(user_id, correct_answers, elapsed_time)

def record_result(user_id, correct_answers, elapsed_time):
    pass

def get_top_results(n=5):
    pass

@bot.message_handler(commands=['record_table'])
def handle_record_table(message):
    top_results = get_top_results()
    if top_results:
        result_text = "Лучшие результаты:\n"
        for i, (user_id, correct_answers, elapsed_time) in enumerate(top_results, start=1):
            result_text += f"{i}. Пользователь {user_id}: {correct_answers} правильных ответов за {elapsed_time} минут\n"
        bot.send_message(message.chat.id, result_text)
    else:
        bot.send_message(message.chat.id, "Нет данных о результатах.")


if __name__ == "__main__":
    bot.polling(none_stop=True)
