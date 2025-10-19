from PySide6.QtWidgets import (QFrame, QPushButton, QHBoxLayout, QScrollArea,
                               QFileDialog, QWidget, QVBoxLayout, QLabel, QLineEdit)
from PySide6.QtGui import QPixmap
from Messages import *
from FRAMES import HomePageWindow
from StaticStorage import Storage
import os
import shutil


class CreateCardFrame(QFrame):

    def __init__(self, controller):
        """
        Конструктор класса
        :param controller: "self" из класса MainApplicationClass (который главное окно)
        """

        super().__init__()
        self.controller = controller
        self.database = controller.db

        self.ICONS_DIR = "/home/neoleg/Documents/Demka3Kurs/Demoexam2026/ICONS"

        # Путь к новой фотографии
        self.new_picture_path = None

        # Создание разметки окна, в которую будет добавляться весь интерфейс
        self.frame_layout = QVBoxLayout(self)
        self.setup_ui()  # Запуск генерации интерфейса

    def setup_ui(self):
        """ Генерация интерфейса"""
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
        title = QLabel("Редактирование")
        title.setObjectName("Title")
        self.frame_layout.addWidget(title)

        # Создание полей для замены данных
        """
        Один из самых трудоемких процессов в 3 модуле
        Суть в том, что для каждого поля надо создать свою строку
            куда надо передать текстовые данные (старые)

        Если создавать не для каждого поля (а сделать как в карточке товара)
            когда сразу в разметку добавлялся объект
            это приведет к усложнению процесса считывания данных из полей для ввода

        Самый порстой вариант, как это ускорить - сделать паттерны полей для ввода
            чтобы в паттерне создавался объект, в него вставлялся Текст
            ему давался стиль и все стартовые значения
            затем его в этом же паттерне надо добавить в разметку
            и ВЕРНУТЬ (return)
            "Возврат" поля для ввода из def нужно для того, чтобы
            определить его в self.enter_place переменную, которая будет
            закреплена за ним.

        Этот шаг позволит при считывании исользовать self.enter_place
            переменную для полученния пользовательского ввода
        """

        # Получение старых данных о продукте
        self.item_data = {
            "article": "Укажите артикул",
            "name": "Укажиет наименование",
            "edinica": "Введите единицу измерения",
            "cost": "Укажите стоимость товара",
            "deliveryman": "Поставщик",
            "creator": "Производитель",
            "category": "Категория",
            "sale": "Скидка",
            "count": "Количество на складе",
            "information": "Информация"
        }
        self.current_picture_filename = ""
        base_inputs = [
            "article",
            "name",
            "edinica",
            "cost",
            "deliveryman",
            "creator",
            "category",
            "sale",
            "count",
            "information"
        ]
        label_hints = {
            "article": "Артикул товара",
            "name": "Наименование товара",
            "edinica": "Единица измерения",
            "cost": "Стоимость товара",
            "deliveryman": "Поставщик",
            "creator": "Производитель",
            "category": "Категория",
            "sale": "Скидка",
            "count": "Количество на складе",
            "information": "Информация"
        }
        self.inputs = []
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        edits_container = QWidget()
        self.container_layout = QVBoxLayout(edits_container)
        for keys in base_inputs:
            self.inputs.append(
                self.edit_text_pattern(
                    edit_old_text=str(self.item_data[keys]),
                    label_text=label_hints[keys]
                )
            )
        scroll_area.setWidget(edits_container)
        self.frame_layout.addWidget(scroll_area)

        # Отображение текущего фото
        self.picture_label = QLabel()
        self.picture_label.setFixedSize(200, 200)
        self.picture_label.setStyleSheet("border: 1px solid gray;")
        self.update_picture_preview()
        self.frame_layout.addWidget(self.picture_label)

        # Кнопка замены фотографии
        change_photo_button = QPushButton("Добавить новое фото")
        change_photo_button.clicked.connect(self.select_new_photo)
        change_photo_button.setObjectName("button")
        self.frame_layout.addWidget(change_photo_button)

        btn = QPushButton("Сохранить изменения")
        btn.setObjectName("button")
        btn.clicked.connect(self.save_changes)

        self.frame_layout.addWidget(btn)

    def change_old_items_data(self):
        """ Метод для обновления товарных данных """
        print("=====Данные=====")

    def update_picture_preview(self):
        """Обновляет превью фото в QLabel"""
        full_path = os.path.join(self.ICONS_DIR, self.current_picture_filename)
        if os.path.exists(full_path):
            pixmap = QPixmap(full_path)
            self.picture_label.setPixmap(pixmap.scaled(
                self.picture_label.width(),
                self.picture_label.height()
            ))
        else:
            self.picture_label.setText("Фото не найдено")

    def select_new_photo(self):
        """ Метод открытия диалогового окна """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите новое фото",
            "",
            "Изображения (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.new_picture_path = file_path
            # Показываем превью нового фото (временно)
            pixmap = QPixmap(file_path)
            self.picture_label.setPixmap(pixmap.scaled(
                self.picture_label.width(),
                self.picture_label.height()
            ))

    def save_changes(self):
        """Сохраняет изменения: копирует новое фото, удаляет старое, обновляет БД"""
        # Сбор данных с ввода пользователя
        user_input_list = []
        # Перебор не всего ввода (до фоток)
        for i in range(len(self.inputs)):
            if len(self.inputs[i].text()) != 0:
                user_input_list.append(self.inputs[i].text())
            else:
                send_C_message("Пустой ввод! Введите значение!")
                return

        try:
            new_filename = ""

            if self.new_picture_path:
                # --- 1. Сформировать новое имя файла ---
                _, ext = os.path.splitext(self.new_picture_path)
                # Сохраняем как article + расширение (например, "ART123.png")
                new_filename = f"{self.inputs[0]}{ext}"
                new_full_path = os.path.join(self.ICONS_DIR, new_filename)

                # --- 3. Скопировать новое фото в папку ICONS ---
                shutil.copy2(self.new_picture_path, new_full_path)
                print(f"Новое фото сохранено: {new_filename}")


            # --- 4. Обновить запись в БД ---
            if self.database.create_new_card(
                    user_input=user_input_list,
                    picture_name=new_filename

            ):
                send_I_message("Карточка успешно добавлена!")
                self.controller.switch_window(HomePageWindow.HomeFrame)
            else:
                send_C_message("Ошибка при создании карточки!")



        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить фото:\n{str(e)}")
            print("Ошибка:", e)

    def edit_text_pattern(self, edit_old_text: str,
                          label_text: str) -> QLineEdit:
        """
        Паттер для создания поля для ввода (с подсказкой)
        :param edit_old_text: Исчезающий Текст
        :param label_text: Текс для подсказки
        :return: QLineEdit
        """
        # По факту - это просто паттерн из окна авторизации, НО теперь текст постоянный
        widget = QWidget()
        widget.setFixedHeight(100)
        widget_l = QVBoxLayout(widget)
        widget_l.addWidget(QLabel(label_text, objectName="UpdateTextHint"))
        edit = QLineEdit()
        # Установка исчезающего текста
        edit.setPlaceholderText(edit_old_text)
        edit.setObjectName("UpdateTextEdit")  # Установка имени для назначения стиля
        widget_l.addWidget(edit)
        self.container_layout.addWidget(widget)
        return edit

    def go_back_to_log_in_window(self):
        """ Обработчик нажатий на кнопку возврата на главное окно """
        if send_I_message("Вы точно прекратить процесс редактирования товара?") < 20_000:
            self.controller.switch_window(HomePageWindow.HomeFrame)
