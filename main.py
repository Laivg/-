import vk_api
import random
import schedule
import time
import requests
import datetime
import threading
import os
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

url= "https://time100.ru/Moscow"
script_directory = os.path.dirname(os.path.abspath(__file__))
folders_path = os.path.join(script_directory, 'photo_packs')
conversations_file = "conversations.txt"

# Инициализация VK API
vk_session = vk_api.VkApi(token='токен'
vk = vk_session.get_api()
group_id = 'айпи'
longpoll = VkBotLongPoll(vk_session, group_id)

selected_folder = None

def get_random_id():
    return random.randint(0, 100000000)

#читаем файл с адишником бесед
def read_conversations_from_file():
    if os.path.exists(conversations_file):
        with open(conversations_file, "r") as f:
            return [
                int(line.strip()) for line in f.readlines()
                if line.strip() and not line.strip().startswith(('#', '\\', '//'))
            ]
    return []
#вписывается новый айдишник
def write_conversation_to_file(conversation_id):
    conversations = read_conversations_from_file()
    if conversation_id not in conversations:
        with open(conversations_file, "a") as f:
            f.write(f"{conversation_id}\n")

# Функция для получения времени с сайта
def get_time():
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["currentTime"]
    else:
        return "Не удалось получить время с сайта"

# Функция для получения случайной папки с фотографиями
def get_selected_folder(folders_path):
    folders = os.listdir(folders_path)
    return os.path.join(folders_path, random.choice(folders))

# Флаг, отслеживающий, было ли отправлено ежедневное сообщение
daily_message_sent = False

# Функция для отправки ежедневного сообщения
def send_daily_message():
    global daily_message_sent
    global selected_folder

    if daily_message_sent:
        return

    print("Trying to send daily message to all conversations...")
    current_day = datetime.datetime.now().strftime("%A")
    current_time = get_time()

    # Если сегодня понедельник или папка еще не выбрана, выбираем случайную папку
    if current_day == "Monday" or selected_folder is None:
        selected_folder = get_selected_folder(folders_path)

    print(f"Selected folder: {selected_folder}")

    # Проверяем, что папка существует
    if not os.path.exists(selected_folder):
        print(f"Папка '{selected_folder}' не найдена.")
        return

    photo_filename = f"{current_day}.jpg"
    photo_path = os.path.join(selected_folder, photo_filename)

    if not os.path.exists(photo_path):
        print(f"Фото '{photo_path}' не найдено.")
        return

    messages = {
        "Monday": ">ПИЗДЕЦ, понедельник, держитесь, мужики! ",
        "Tuesday": ">СУКА, сегодня вторник! ",
        "Wednesday": ">живем-живем, сегодня среда,ква! ",
        "Thursday": ">почти, мужики, уже четверг! ",
        "Friday": ">Ура, сегодня пятница, мужики! ",
        "Saturday": ">Ура, сегодня суббота,раслабон! ",
        "Sunday": ">Ура, сегодня воскресенье! "
    }
    message = messages.get(current_day, ">Ура, сегодня день!")

    bot_conversations = read_conversations_from_file()
    for conversation_id in bot_conversations:
        try:
            upload = vk_api.VkUpload(vk)
            photo = upload.photo_messages(photo_path)
            attachment = f"photo{photo[0]['owner_id']}_{photo[0]['id']}"
            vk.messages.send(peer_id=conversation_id, message=message, attachment=attachment, random_id=get_random_id())
            print(f"Message sent successfully to conversation {conversation_id}! Response: {get_random_id()}")
            time.sleep(0.1)  # Задержка 100 мс между отправками сообщений
        except Exception as e:
            print(f"Error sending message to conversation {conversation_id}: {e}")

    daily_message_sent = True

# активные сообщения
def handle_new_messages():
    global daily_message_sent
    while True:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                message = event.object.message
                message_text = message['text'].lower().strip()
                peer_id = message['peer_id']

                if message_text == 'начать' or message_text == 'помощь':
                    vk.messages.send(peer_id=peer_id, random_id=get_random_id(), message="Привет, я бот! РАЗРАБ ТУПОЙ КЛОВН,НЕ СМОГ В МНОГОПОТОК,И ТУПИЛ 3 ДНЯ,ЧТОБЫ Я МОГ И СООБЩЕНИЯ В ОТВЕТ ОТПРАВЛЯТЬ И ЗАПЛАНИРОВАНА!")
                    daily_message_sent = False
                elif message_text == r'\гойда':
                    vk.messages.send(peer_id=peer_id, message="ГОЙДА!", attachment="photo-220974325_457239019", random_id=get_random_id())
                elif message_text == r'\z':
                    vk.messages.send(peer_id=peer_id, message="z!", attachment="doc-195035228_663836974", random_id=get_random_id())

                # Запись ID беседы в файл
                write_conversation_to_file(peer_id)

# Запуск бота
schedule.every().day.at("00:01").do(send_daily_message)
message_handler_thread = threading.Thread(target=handle_new_messages)
message_handler_thread.start()

while True:
    schedule.run_pending()
    time.sleep(1)