from PySide6.QtWidgets import (QFrame, QPushButton, QHBoxLayout, QLineEdit, QCheckBox,
                               QComboBox, QWidget, QVBoxLayout, QLabel, QScrollArea)

from Messages import *
from FRAMES import HomePageWindow
from StaticStorage import Storage


class OrdersCardsFrame(QFrame):
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
        # Шапка с кнопкой назад и ФИО
        header_widget = QWidget()

        header_widget.setObjectName("header_widget")
        header_widget_hbox = QHBoxLayout(header_widget)

        # Добавление кнопки "Назад"
        back_header_btn = QPushButton("< Назад")
        back_header_btn.setFixedWidth(150)
        back_header_btn.clicked.connect(self.go_back_to_home_page_window)
        back_header_btn.setObjectName("back_header_button")
        header_widget_hbox.addWidget(back_header_btn)
        header_widget_hbox.addStretch()

        # Добавление фио
        # получение информации по пользователю (используя Login из статического класса)
        user_data: dict = self.database.take_user_data()
        fio_widget = QWidget()
        fio_layout = QVBoxLayout(fio_widget)
        print(user_data["user_name"].replace(" ", "\n"))
        # Добавляем не просто ФИО, а делим его построчно
        # Если входил гость - появится надпись Аккаунт Гостя
        fio_layout.addWidget(QLabel(user_data["user_name"].replace(" ", "\n"), objectName="FIO"))
        header_widget_hbox.addWidget(fio_widget)

        self.frame_layout.addWidget(header_widget)

        # Получить список заказов всех

        # Отображение списка товаров
        title = QLabel("Список заказов")
        title.setObjectName("Title")
        self.frame_layout.addWidget(title)

        # Создание области прокрутки для списка товаров
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        print(self.database.take_all_orders_rows())
        self.scroll_area.setWidget(
            self.create_items_cards_from_list(self.database.take_all_orders_rows()))  # Изначально пусто
        self.frame_layout.addWidget(self.scroll_area)

        create_card_btn = QPushButton("Добавить заказ")
        create_card_btn.setObjectName("button")
        create_card_btn.clicked.connect(
            lambda: print("Переход в окно создание заказа")
        )
        self.frame_layout.addWidget(create_card_btn)

    def create_items_cards_from_list(self, items_list):
        """Создаёт виджет с карточками из переданного списка"""
        cards_container = QWidget()
        cards_container_layout = QVBoxLayout(cards_container)

        for item in items_list:
            print(item)
            order_card = QWidget()
            order_card.setObjectName("item_card")
            order_card.setMaximumHeight(170)
            order_card_hbox = QHBoxLayout(order_card)

            # Кнопка редактирования
            update_button = QPushButton()
            update_button.setObjectName("update_button")
            update_button.setFixedHeight(150)

            # Даем кнопке имя в виде ID, который является PK в таблице
            update_button.setAccessibleName(str(item["id"]))
            update_button.clicked.connect(self.go_to_update_window)

            # Разметка для размещения строчек текста
            information_vbox = QVBoxLayout(update_button)
            update_button.setLayout(information_vbox)

            information_vbox.addWidget(
                QLabel(f"Артикул заказа: {item['article']}", objectName="cardText", wordWrap=True))

            information_vbox.addWidget(
                QLabel(f"Статус закааз: {item['status']}", objectName="cardText", wordWrap=True))

            information_vbox.addWidget(
                QLabel(f"Адрес пункта выдачи: {self.database.take_pvz_address(item['pvz'])}", objectName="cardText",
                       wordWrap=True))

            information_vbox.addWidget(
                QLabel(f"Дата заказа: {item['create_date']}", objectName="cardText", wordWrap=True))

            order_card_hbox.addWidget(update_button)

            cards_container_layout.addWidget(order_card)

        return cards_container

    def go_to_update_window(self):
        """
        Обработка нажатия на кнопку для переходя в окно редактирования
        :return: Ничего
        """
        # Если пользователь - Администратор
        if Storage.get_user_role() == "Администратор":
            ...

    def go_back_to_home_page_window(self):
        """ Обработчик нажатий на кнопку возврата на главное окно """
        if send_I_message("Вы точно хотите вернуться в окно товаров?") < 20_000:
            self.controller.switch_window(HomePageWindow.HomeFrame)
