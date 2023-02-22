import json
import telebot
from googletrans import Translator
from telebot import types
import csv
import speech_recognition as sr
from pydub import AudioSegment
from config import TOKEN

bot = telebot.TeleBot(token=TOKEN)

# 1. Написать в текстовый файл users.txt пользователей, которые запускают бота (никнейм, фамилия, имя, id)
@bot.message_handler(commands=['start'])  
def start(message):
    follow = types.KeyboardButton(text="follow")
    unfollow = types.KeyboardButton(text="unfollow")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(follow)
    markup.add(unfollow)

    user = message.from_user
    with open('users.txt', 'a') as f:
        f.write(f"{user.username}, {user.last_name}, {user.first_name}, {user.id}\n")

    bot.send_message(message.chat.id, 'Добро пожаловать!', reply_markup=markup)


@bot.message_handler(commands=['follow'])
def follow(message):
    bot.send_message(message.chat.id, "Вы подписались")


@bot.message_handler(commands=['unfollow'])
def unfollow(message):
    bot.send_message(message.chat.id, "Вы отписались")


# 3. Написать хендлер (функцию), которая отвечает на картинку картинкой
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    photo = message.photo[-1]  # берем последнюю (самую большую) фотографию из списка
    bot.send_photo(message.chat.id, photo.file_id)


# 4. Написать функцию, которая реагирует на определенную команду и отправляет всем пользователям
# с users.txt сообщение "Привет мир!"
@bot.message_handler(commands=['hello'])
def send_hello(message):
    with open('users.txt', 'r') as f:
        for line in f:
            user = line.strip().split(', ')
            bot.send_message(user[-1], 'Привет мир!')


# 2. Написать в csv файл текст, который переводит бот (исходный текст, переведенный текст, пользователь)
@bot.message_handler()
def translate_text(message):
    if message.chat.type == 'private':
        translator = Translator()
        text = message.text
        result = translator.translate(text, dest='ru')
        bot.reply_to(message, text=result.text)

        user = message.from_user
        with open('translations.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([text, result.text, f"{user.username}, {user.last_name}, {user.first_name}"])
    else:
        bot.reply_to(message, text=message.text)


# Аудио на текст
@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    # Получаем информацию о голосовом сообщении
    voice_info = message.voice
    # Скачиваем голосовое сообщение во временную директорию
    file_info = bot.get_file(voice_info.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open('voice.ogg', 'wb') as f:
        f.write(downloaded_file)
   


bot.infinity_polling()