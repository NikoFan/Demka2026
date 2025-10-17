import pandas as pd
import psycopg
import openpyxl
from config import *
from datetime import datetime


def import_clients(conn):
    query = """
    insert into Client
    values (%s, %s, %s, %s);
    """
    data_frame = pd.read_excel(
        "/home/neoleg/Documents/Demka3Kurs/Demoexam2026/EXCEL/user_import.xlsx",
        engine="openpyxl"
    )
    cursor = conn.cursor()
    for row in data_frame.itertuples():
        print(row)

        values = (
            row._1, row.ФИО, row.Логин, row.Пароль
        )
        cursor.execute(query, values)
    conn.commit()
    cursor.close()


def import_items(conn):
    query = """
    insert into Items
    values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    data_frame = pd.read_excel(
        "/home/neoleg/Documents/Demka3Kurs/Demoexam2026/EXCEL/Tovar.xlsx",
        engine="openpyxl"
    )
    cursor = conn.cursor()
    for row in data_frame.itertuples():
        picture = row.Фото
        if str(row.Фото) == "nan":
            picture = ""
        values = (
            row.Артикул, row._2,
            row._3, row.Цена,
            row.Поставщик,
            row.Производитель,
            row._7,
            row._8,
            row._9,
            row._10,
            picture
        )
        print(values)
        cursor.execute(query, values)
    conn.commit()
    cursor.close()

def import_pvz(conn):
    query = """
        insert into PVZ
        values (%s, %s);
        """
    data_frame = pd.read_excel(
        "/home/neoleg/Documents/Demka3Kurs/Demoexam2026/EXCEL/Пункты выдачи_import.xlsx",
        engine="openpyxl"
    )
    cursor = conn.cursor()
    for row in data_frame.itertuples():
        print(row)
        '''
        Почему я использую Индекс, хотя говорил его не трогать???
        Проблема в таблице, (и не в ней одной)
        Используется FK в Orders, где выводится номер ПВЗ,
        однако у ПВЗ нет номеров
        Это скорее всего ошибка ФИРПО (бывает)
        так что просто адаптируемся под ситуацию
        '''
        values = (
            row.Index, # ДА - я тут использую индекс
            row._1
        )
        cursor.execute(query, values)
    conn.commit()
    cursor.close()

def import_orders(conn):
    query = """
        insert into Orders
        values (%s, %s, %s, %s, %s, %s, %s, %s);
        """
    data_frame = pd.read_excel(
        "/home/neoleg/Documents/Demka3Kurs/Demoexam2026/EXCEL/Заказ_import.xlsx",
        engine="openpyxl"
    )
    cursor = conn.cursor()
    for row in data_frame.itertuples():
        print(row)
        date = str(row._3).split(" ")[0]
        # print(str(row._3).split(" ")[0].format("YYYY-MM-DD"))
        if "." in date:
            print("dddd")
            try:
                print(datetime.strptime(date, "%d.%m.%Y").strftime('%Y-%m-%d'))
            except Exception:
                date = "2025-12-12"
        values = (
            row._1,
            row._2,
            date, # Вы дату там видели? 30.02.2025 (30 дней в феврале жиес)
            str(row._4).split(" ")[0],
            row._5,
            row._6,
            row._7,
            row._8,
        )
        print(values)
        cursor.execute(query, values)
    conn.commit()
    cursor.close()


connection = psycopg.connect(
    user=user_name,
    password=user_password,
    host=host_address,
    dbname=database_name
)

# import_clients(connection)
# import_items(connection)
# import_pvz(connection)
import_orders(connection)
