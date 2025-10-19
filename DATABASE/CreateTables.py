import psycopg  # Добавление бибоиотеки для работы с Postgres
from config import *  # Добавление данных из конфига

'''
Таблицы:
    Client - user_import.xlsx (PK)
    Items - Tovar.xlsx (PK)
    PVZ - Пункты_выдачи_import.xlsx (PK)
    Orders - Заказ_import.xlsx (PK, FK (Адрес выдачи))
        по идее там также надо FK (ФИО клиента), но если делать так - будет ошибка 3 норм формы
    
'''
create_table_USER = """
create table Client (
user_role text not null,
user_name text not null,
user_login text not null primary key,
user_password text not null
)
"""

# Да, тут ID выделен отдельно, так надо по Заданию
create_table_ITEMS = """
create table Items(
item_id serial primary key not null,
item_article text not null,
item_name text not null,
item_edinica text not null,
item_cost int not null,
item_deliveryman text not null,
item_creator text not null,
item_category text not null,
item_sale int not null,
item_count int not null,
item_information text not null,
item_picture text -- Не требуется быть всегда заполненным
)
"""

create_table_PVZ = """
create table PVZ(
pvz_id int primary key not null,
pvz_address text not null
)
"""

create_table_ORDERS = """
create table Orders(
order_id int primary key not null,
order_article text not null,
order_create_date date not null,
order_delivery_date date not null,

order_pvz_id_fk int not null,
foreign key (order_pvz_id_fk) references PVZ(pvz_id)
ON UPDATE CASCADE,
order_client_name text not null,
order_code int not null,
order_status text not null
)
"""

def create_table(query, conn):
    """
    Функция создания таблиц
    :param query: запрос для создания
    :param conn: строка подключения
    :return: null
    """
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    cursor.close()

connection = psycopg.connect(
    user=user_name,
    password=user_password,
    host=host_address,
    dbname=database_name
)
# create_table(
#     query=create_table_USER,
#     conn=connection
# )

create_table(
    query=create_table_ITEMS,
    conn=connection
)

# create_table(
#     query=create_table_PVZ,
#     conn=connection
# )
#
# create_table(
#     query=create_table_ORDERS,
#     conn=connection
# )