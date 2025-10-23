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

        if result == dict():
            # Если ответ из БД - пустой, значит входил гость
            print("NO one")
            result["user_role"] = "Гость"
            result["user_name"] = "Аккаунт Гостя"
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
            picture = answer[11]
            if picture == "":
                picture = "picture.png"
            result.append(
                # Добавление словаря для каждого товара в список
                {
                    "id": answer[0],
                    "article": answer[1],
                    "name": answer[2],
                    "edinica": answer[3],
                    "cost": answer[4],
                    "deliveryman": answer[5],
                    "creator": answer[6],
                    "category": answer[7],
                    "sale": answer[8],
                    "count": answer[9],
                    "information": answer[10],
                    "picture": picture,
                }
            )
        return result

    def search_and_filter_items(self,
                                search_text: str = "",
                                company_filter: str = "",
                                sort_by_count: bool = False):
        query = """
            SELECT 
                item_id, item_article, item_name, item_edinica, item_cost,
                item_deliveryman, item_creator, item_category,
                item_sale, item_count, item_information, item_picture
            FROM Items
            WHERE 1=1
        """
        params = []

        # Поиск по тексту (регистронезависимо в PostgreSQL — ILIKE)
        if search_text:
            like_clause = " OR ".join([
                "item_article ILIKE %s",
                "item_name ILIKE %s",
                "item_edinica ILIKE %s",
                "item_deliveryman ILIKE %s",
                "item_creator ILIKE %s",
                "item_category ILIKE %s",
                "item_information ILIKE %s",
                "item_picture ILIKE %s"
            ])
            query += f" AND ({like_clause})"
            params.extend([f"%{search_text}%"] * 8)

        # Фильтр по поставщику
        if company_filter and company_filter != "Все поставщики":
            query += " AND item_deliveryman = %s"
            params.append(company_filter)

        # Сортировка
        if sort_by_count:
            query += " ORDER BY item_count DESC"  # от большего к меньшему
        else:
            query += " ORDER BY item_name"  # по умолчанию — по названию

        cursor = self.connection.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

        result = []
        for answer in rows:
            picture = answer[11] or "picture.png"
            result.append({
                "id": answer[0],
                "article": answer[1],
                "name": answer[2],
                "edinica": answer[3],
                "cost": answer[4],
                "deliveryman": answer[5],
                "creator": answer[6],
                "category": answer[7],
                "sale": answer[8],
                "count": answer[9],
                "information": answer[10],
                "picture": picture,
            })
        return result

    def take_all_deliveryman(self):
        """
        Метод получения всех поставщиков
        :return: Список поставщиков
        """
        cursor = self.connection.cursor()
        cursor.execute("""
        SELECT DISTINCT item_deliveryman
        FROM Items
        ORDER BY item_deliveryman
        """)

        result = ["Все поставщики"]
        for answer in cursor.fetchall():
            result.append(answer[0])
        print(result)
        return result

    def take_item_single_info(self):
        """
        Метод получения информации о конкретном товаре
        :return: dict()
        """

        query = f"""
        select *
        from Items
        where item_id = {Storage.get_item_id()}
        """
        print(query)
        cursor = self.connection.cursor()
        cursor.execute(query)
        result = dict()
        for answer in cursor.fetchall():
            result = {
                "id": answer[0],
                "article": answer[1],
                "name": answer[2],
                "edinica": answer[3],
                "cost": answer[4],
                "deliveryman": answer[5],
                "creator": answer[6],
                "category": answer[7],
                "sale": answer[8],
                "count": answer[9],
                "information": answer[10],
                "picture": answer[11]
            }
        return result

    def update_card_picture(self, picture_name: str,
                            user_input_data: list):
        """
        Обновление фотографии товара
        :param picture_name: Новое имя товара
        :param user_input_data: Данные от ввода пользователя
        :return: Bool
        """
        print(tuple(map(str, user_input_data)))
        try:
            query = f"""
                UPDATE Items
                SET item_picture = '{picture_name}',
                item_article = %s,
                item_name = %s,
                item_edinica = %s,
                item_cost = %s,
                item_deliveryman = %s,
                item_creator = %s,
                item_category = %s,
                item_sale = %s,
                item_count = %s,
                item_information = %s
                WHERE item_id = {Storage.get_item_id()}
            """
            cursor = self.connection.cursor()
            cursor.execute(query, tuple(map(str, user_input_data)))
            self.connection.commit()

            return True
        except Exception as e:
            print(e)
            return False

    def create_new_card(self,
                        user_input: list,
                        picture_name: str):
        """
        Метод создания нового товара
        :param user_input: Ввод пользователя
        :param picture_name: Название для фото
        :return: bool
        """
        try:
            query = f"""
            insert into Items (
            item_article,
            item_name,
            item_edinica,
            item_cost,
            item_deliveryman,
            item_creator,
            item_category,
            item_sale,
            item_count,
            item_information,
            item_picture)
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '{picture_name}')
            """
            cursor = self.connection.cursor()
            cursor.execute(query, tuple(map(str, user_input)))
            self.connection.commit()
            return True
        except Exception as e:
            print("Error:", e)
            return False

    def delete_item(self,
                    item_article: str):
        """
        Метод для удаления товара из таблицы
        :return: bool
        """
        # Проверка, что товара нет в заказах
        cursor = self.connection.cursor()
        # Этот код немного неверен
        # Проблема в том, что order_article не является FK
        # это приводит к тому, что при замене в Items
        # Он не будет меняться в Orders
        cursor.execute(f"""
        SELECT *
        FROM Orders
        WHERE order_article LIKE '{item_article}, %'
           OR order_article LIKE '%, {item_article}, %';
        """)
        # Если в ответе от бд есть хоть 1 элемент - отклонение запроса
        if len(cursor.fetchall()) != 0:
            cursor.close()
            return False
        # Если ответ пуст - заказов нет
        cursor.close()
        cursor = self.connection.cursor()
        # Запуск удаления элемента
        cursor.execute(f"""
                delete 
                FROM Items
                WHERE item_id = {Storage.get_item_id()}
                """)
        self.connection.commit()
        return True

    def take_all_text_data_for_combo_box(self,
                                         type_of_data: str):
        """
        Метод для получения списка строк для Выпадающего списка
        :param type_of_data: Наименование колонки для получения данных
        :return: list()
        """
        # По умолчанию - выбираем все колонки
        # Но 100% будет 1 из вариантов Условного Опператора
        column_name = "*"
        if type_of_data == "category":
            column_name = "item_category"
        elif type_of_data == "deliveryman":
            column_name = "item_deliveryman"

        query = f"""
        select DISTINCT {column_name}
        from Items
        order by {column_name}
        """

        cursor = self.connection.cursor()
        cursor.execute(query)

        result = []

        # Да, можно перебрать через fetchone(), который
        # сразу вернет кортеж элементов
        # однако исправление подобных моментов будет на стадии доработки
        for answer in cursor.fetchall():
            result.append(answer[0])

        return result

    def take_all_orders_rows(self):
        """
        Метод получения списка товаров из Таблицы Orders
        :return: [dict()]
        """
        query = """
        select *
        from Orders;
        """

        cursor = self.connection.cursor()
        cursor.execute(query)

        result = []
        for answer in cursor.fetchall():
            result.append(
                {
                    "id": answer[0],
                    "article": answer[1],
                    "create_date": answer[2],
                    "delivery_date": answer[3],
                    "pvz": answer[4],
                    "client_name": answer[5],
                    "code": answer[6],
                    "status": answer[7],

                }
            )
        cursor.close()
        return result

    def take_single_order_data(self):
        """
        Метод получения данных о конкретном товаре
        :param order_id: ID просматриваемого товара
        :return: dict()
        """
        print(f"""
           select *
           from Orders
           where order_id = {Storage.get_order_id()};
           """)
        query = f"""
           select *
           from Orders
           where order_id = {Storage.get_order_id()};
           """

        cursor = self.connection.cursor()
        cursor.execute(query)

        result = []
        for answer in cursor.fetchall():
            result = {
                "id": answer[0],
                "article": answer[1],
                "create_date": answer[2],
                "delivery_date": answer[3],
                "pvz": answer[4],
                "client_name": answer[5],
                "code": answer[6],
                "status": answer[7],

            }

        cursor.close()
        return result

    def take_pvz_address(self,
                         pvz_id):
        """
        Метод получения адреса ПВЗ для заказа
        :param pvz_id: id ПВЗ из заказа
        :return: string
        """
        cursor = self.connection.cursor()
        cursor.execute(
            f"""
            select pvz_address
            from PVZ
            where pvz_id = {pvz_id}
            """
        )

        return str(cursor.fetchall()[0])

    def take_all_pvz_addresses(self):
        """
        Метод получения всех ПВЗ для редактирования / создания нового заказа
        :return: list("1 | Старокачаловская д3к1")
        """
        cursor = self.connection.cursor()
        cursor.execute("""
        select *
        from PVZ
        """)

        result = []
        for answer in cursor.fetchall():
            result.append(f"{answer[0]} | {answer[1]}")

        cursor.close()
        return result

    def take_all_statuses(self):
        """
        Метод получения всех вариантов статуса заказа
        :return: list()
        """
        cursor = self.connection.cursor()
        cursor.execute(
            """
            select DISTINCT order_status
            from Orders;
            """
        )
        return [i[0] for i in cursor.fetchall()]
