from PySide6.QtWidgets import (QFrame, QPushButton, QHBoxLayout, QLineEdit, QCheckBox,
                               QComboBox, QWidget, QVBoxLayout, QLabel, QScrollArea)
from PySide6.QtGui import QPixmap, QPalette  # Для фоток

from Messages import *
from FRAMES import (LogInWindow, UpdateCardWindow,
                    CreateCardWindow, OrdersCardsWindow)
from StaticStorage import Storage

from PySide6.QtCore import QTimer


class HomeFrame(QFrame):
    def __init__(self, controller):
        """
        Конструктор класса
        :param controller: "self" из класса MainApplicationClass (который главное окно)
        """

        super().__init__()
        self.controller = controller
        self.database = controller.db

        # Таймер для поиска
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)  # Срабатывает один раз
        self.search_timer.timeout.connect(self.perform_search_and_filter)

        # Виджеты для поиска и фильтрации
        self.search_edit = None
        self.company_combo = None
        self.sort_by_count_checkbox = None

        # Создание разметки окна, в которую будет добавляться весь интерфейс
        self.frame_layout = QVBoxLayout(self)
        self.setup_ui()  # Запуск генерации интерфейса

    def on_any_change(self):
        """Вызывается при любом изменении: поиск, фильтр, сортировка"""
        self.search_timer.stop()
        self.search_timer.start(300)

    def perform_search_and_filter(self):
        """
        После сброса таймера идет перезапись всей Scroll Area
        :return: none
        """
        # Сбор всех данных для корректной перезаписи
        search_text = self.search_edit.text().strip() if self.search_edit else ""
        company = self.company_combo.currentText() if self.company_combo != "Все поставщики" else ""
        sort_by_count = self.sort_by_count_checkbox.isChecked() if self.sort_by_count_checkbox else False
        # Выполняем запрос в основном потоке
        try:
            # Получение списка с учетом всех вводных
            items = self.database.search_and_filter_items(
                search_text=search_text,
                company_filter=company,
                sort_by_count=sort_by_count
            )
            # Отправка команды на перезапись
            self.update_items_display(items)
        except Exception as e:
            print(f"Ошибка при поиске: {e}")
            self.update_items_display([])

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
        # Если входил гость - появится надпись Аккаунт Гостя
        fio_layout.addWidget(QLabel(user_data["user_name"].replace(" ", "\n"), objectName="FIO"))
        header_widget_hbox.addWidget(fio_widget)

        self.frame_layout.addWidget(header_widget)

        """ 3й модуль
        Суть - создать децствия для Менеджера и Администратора
        Для того, чтобы каждый раз не проверять наличие действий у роли
            в класса Storage был создан словарь 'roles_actions'
        Который хранит зависимости Роль:[Действия]
        
        При запуске окна из Storage получается список с действиями,
            которые требуется реализовать для выбранной роли
        После, через цикл 'for' идет перебор списка и для каждого дейсвтия
            работает свой паттерн сборки объектов
        
        Каждый объект интерфейса 3 модуля регулируется из БД
            и то, что в нем будет выводиться - зависит от запросов к Таблицам
        НЕ надо пытаться считать все данные и после - отсортировать их
            средствами python. Вы потеряете больше времени на корректировку вывода
        
        Весь код 3 модуля будет переплетен с кодом 2го модуля, поэтому
            я буду помечать его комментариями (по возможности)
        """

        # Получение списка действий для роли
        roles_actions_list = Storage.get_roles_action()
        # в roles_actions_list хранится список по типу ["Поиск", "Сортировка", "Фильтрация"]
        # Храним ссылки на виджеты для доступа из других методов
        self.search_edit = None
        self.company_combo = None
        self.stock_combo = None
        # Перебор списка
        for action in roles_actions_list:
            match (action):
                case ("Поиск"):
                    self.create_search_block()
                case ("Сортировка"):
                    self.create_sort_block()
                case ("Фильтрация"):
                    self.create_filter_block()
                case ("Заказы"):
                    orders_button = QPushButton("Заказы")
                    orders_button.setObjectName("button")
                    orders_button.clicked.connect(
                        lambda: self.controller.switch_window(
                            OrdersCardsWindow.OrdersCardsFrame
                        )
                    )
                    self.frame_layout.addWidget(orders_button)
                case _:  # Аналог default
                    continue

        # Отображение списка товаров
        title = QLabel("Список товаров")
        title.setObjectName("Title")
        self.frame_layout.addWidget(title)

        # Создание области прокрутки для списка товаров
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.update_items_display(self.database.get_all_items())  # Изначально пусто
        self.frame_layout.addWidget(self.scroll_area)

        create_card_btn = QPushButton("Добавить товар")
        create_card_btn.setObjectName("button")
        create_card_btn.clicked.connect(
            lambda: self.controller.switch_window(CreateCardWindow.CreateCardFrame)
        )
        self.frame_layout.addWidget(create_card_btn)

    def create_sort_block(self):
        """ Метод создания блока сортировки по количеству на складе"""
        widget = QWidget()
        layout = QHBoxLayout(widget)

        self.sort_by_count_checkbox = QCheckBox("Сортировать по количеству на складе")
        self.sort_by_count_checkbox.stateChanged.connect(self.on_any_change)
        layout.addWidget(self.sort_by_count_checkbox)
        layout.addStretch()
        self.frame_layout.addWidget(widget)

    def create_search_block(self):
        """ Метод для создания поля для поиска """
        widget = QWidget()
        layout = QHBoxLayout(widget)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Поиск...")
        self.search_edit.setObjectName("search_edit")
        self.search_edit.textChanged.connect(self.on_any_change)
        layout.addWidget(self.search_edit)
        self.frame_layout.addWidget(widget)

    def update_items_display(self, items_list):
        """Обновляет карточки товаров"""
        container = self.create_items_cards_from_list(items_list)
        # Обновление контейнера (там уже будет новый состав карточек)
        self.scroll_area.setWidget(container)

    def create_filter_block(self):
        """ Метод для создания поля фильтрации"""
        widget = QWidget()
        layout = QHBoxLayout(widget)

        # Фильтр по поставщику
        self.company_combo = QComboBox()
        self.company_combo.setObjectName("company_filter")

        # Подгрузка списока поставщиков из БД
        deliveryman = self.database.take_all_deliveryman()  # Список поставщиков из Таблицы
        self.company_combo.addItems(deliveryman)

        self.company_combo.currentIndexChanged.connect(self.on_any_change)
        layout.addWidget(QLabel("Поставщик:"))
        layout.addWidget(self.company_combo)
        layout.addStretch()
        self.frame_layout.addWidget(widget)

        layout.addStretch()
        self.frame_layout.addWidget(widget)

    def create_items_cards_from_list(self, items_list):
        """Создаёт виджет с карточками из переданного списка"""
        cards_container = QWidget()
        cards_container_layout = QVBoxLayout(cards_container)

        for item in items_list:
            item_card = QWidget()
            item_card.setObjectName("item_card")
            item_card.setMaximumHeight(300)
            item_card_hbox = QHBoxLayout(item_card)

            # Кнопка редактирования
            update_button = QPushButton()
            update_button.setObjectName("update_button")
            update_button.setFixedHeight(290)

            # Даем кнопке имя в виде ID, который является PK в таблице
            update_button.setAccessibleName(str(item["id"]))
            update_button.clicked.connect(self.go_to_update_window)

            # Разметка для размещения строчек текста
            information_vbox = QVBoxLayout(update_button)
            update_button.setLayout(information_vbox)


            if item['sale'] > 15:
                item_card.setStyleSheet("background: #2E8B57")

            final_cost = QLabel(f"Цена: {item['cost']}", objectName="cardText")
            final_cost.setFixedWidth(110)
            another_cost = QLabel("", objectName="cardText")

            if item['sale'] > 0:
                final_cost.setText(f"Цена: <s>{item['cost']}</s>")
                final_cost.setStyleSheet("color: red;")
                another_cost.setText(f"{item['cost'] - (item['cost'] * (item['sale'] / 100))}")

            item_card_hbox.addWidget(self.create_picture(item["picture"]))
            information_vbox.addWidget(QLabel(f"{item['category']} | {item['name']}", objectName="cardText"))
            information_vbox.addWidget(
                QLabel(f"Описание товара: {item['information']}", objectName="cardText", wordWrap=True))
            information_vbox.addWidget(
                QLabel(f"Производитель: {item['creator']}", objectName="cardText", wordWrap=True))
            information_vbox.addWidget(
                QLabel(f"Поставщик: {item['deliveryman']}", objectName="cardText", wordWrap=True))

            hbox = QHBoxLayout()
            hbox.addWidget(final_cost)
            hbox.addWidget(another_cost)
            information_vbox.addLayout(hbox)

            information_vbox.addWidget(
                QLabel(f"Единица измерения: {item['edinica']}", objectName="cardText", wordWrap=True))

            count_label = QLabel(f"Количество на складе: {item['count']}", objectName="cardText", wordWrap=True)
            if item['count'] == 0:
                count_label.setStyleSheet("background: blue;")
            information_vbox.addWidget(count_label)

            item_card_hbox.addWidget(update_button)
            item_card_hbox.addWidget(self.create_discount_widget(str(item['sale'])))

            cards_container_layout.addWidget(item_card)

        return cards_container

    def go_to_update_window(self):
        """
        Обработка нажатия на кнопку для переходя в окно редактирования
        :return: Ничего
        """
        # Если пользователь - Администратор
        if Storage.get_user_role() == "Администратор":
            sender = self.sender()
            print(sender.accessibleName())
            # Устанавливаем ID карточки товара, с которой будет вестись работа
            Storage.set_item_id(sender.accessibleName())

            # Переход на новое окно
            self.controller.switch_window(goal_frame=UpdateCardWindow.UpdateCardFrame)

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
