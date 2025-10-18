from PySide6.QtWidgets import (QFrame, QPushButton, QHBoxLayout,
                               QWidget, QVBoxLayout, QLabel, QLineEdit)

from Messages import *
from FRAMES import HomePageWindow


class LogInFrame(QFrame):
    def __init__(self, controller):
        """
        Конструктор класса
        :param controller: "self" из класса MainApplicationClass (который главное окно)
        """

        super().__init__()
        self.controller = controller
        self.database = controller.db
        # Создание разметки окна, в которую будет добавляться весь интерфейс
        self.frame_layout = QVBoxLayout(self)
        self.setup_ui()  # Запуск генерации интерфейса

    def setup_ui(self):
        """ Генерация интерфейса """
        title = QLabel("Авторизация")
        title.setObjectName("Title")
        self.frame_layout.addWidget(title)
        self.frame_layout.addStretch()

        # Блок ввода Логина и пароля
        # Блок для Логина
        self.login_edit = self.edit_text_pattern(placeholder_text="Введите логин",
                                                 label_text="Логин")

        # Блок для Пароля
        self.password_edit = self.edit_text_pattern(placeholder_text="Введите пароль",
                                                    label_text="Пароль")

        log_in_button = QPushButton("Войти")
        log_in_button.setObjectName("button")
        log_in_button.clicked.connect(self.log_in)
        self.frame_layout.addWidget(log_in_button)

        guest_button = QPushButton("Войти как гость")
        guest_button.setObjectName("button")
        guest_button.clicked.connect(self.guest_enter)
        self.frame_layout.addWidget(guest_button)

    def log_in(self):
        """ Обработчик нажатия на кнопку log_in """
        # 94d5ous@gmail.com uzWC67 -- Админ
        # tjde7c@yahoo.com YOyhfR -- Менеджер
        # 4np6se@mail.com AtnDjr -- Клиент
        print(f"login: {self.login_edit.text()}\npassword: {self.password_edit.text()}")
        # if self.database.check_user_login_password(user_login=self.login_edit.text(),
        #                                            user_password=self.password_edit.text()):
        if self.database.check_user_login_password(user_login="94d5ous@gmail.com",
                                                   user_password="uzWC67"):
            # Если вернулось true:
            print("Пользователь существует")
            # Переход в новое окно
            self.controller.switch_window(HomePageWindow.HomeFrame)
        else:
            # Отправка сообщения об ошибке
            send_C_message("Ошибка входа! Проверьте Логин и Пароль!")

    def guest_enter(self):
        """ Обработчик нажатия на кнопку guest_button """
        print(f"GUEST")

    def edit_text_pattern(self, placeholder_text: str, label_text: str) -> QLineEdit:
        """
        Паттерн по созданию поля для ввода
        :param placeholder_text: Исчезающий текст
        :param label_text: Текст для подсказки
        :return: QLineEdit
        """
        widget = QWidget()
        widget.setMaximumHeight(300)
        widget_l = QVBoxLayout(widget)
        widget_l.addWidget(QLabel(label_text, objectName="logInLabel"))
        edit = QLineEdit()
        # Установка исчезающего текста
        edit.setPlaceholderText(placeholder_text)
        edit.setObjectName("LogInEdit")  # Установка имени для назначения стиля
        widget_l.addWidget(edit)
        self.frame_layout.addWidget(widget)
        return edit
