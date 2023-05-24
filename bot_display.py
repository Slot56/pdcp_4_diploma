from method_main import bot
from keyboards import sender
from vk_api.longpoll import VkEventType

from cursor_db import creating_database


for event in bot.longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text.lower()
        user_id = str(event.user_id)
        msg = event.text.lower()
        sender(user_id, msg.lower())
        if request == 'начать поиск':
            creating_database()
            bot.write_msg(user_id, f'Привет, {bot.names_vk(user_id)}')
            bot.user_search_by_data(user_id)
            bot.write_msg(event.user_id,
                          'Нашёл для тебя, посмотри. Есть ещё, жми на кнопку "Вперёд"')
            bot.displaying_information_in_a_chat(user_id)
        elif request == 'вперёд':
            bot.displaying_information_in_a_chat(user_id)
        else:
            bot.write_msg(event.user_id, 'Я не понял что ты хочешь')
