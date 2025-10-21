class Storage:
    user_login_pk: str = None
    user_role: str = None

    # Список действий для каждой роли
    roles_actions = {
        # Администратору еще добавится блок с действиями над товарами
        "Администратор": ["Поиск", "Сортировка", "Фильтрация", "Заказы"],
        "Менеджер": ["Поиск", "Сортировка", "Фильтрация", "Заказы"],
        "Авторизированный клиент": [],  # Он только просматривает, как и гость
        "Гость": []
    }

    # id товара, с которым идет работа (Редактирование)
    current_item_id: str = None

    @staticmethod
    def set_item_id(new_id):
        Storage.current_item_id = new_id

    @staticmethod
    def get_item_id(): return Storage.current_item_id

    @staticmethod
    def get_roles_action():
        return Storage.roles_actions[Storage.user_role]

    @staticmethod
    def set_user_login(new_login: str):
        """
        Метод для установки логина активного пользователя
        :param new_login: Новый логин активного пользователя
        :return: none
        """
        Storage.user_login_pk = new_login

    @staticmethod
    def get_user_login() -> str: return Storage.user_login_pk

    @staticmethod
    def set_user_role(new_role: str):
        """
        Метод для установки роли активного пользователя
        :param new_role: Роль активного пользователя
        :return: none
        """
        Storage.user_role = new_role

    @staticmethod
    def get_user_role() -> str: return Storage.user_role
