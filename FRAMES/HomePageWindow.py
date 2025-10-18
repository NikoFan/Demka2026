from PySide6.QtWidgets import (QFrame, QPushButton, QHBoxLayout, QStyle,
                               QWidget, QVBoxLayout, QLabel, QScrollArea)
from PySide6.QtGui import QPixmap, QPalette  # Для фоток
from PySide6.QtCore import Qt
from Messages import *
from FRAMES import LogInWindow


class HomeFrame(QFrame):
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
        back_header_btn.clicked.connect(self.go_back_to_log_in_window)
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
        fio_layout.addWidget(QLabel(user_data["user_name"].replace(" ", "\n"), objectName="FIO"))
        header_widget_hbox.addWidget(fio_widget)

        self.frame_layout.addWidget(header_widget)

        # Отображение списка товаров
        title = QLabel("Список товаров")
        title.setObjectName("Title")
        self.frame_layout.addWidget(title)

        # Создание области прокрутки для списка товаров
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.create_items_cards())
        self.frame_layout.addWidget(scroll_area)

    def create_items_cards(self):
        """ Метод создания карточек товара """
        cards_container = QWidget()  # контейнер для карточек
        cards_container_layout = QVBoxLayout(cards_container)
        # Получение списка товаров
        items_list = self.database.get_all_items()
        for item in items_list:

            item_card = QWidget()
            item_card_hbox = QHBoxLayout(item_card)  # Разметка для ВСЕЙ карточки
            information_vbox = QVBoxLayout()  # Разметка для области с инфой

            # Если скидка юольше 15
            if item['sale'] > 15:
                item_card.setStyleSheet("background: #2E8B57")

            # Цена
            final_cost = QLabel(f"Цена: {item['cost']}", objectName="cardText", wordWrap=True)
            final_cost.setFixedWidth(110)
            another_cost = QLabel("", objectName="cardText", wordWrap=True)
            if item['sale'] > 0:
                # Если есть скидка
                final_cost.setText(f"Цена: <s>{item['cost']}</s>")
                final_cost.setStyleSheet("color: red;")
                another_cost.setText(f"{item['cost'] - (item['cost'] * (item['sale'] / 100))}")

            # Добавление фото в левую часть
            item_card_hbox.addWidget(self.create_picture(item["picture"]))
            information_vbox.addWidget(QLabel(f"{item['category']} | {item['name']}", objectName="cardText", ))
            information_vbox.addWidget(QLabel(f"Описание товара: {item['information']}", objectName="cardText",
                                              wordWrap=True))
            information_vbox.addWidget(
                QLabel(f"Производитель: {item['creator']}", objectName="cardText", wordWrap=True))
            information_vbox.addWidget(
                QLabel(
                    text=f"Поставщик: {item['deliveryman']}",
                    objectName="cardText",
                    wordWrap=True)
            )
            # Усановка кастомной цены
            hbox = QHBoxLayout()
            hbox.addWidget(final_cost)
            hbox.addWidget(another_cost)
            information_vbox.addLayout(hbox)


            information_vbox.addWidget(
                QLabel(f"Единица измерения: {item['edinica']}", objectName="cardText", wordWrap=True))

            # Текстовое поле для Количества
            count_of_items_on_store = QLabel(f"Количество на складе: {item['count']}", objectName="cardText", wordWrap=True)
            if item['count'] == 0:
                # Если количество на складе = 0
                count_of_items_on_store.setStyleSheet("background: blue;")

            information_vbox.addWidget(count_of_items_on_store)

            item_card_hbox.addLayout(information_vbox) # Добавление разметки с ИНФОРМАЦИЕЙ в карточку
            item_card_hbox.addWidget(self.create_discount_widget(str(item['sale'])))

            cards_container_layout.addWidget(item_card)

        return cards_container

    def create_discount_widget(self, sale_count: str):
        """
        Паттер для создания виджета со скидкой
        :param sale_count: Количество скидки
        :return: QWidget
        """
        widget = QWidget()
        widget.setObjectName("sale_widget")
        widget.setFixedWidth(100)
        widget_layout = QVBoxLayout(widget)

        widget_layout.addWidget(QLabel(sale_count + "%", objectName="sale_count"))
        return widget

    def create_picture(self, picture_name: str) -> QLabel:
        """
        Паттерн для создания фото
        :param picture_name: имя фото
        :return: QLabel
        """
        picture_socket = QLabel()
        picture_socket.setScaledContents(True)
        picture_socket.setFixedSize(120, 120)

        picture = QPixmap(f"/home/neoleg/Documents/Demka3Kurs/Demoexam2026/ICONS/{picture_name}")
        picture_socket.setPixmap(picture)  # Установка фото
        return picture_socket

    def go_back_to_log_in_window(self):
        """ Обработчик нажатий на кнопку возврата на главное окно """
        if send_I_message("Вы точно хотите вернуться в окно авторизации?") < 20_000:
            self.controller.switch_window(LogInWindow.LogInFrame)
