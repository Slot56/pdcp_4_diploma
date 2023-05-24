import datetime
import time
from random import randrange

import vk_api
import requests

from config import user_token, comm_token

from vk_api.longpoll import VkLongPoll, VkEventType
from cursor_db import insert_data_users, select_db_step


class VKBot:
    """class VkBot Основная идея алгоритма в том,
    что основной тред будет занят слушанием longpoll,
    который при появлении нового сообщения будет создавать новый тред. 
    
    class VkBot:
    Methods:  13 для написания методов были использованы две основных библиотеки:
    1. requests
    2. vk-api
    1. names_vk():
    Опредиление имяни пользователя.
    2. get_vk_sex():
    Опредиление пола пользователя.
    3. get_age_bottom_line():
    Опредиляет нижнюю границу пользователя.
    4. get_age_upper_bound():
    Определяет верхнюю границу пользователя.
    5. user_s_city():
    Опредиляет город пользователя.
    6. user_city_search()
    Получает информацию о городе пользователя.
    7. user_search_by_data():
    Ищет пользователя  по полученным данным.
    8. get_photos_id():
    ПОЛУЧЕНИЕ ID ФОТОГРАФИЙ .
    9. get_photo_ids():
    Выводит 3 фото из общего списка фотографий get_photos_id()
    10. send_photo_ids():
    Отправляет фотографии в чат.
    11. displaying_information_in_a_chat():
    Выводит информацию в чат группы.
    12. user_information_in_chat():
    Выводит информацию о пользователе в чат группы. (Имя, Фамилия, сылка на профиль пользователя)
    13. gets_user_id():
    Выводит ID пользователя.
    """
    def __init__(self):
        print('Всё готово к работе, подключаемся')
        self.vk_group = vk_api.VkApi(token=comm_token)  # Авторизация в сообществе
        self.longpoll = VkLongPoll(self.vk_group)  # Работа с (message)


    def write_msg(self, user_id, message):
        """write_msg
        МЕТОД ДЛЯ ОТПРАВКИ СООБЩЕНИЙ
        https://dev.vk.com/method/messages.send

        Args:
            user_id ([int]): integer Обязательный параметр. Идентификатор пользователя,
            которому отправляется сообщение.
            message ([str]): string Необязательный параметр. Текст личного сообщения. Максимальное
            количество символов — 4096. 
        """
        self.vk_group.method('messages.send', {
            'user_id': user_id,
            'message': message,
            'random_id': randrange(10**6, 10**8)})

    def names_vk(self, user_id):
        """names_vk
        получение имени пользователя, который написал боту
        https://vk.com/dev.php?method=users.get

        Args:
            user_id ([string]): [перечисленные через запятую идентификаторы пользователей или
            их короткие имена
            (screen_name).
            По умолчанию — идентификатор текущего пользователя.
список слов, разделенных через запятую]

        Returns:
            [str]: [На выходе ожидается имя пользователя vk.com]
        """
        url = 'https://api.vk.com/method/users.get'
        params = {
            'access_token': user_token,
            'user_ids': user_id,
            'v': '5.131'
            }
        repl_params = requests.get(url, timeout=(3.05, 27), params=params)
        response = repl_params.json()
        try:
            information_dict = response['response']
            for i in information_dict:
                first_name = i['first_name']
            return first_name
        except KeyError:
            self.write_msg(user_id, 'Ошибка получения токена, введите токен в переменную')

    def get_vk_sex(self, user_id):
        """get_vk_sex
        получение пола пользователя,
        меняет на противоположный.
        https://vk.com/dev.php?method=users.get

        Args:
            user_id ([string]): [перечисленные через запятую идентификаторы
            пользователей или их короткие
            имена (screen_name).
            По умолчанию — идентификатор текущего пользователя.]

        Returns:
            [integer]: [После успешного выполнения возвращает массив объектов пользователей. Пол.
            Возможные значения
            1 — женский; 2 — мужской; 0 — пол не указан.]
        """
        url = 'https://api.vk.com/method/users.get'
        params = {
            'access_token': user_token,
            'user_ids': user_id,
            'fields': 'sex',
            'v': '5.131'
            }
        repl = requests.get(url, timeout=(3.05, 27), params=params)
        response = repl.json()
        try:
            information_list = response['response']
            for i in information_list:
                if i['sex'] == 2:
                    find_sex = 1
                    return find_sex
                elif i['sex'] == 1:
                    find_sex = 2
                    return find_sex
        except KeyError:
            self.write_msg(user_id, 'Ошибка получения токена, введите токен в переменную')

    def get_age_bottom_line(self, user_id):
        """get_age_bottom_line 
        получение возраста пользователя или нижней границы для поиска
        https://dev.vk.com/method/users.get

        Args:
            user_id ([integer]): [Идентификатор пользователя.]

        Returns:
            [integer]: [Возвращает возраст пользователя]
        """
        url = 'https://api.vk.com/method/users.get'
        params = {
            'access_token': user_token,
            'user_ids': user_id,
            'fields': 'bdate',
            'v': '5.131'
            }
        repl = requests.get(url, timeout=(3.05, 27), params=params)
        response = repl.json()
        information_list = response['response']
        for datas in information_list:
            date = datas['bdate']
            date_list = date.split('.')
            if len(date_list) == 3:
                year = int(date_list[2])
                year_now = int(datetime.date.today().year)
            elif len(date_list) == 2:
                date_list = list(date_list)
                date_list.append('1985')
                year = int(date_list[2])
                year_now = int(datetime.date.today().year)
            return year_now - year

        try:
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    self.write_msg(user_id, f'{self.get_age_bottom_line(user_id)}')
        except KeyError:
            self.write_msg(user_id, f'Ошибка получения возраста пользователя ! {KeyError}')

    def get_age_upper_bound(self, user_id):
        """get_age_upper_bound
        получение возраста пользователя или верхней границы для поиска
        https://dev.vk.com/method/users.get


        Args:
            user_id ([integer]): [Идентификатор пользователя.]

        Returns:
            [integer]: [Возвращает возраст пользователя]
        """
        url = 'https://api.vk.com/method/users.get'
        params = {
            'access_token': user_token,
            'user_ids': user_id,
            'fields': 'bdate',
            'v': '5.131'
            }
        repl = requests.get(url, timeout=(3.05, 27), params=params)
        response = repl.json()
        try:
            information_list = response['response']
            for i in information_list:
                date = i['bdate']
            date_list = date.split('.')
            if len(date_list) == 3:
                year = int(date_list[2])
                year_now = int(datetime.date.today().year)
                return year_now - year
            elif len(date_list) == 2 or date not in information_list:
                self.write_msg(user_id, 'Введите верхний порог возраста (max - 65): ')
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        age = event.text
                        return age
        except KeyError:
            self.write_msg(user_id, 'Ошибка получения токена, введите токен в переменную')

    def user_s_city(self, user_id, city_name):
        """user_s_city
        получение id города пользователя по названию
        https://vk.com/dev/database

        Args:
            user_id ([integer]): [Идентификатор пользователя.]
            city_name ([str]): [строка поискового запроса. Например, Санкт.
Максимальная длина строки — 15 ]

        Returns:
            [int]: [Возвращает город]
        """
        url = 'https://api.vk.com/method/database.getCities'
        params = {
            'access_token': user_token,
            'country_id': 1,
            'q': f'{city_name}',
            'need_all': 0,
            'count': 1000,
            'v': '5.131'
            }
        repl = requests.get(url, timeout=(3.05, 27), params=params)
        response = repl.json()
        try:
            information_list = response['response']
            list_cities = information_list['items']
            for i in list_cities:
                found_city_name = i['title']
                if found_city_name == city_name:
                    found_city_id = i['id']
                    return int(found_city_id)
        except KeyError:
            self.write_msg(user_id, 'Ошибка получения токена')

    def user_city_search(self, user_id):
        """user_city_search
        получение информации о городе пользователя
        https://dev.vk.com/method/users.get

        Args:
            user_id ([integer]): [Идентификатор пользователя.]

        Returns:
            [str]: [Номер города]
        """
        url = 'https://api.vk.com/method/users.get'
        params = {
            'access_token': user_token,
            'fields': 'city',
            'user_ids': user_id,
            'v': '5.131'
            }
        repl = requests.get(url, timeout=(3.05, 27), params=params)
        response = repl.json()
        try:
            information_dict = response['response']
            for i in information_dict:
                if 'city' in i:
                    city = i['city']
                    id_name_city = str(city['id'])
                    return id_name_city
                elif 'city' not in i:
                    self.write_msg(user_id, 'Введите название вашего города: ')
                    for event in self.longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                            city_name = event.text
                            id_city = self.user_s_city(user_id, city_name)
                            if id_city != '' or id_city is not None:
                                return str(id_city)
                            else:
                                break
        except KeyError:
            self.write_msg(user_id, 'Ошибка получения токена')

    def user_search_by_data(self, user_id):
        """user_search_by_data
        поиск человека по полученным данным
        https://vk.com/dev/users.search
        Метод добавляет найденных пользователей в базу данных
        error_code:
        Обработка кода ошибки 6 в Вконтакте - Слишком много запросов в секунду
        При работе с API в Контакте можно встретить следующий ответ:
        {'error': 'Too many requests per second', 'error_code': 6}

        Args:
            user_id ([integer]): [Идентификатор пользователя.]

        Returns:
            [str, int]: [Возвращает список пользователей в соответствии
            с заданным критерием поиска.]
        """
        url = 'https://api.vk.com/method/users.search'
        params = {
            'access_token': user_token,
            'v': '5.131',
            'sex': self.get_vk_sex(user_id),
            'age_from': self.get_age_bottom_line(user_id),
            'age_to': self.get_age_upper_bound(user_id),
            'city': self.user_city_search(user_id),
            'fields': 'id, first_name, last_name',
            'status': '1',
            'count': 50
            }
        resp = requests.get(url, timeout=(3.05, 27), params=params)
        max_attempts = 20
        attempt = 0
        while attempt < max_attempts:
            data = resp.json()
            if 'error' in data and data['error'].get('error_code') == 6:
                time.sleep(2)
                attempt += 1
                continue
            break
        # return data


        try:
            resp_person_dict = data['response']
            resp_person_list = resp_person_dict['items']
            for person_dict in resp_person_list:
                if person_dict['is_closed'] is False:
                    first_name = person_dict['first_name']
                    last_name = person_dict['last_name']
                    vk_id = str(person_dict['id'])
                    insert_data_users   (first_name, last_name, vk_id)
                else:
                    continue
            return 'Поиск завершён удачно !'
        except KeyError:
            self.write_msg(user_id, 'Ошибка получения токена')

    def get_photos_id(self, user_id):
        """get_photos_id
        получение id фотографий с ранжированием в обратном порядке
        https://vk.com/dev/photos.get

        Args:
            user_id ([integer]): [Идентификатор пользователя.]

        Returns:
            [list + tuple]: [Возвращает список фотографий в альбоме.]
        """
        url = 'https://api.vk.com/method/photos.get'
        params = {
            'access_token': user_token,
            'v': '5.131',
            'album_id': 'profile',
            'owner_id': user_id,
            'extended': 1,
            'count': 25
            }
        resp = requests.get(url, timeout=(3.05, 27), params=params)
        dict_photos = dict()
        resp_json = resp.json()
        # return resp_json
        try:
            resp_person_dict = resp_json['response']
            resp_person_list = resp_person_dict['items']
            for i in resp_person_list:
                photo_id = str(i['id'])
                i_likes = i['likes']
                if i_likes['count']:
                    likes = i_likes['count']
                    dict_photos[likes] = photo_id
            list_of_ids = sorted(dict_photos.items(), reverse=True)
            return list_of_ids
        except KeyError:
            self.write_msg(user_id, 'Ошибка получения токена')

    def get_photo_ids(self, user_id):
        """get_photo_ids
        ПОЛУЧЕНИЕ ID ФОТОГРАФИИ 3 фото

        Args:
            user_id ([integer]): [Идентификатор пользователя.]

        Returns:
            [list + tuple]: [Возвращает список фотографий ]
        """
        list_photo = self.get_photos_id(user_id)
        result = []
        for i, ids in enumerate(list_photo):
            result.append(ids)
            if i == 2:
                break
        results = [ x[1] for x in result[0:]]
        # return results
        if len(results) == 3:
            return f'фото 1: id{result[0][1]}\nфото 2 : id{result[1][1]}\nфото 3 : id{result[2][1]}'
        if len(results) == 2:
            return f'фото 1 : id{result[0][1]}\n фото 2 : id{result[1][1]}'
        if len(results) == 1:
            return f'фото 1 : id{result[0][1]} здесь только одно фото, перейди в профиль по ссылке выше !'


    def send_photo_ids(self, user_id, message):
        """send_photo_ids
        отправка фотографии
        https://dev.vk.com/method/messages.send

        Args:
            user_id ([integer]): [Идентификатор пользователя.]
            message ([string]): [Необязательный параметр. Текст личного сообщения.
            Максимальное количество символов — 4096.]
        """
        self.vk_group.method('messages.send', {
            'user_id': user_id,
            'access_token': user_token,
            'message': message,
                'attachment': f'{self.gets_user_id()}_{self.get_photo_ids(self.gets_user_id())}',
            'random_id': randrange(10**6, 10**8)})

    def displaying_information_in_a_chat(self, user_id):
        """displaying_information_in_a_chat Метод  состоит из нескольких методов,
        выводит основную информацию о пользователе в чат "ВКонтакте."

        Args:
            user_id ([integer]): [Идентификатор пользователя.]
        """
        self.write_msg(user_id, self.user_information_in_chat())
        self.send_photo_ids(user_id,
                            f'Фото пользователя: {self.get_photo_ids(self.gets_user_id())}',
                            )
        self.write_msg(user_id,
                           'Есть ещё, поехали дальше? Нажимай на кнопку (вперёд) !')
        if self.get_photo_ids(self.gets_user_id()) is None:
            self.write_msg(user_id,
                           'Извини, но фото больше нет, перейди в профиль по сылке !')

    def user_information_in_chat(self):
        """user_information_in_chat
        вывод информации о найденном пользователи
        Метод берёт информацию из базы данных с помощью функции: select_db_step()

        Args:

        Returns:
            [list]: [На выходе получается Имя, Фамилия, сылка на страницу пользователя]
        """
        tuple_person = select_db_step()
        list_person = []
        for i in tuple_person:
            list_person.append(i)
        return f'{list_person[0]} {list_person[1]}, ссылка - http://vk.com/id{list_person[2]}'

    def gets_user_id(self):
        """gets_user_id
        вывод id найденного пользователя

        Args:

        Returns:
            [str]: [Идентификатор пользователя.]]
        """
        tuple_person = select_db_step()
        list_person = []
        for i in tuple_person:
            list_person.append(i)
        return str(list_person[2])

bot = VKBot()
# if __name__ == '__main__':
    # bot = VKBot()


# print(bot.names_vk(555))

# print(bot.get_vk_sex(555))

# print(bot.get_age_bottom_line(222))

# print(bot.get_age_upper_bound(555))

# print(bot.user_s_city(555, 'Москва'))

# print(bot.user_city_search(555))

# print(bot.user_search_by_data(555))

# print(bot.get_photos_id(222))

# print(bot.get_photo_ids(217308514))
# print(bot.get_photo_ids(222))

# print(bot.displaying_information_in_a_chat(16854772))

# print(bot.user_information_in_chat())

# print(bot.gets_user_id())
# (22, 'Ольга', 'Аратова', '217308514')
