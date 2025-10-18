import psycopg
from DATABASE.config import *
from StaticStorage import Storage


class DatabaseConnection:
    def __init__(self):
        """ Конструктор класса """
        self.connection = self.connect_to_database()

    def connect_to_database(self):
        """ Подключение к базе данных на сервере """
        try:
            # Подключение
            connection = psycopg.connect(
                user=user_name,
                password=user_password,
                host=host_address,
                dbname=database_name
            )
            print(f"Подключено! {connection}")
            return connection
        except Exception as e:
            # Ошибка при подключении
            print(e)
            return None

    def check_user_login_password(self,
                                  user_login: str,
                                  user_password: str) -> bool:
        """
        Метод проверки наличия пользователя в БД
        :param user_login: Логин введеный пользователем
        :param user_password: Пароль ввденый пользователем
        :return: True - пользователь есть | False - пользователя нет
        """
        query = f"""
        select user_login, user_role
        from Client
        where user_login = '{user_login}'
            and user_password = '{user_password}'
        """
        cursor = self.connection.cursor()
        cursor.execute(query)
        existing_login = ""
        existing_user_role = ""
        for answer in cursor.fetchall():
            existing_login = answer[0]
            existing_user_role = answer[1]
        if existing_login == "":
            # Не найдено совпадений Логина И Пароля - Аккаунт не существует
            return False

        # Совпадения найдены
        # Добавление активного логина в статический класс
        Storage().set_user_login(existing_login)
        Storage().set_user_role(existing_user_role)
        return True

    def take_user_data(self) -> dict:
        """
        Метод получения информации по пользовтелю
        :return: Словарь с данными
        """
        query = f"""
        select *
        from Client
        where user_login = '{Storage().get_user_login()}'
        """
        cursor = self.connection.cursor()
        cursor.execute(query)
        result = dict()
        for answer in cursor.fetchall():
            result["user_role"] = answer[0]
            result["user_name"] = answer[1]
            result["user_login"] = answer[2]
            result["user_password"] = answer[3]
        return result

    def get_all_items(self):
        """
        Метод получения списка всех товаров
        :return: list(dict())
        """

        query = """
        select *
        from Items
        """
        result = []
        cursor = self.connection.cursor()
        cursor.execute(query)
        for answer in cursor.fetchall():
            print(answer)
            picture = answer[10]
            if picture == "":
                picture = "picture.png"
            result.append(
                # Добавление словаря для каждого товара в список
                {
                    "article": answer[0],
                    "name": answer[1],
                    "edinica": answer[2],
                    "cost": answer[3],
                    "deliveryman": answer[4],
                    "creator": answer[5],
                    "category": answer[6],
                    "sale": answer[7],
                    "count": answer[8],
                    "information": answer[9],
                    "picture": picture,
                }
            )
        print(result)
        return result
