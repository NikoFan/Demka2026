from PySide6.QtWidgets import (QFrame, QPushButton, QHBoxLayout, QScrollArea, QComboBox,
                               QFileDialog, QWidget, QVBoxLayout, QLabel, QLineEdit)
from PySide6.QtGui import QPixmap
from Messages import *
from FRAMES import HomePageWindow
from StaticStorage import Storage
import os
import shutil


class UpdateOrderFrame(QFrame):

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
        # Получение старых данных о продукте
        self.item_data = self.database.take_single_order_data()
        base_inputs = [
            "id",
            "article",
            "create_date",
            "delivery_date",
            "pvz",
            "client_name",
            "code",
            "status"
        ]
        labels_hints = {
            "id": "Id заказа",
            "article": "Артикул товара",
            "create_date": "Дата создания",
            "delivery_date": "Дата доставки",
            "pvz": "Адрес доставки",
            "client_name": "Имя клиента",
            "code": "Код доставки",
            "status": "Статус заказа"
        }

        self.inputs = []
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        edits_container = QWidget()
        self.container_layout = QVBoxLayout(edits_container)
        print(self.item_data)
        for keys in base_inputs:
            self.inputs.append(
                self.edit_text_pattern(
                    edit_old_text=str(self.item_data[keys]),
                    label_text=labels_hints[keys],
                    accept_to_change=True if keys in ["id"] else False,
                    type_of_enter=True if keys in ["status", "pvz"] else False

                )
            )
        scroll_area.setWidget(edits_container)
        self.frame_layout.addWidget(scroll_area)

        btn = QPushButton("Сохранить изменения")
        btn.setObjectName("button")
        btn.clicked.connect(self.save_changes)

        self.frame_layout.addWidget(btn)

        delete_button = QPushButton("Удалить заказ")
        delete_button.setObjectName("button")
        delete_button.clicked.connect(self.delete_item)

        self.frame_layout.addWidget(delete_button)

    def delete_item(self):
        """ Метод для удаления товарных данных """
        if send_I_message("Вы точно хотите удалить карточку?") < 20_000:
            if not self.database.delete_item(self.item_data["article"]):
                send_C_message("Товар добавлен в Заказ! Удаление невозможно!")
                return
            send_I_message("Товар успешно удален!")
            self.controller.switch_window(HomePageWindow.HomeFrame)

    def save_changes(self):
        """ Функция сохранения и обновления данных в таблице """
        # Сбор данных с ввода пользователя
        user_input_list = []
        # Перебор не всего ввода (до фоток)
        for i in range(1, len(self.inputs) - 1):
            print(str(type(self.inputs[i])) == "<class 'PySide6.QtWidgets.QLineEdit'>")
            input_data = self.inputs[i].text() if str(
                type(self.inputs[i])) == "<class 'PySide6.QtWidgets.QLineEdit'>" else self.inputs[i].currentText().split(" | ")[0] if self.inputs[i].currentText() not in ["Завершен", "Новый"] else self.inputs[i].currentText()
            if len(input_data) != 0:
                user_input_list.append(input_data)
            else:
                send_C_message("Пустой ввод! Введите значение!")
                return
        print("-------------")
        print(user_input_list)

        # ДОБАВИТЬ ПРОВЕРКУ ДЛЯ ДАТЫ!!!!

        try:

            user_input_list[3] = round(float(user_input_list[3]), 2)
            # --- 4. Обновить запись в БД ---
            # if self.database.update_card_picture(
            #         picture_name=new_filename,
            #         user_input_data=user_input_list
            # ):
            #     send_I_message("Карточка успешно обновлена!")
            #     self.controller.switch_window(HomePageWindow.HomeFrame)
            # else:
            #     send_C_message("Ошибка при обновлении!")



        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить фото:\n{str(e)}")
            print("Ошибка:", e)

    def edit_text_pattern(self, edit_old_text: str,
                          label_text: str,
                          accept_to_change: bool = False,
                          type_of_enter: bool = False):
        """
        Паттер для создания поля для ввода (с подсказкой)
        :param edit_old_text: Текст из Таблицы, который надо поменять
        :param label_text: Текс для подсказки
        :param accept_to_change: Разрешение на изменение (запрещено только для id и Иконки)
        :param type_of_enter: False - Поле для ввода | True - Выпадающий список
        :return: QLineEdit
        """
        # По факту - это просто паттерн из окна авторизации, НО теперь текст постоянный
        widget = QWidget()
        widget.setFixedHeight(100)
        widget_l = QVBoxLayout(widget)
        widget_l.addWidget(QLabel(label_text, objectName="UpdateTextHint"))
        if type_of_enter:
            # Если тип ввода True - Выпадающий список
            edit = QComboBox()
            # Т.к. данные стоят хаотично, надо удалить из ПОЛНОГО списка
            # тот вариант, который используется
            # А затем выполнить операцию ["our element"] + [all elements]
            # Удаляем адрес по строке "ID | AddressName"
            if edit_old_text == str(self.item_data["pvz"]):
                list_of_elements: list = self.database.take_all_pvz_addresses()
                print(list_of_elements)
                # Исполняю поиск текущего ПВЗ прям тут, потому что мне было так удобно)
                current_pvz_address = self.database.connection.cursor().execute(f"""
                select pvz_address
                from PVZ
                where pvz_id = {self.item_data['pvz']}""").fetchone()[0]

                print(f"{self.item_data['pvz']} | {current_pvz_address}")
                # Я просто удаляю схожий элемент из списка ВСЕХ пвз
                list_of_elements.remove(f"{self.item_data['id']} | {current_pvz_address}")
                list_of_elements = [f"{self.item_data['id']} | {current_pvz_address}"] + list_of_elements
            else:
                list_of_elements: list = self.database.take_all_statuses()
                print(list_of_elements, edit_old_text, label_text, self.item_data["pvz"])
                list_of_elements.remove(edit_old_text)
                list_of_elements = [edit_old_text] + list_of_elements

            # Добавление списка в выпадающую область
            edit.addItems(list_of_elements)
        else:
            # Если False - Поле для ввода
            edit = QLineEdit()
            # Установка исчезающего текста
            edit.setText(edit_old_text)
            edit.setReadOnly(accept_to_change)
            edit.setObjectName("UpdateTextEdit")  # Установка имени для назначения стиля
        widget_l.addWidget(edit)
        self.container_layout.addWidget(widget)
        return edit

    def go_back_to_log_in_window(self):
        """ Обработчик нажатий на кнопку возврата на главное окно """
        if send_I_message("Вы точно прекратить процесс редактирования Заказа?") < 20_000:
            self.controller.switch_window(HomePageWindow.HomeFrame)
