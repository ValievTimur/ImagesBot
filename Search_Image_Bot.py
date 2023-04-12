import telebot
from telebot.types  import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import requests, json

users = []
request = {}
mes = {'helping': '''Отправь мне запрос, а я найду по нему картинку и отправлю тебе. \n\nНекоторые запросы на русском языке могут плохо обрабатываться, поэтому лучше использовать английский. \n\nДля создания запроса просто отправь текстовое сообщение в чат.''', 
'start': 'Отправь мне запрос, а я найду по нему картинку и отправлю тебе.', 
'about': '''Меня создал Тимур --> @T_i_m_u_p_k_a \n\nВведенный текстовый запрос отправляется через API запрос на хостинг картинок Unsplash.'''}

# создаем обьект бота и кнопки
bot = telebot.TeleBot('6223766493:AAFQZJrUOCE7e9C7u0BNLBJOeka4Gb3O0M4')
keys = ReplyKeyboardMarkup(resize_keyboard=True)
keys.add(KeyboardButton('О проекте'))
keys.add(KeyboardButton('Помощь'))
inline_keys = InlineKeyboardMarkup()
inline_keys.add(InlineKeyboardButton('Мне не понравилось!', callback_data='button1'))

# функции
def get_image(query):
    params = {
        'query': query,
        'client_id': 'ea2LOFJk7qNeowtjX9--FvZmr6N32Nsp6S8Hyyn8wu0'
    }
    try:
        response = requests.get('https://api.unsplash.com/photos/random', params=params)
        response_json = response.json()
        photo_url = response_json['urls']['regular']
        photo = requests.get(photo_url)
        return photo.content
    except:
        return False
def register(data):
    if data.from_user.id not in users:
        users.append(data.from_user.id)
        print(f'Person: {data.from_user.first_name} --> @{data.from_user.username}')
def get_des(photo):
    headers = {"Authorization": f"Bearer {'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'}"}
    API_URL = "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"
    response = requests.request("POST", API_URL, headers=headers, data=photo)
    data = json.loads(response.content.decode("utf-8"))
    values = [f"{i['label']}" for i in data]
    items = ''
    for i in values:
        items += f'{i}, '
    items = items.strip(', ')
    return f'Мне кажется здесь изображено: {items }'
# стартовое сообщение и помощь
@bot.message_handler(regexp=r'/*start')
def send_welcome(message):
    register(message)
    bot.send_message(message.chat.id, mes['start'], reply_markup=keys)
@bot.message_handler(regexp=r'/*help|Помощь')
def send_help(message):
    register(message)
    bot.send_message(message.chat.id, mes['helping'], reply_markup=keys) 
# об авторе
@bot.message_handler(regexp=r'/*about|О проекте')
def send_about(message):
    register(message)
    bot.send_message(message.chat.id, mes['about'], reply_markup=keys)

# обработчик запроса на поиск
@bot.message_handler(content_types='text')
def send_image(message):
    register(message)
    global request
    request[message.chat.id] = message.text
    result = get_image(message.text)
    if result is False:
        bot.send_message(message.chat.id, f'Я не могу найти изображение по запросу <{message.text}>')    
    else:
        bot.send_photo(message.chat.id, result, reply_markup=inline_keys)
# обработчик запроса на повторный поиск
@bot.callback_query_handler(func = lambda call: True)
def resend(call):
    register(call)
    if call.from_user.id in request.keys():
    	bot.send_photo(call.from_user.id, get_image(request[call.from_user.id]), reply_markup=inline_keys)
    else:
    	bot.send_message(call.from_user.id, 'Ваш запрос оказался пустым!')
# обработчик запроса на описание изображения
@bot.message_handler(content_types='photo')
def send_description(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    # скачиваем файл
    photo = bot.download_file(file_info.file_path)
    bot.send_message(message.chat.id, get_des(photo))
    register(message)
bot.polling()