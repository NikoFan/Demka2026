# Workers.py
from PySide6.QtCore import QThread, Signal
from typing import List, Dict


class SearchFilterWorker(QThread):
    finished = Signal(list)  # Сигнал с результатом: список словарей

    def __init__(self, db_connection_func, search_text: str = "", company: str = "", stock: str = ""):
        super().__init__()
        self.db_connection_func = db_connection_func  # функция, возвращающая подключение или объект БД
        self.search_text = search_text
        self.company = company
        self.stock = stock

    def run(self):
        try:
            db = self.db_connection_func()
            results = db.search_items_from_table(
                search_text=""
            )
            self.finished.emit(results)
        except Exception as e:
            print(f"Ошибка в потоке: {e}")
            self.finished.emit([])