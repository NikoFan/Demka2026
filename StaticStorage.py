class Storage:
    user_login_pk: str = None
    user_role: str = None

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