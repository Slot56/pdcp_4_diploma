import psycopg2

from config import host, user, password, db_name


connection = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    database=db_name
)

connection.autocommit = True


def create_table_users():
    """create_table_users 
    создание таблицы users
    """

    with connection.cursor() as cursor:
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS users (
                           id SERIAL,
                           first_name varchar(50) NOT NULL,
                           last_name varchar(25) NOT NULL,
                           vk_id varchar(20) NOT NULL PRIMARY KEY);""")
    print("[INFO] таблица USERS успешно создана !")


def insert_data_users(first_name, last_name, vk_id):
    """insert_data_users
    вставка данных в таблицу users

    :param first_name:Имя пользователя в базе данных.
    :type first_name: string
    :param last_name: Фамилия пользователя в базе данных
    :type last_name: string
    :param vk_id: идентификатор текущего пользователя.
    :type vk_id: string
    """
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT first_name, last_name, vk_id, ID FROM users WHERE vk_id=%s;
            """,(vk_id,))
        user_data_client = cursor.fetchone()
        if user_data_client:
            print(f'{user_data_client} [info] такие пользователи есть уже в базе данных !')
            return f'{user_data_client} [info] такие пользователи есть уже в базе данных !'
        if not user_data_client:
            cursor.execute("""
                           INSERT INTO users (first_name, last_name, vk_id)
                           VALUES (%s, %s, %s);""",(first_name, last_name, vk_id)
                           )
            connection.commit()
            return '[info] пользователи успешно добавлены !'

def select_db_step():
    """select_db_step()
    Функция выбирает пользователя из базы данных,
    (tuple:) выбирается три значения: Имя, Фамилия, и уникальный id (vk.com)

    :return:tuple на выходе ожидается:
    example : ('Татьяна', 'Будникова', '197512831')
    :rtype: 
    После того как данные упорядочены каким-либо образом, можно применять  RANDOM(). 
    """
    with connection.cursor() as cursor:
        cursor.execute("""SELECT first_name, last_name, vk_id
                       FROM users ORDER BY RANDOM() LIMIT 1;""")
        return cursor.fetchone()


def creating_database():
    """creating_database 
    Метод создаёт базу данных
    """
    create_table_users()


# print( 'Hello bot_users:',connection)
# print(create_table_users())
# print(insert_data_users('Ольга', 'Баранова', '164567004'))
#   print(select_db_step())
