import json

from random import randint
from method_main import bot


def get_button(text, color):
    """get_button

    Args:
        text ([type]): Текст опредиления кнопки в чате
        color ([type]): Цвет кнопки в чате

    Returns:
        [type]: На выходе получается две кнопки (начать поиск), (Вперёд)
        
    """
    return {
        "action": {
            "type": "text",
            "payload": "{\"button\": \"" + "1" + "\"}",
            "label": f"{text}"
        },
        "color": f"{color}"
    }


keyboard = {
    "one_time": False,
    "buttons": [
        [get_button('Начать поиск', 'primary')],
        [get_button('Вперёд', 'secondary')]
    ]
}


def sender(user_id, text):
    """sender Метод отправляет сообщения в чат "В Контакте"
    'keyboard': Происходит передача клавиатуры с преобразованием в JSON() files
    Args:
        user_id ([type]): Пользователь "В Контакте"
        text ([type]): Текст сообщения
    """
    bot.vk_group.method('messages.send', {
        'user_id': user_id,
        'message': text,
        'random_id': randint(10**6, 10**8),
        'keyboard': keyboard
        })


keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')

keyboard = str(keyboard.decode('utf-8'))
