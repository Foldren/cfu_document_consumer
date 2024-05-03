from traceback import print_exc
from openpyxl.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet


class Excel:
    ws: Worksheet = None

    def __init__(self, worksh: Worksheet):
        self.ws = worksh

    async def insert_row_to_ws(self, text: str, cols_interval: str) -> None:
        """
        Метод для вставки текста в поле документа.
        :param text: слово которое надо вставить в поле
        :param cols_interval: интервал ячеек в формате A1:B2, AC25
        """

        list_symbols = list(text.upper())

        if ":" not in cols_interval:
            self.ws[cols_interval] = text.upper()

        else:
            # Бежим по первой строке из интервала
            try:
                i = 0
                row_index = 0
                for row in self.ws[cols_interval]:
                    row_index += 1

                    # Если строк несколько, то заполняет данные через строку
                    if row_index % 2 == 0:
                        continue

                    for cell in row:
                        if type(cell) is Cell:
                            if i >= len(list_symbols):
                                break
                            cell.value = list_symbols[i]
                            i += 1
            except:
                print_exc()
                raise Exception("Ошибка при задании интервала!")

    async def insert_rows_to_ws(self, list_rows: list[dict]) -> None:
        """
        Метод для множественного заполнения полей документа. Объект dict_item:
        {'text': 'sometext', 'interval': 'A1:B2'}
        :param list_rows: список строк с объектами dict_item:
        """

        for row in list_rows:
            if ('text' not in row) or ('interval' not in row):
                raise ValueError('Не правильно заданы параметры входных данных.')
            if row['text'] is not None:
                await self.insert_row_to_ws(str(row['text']), row['interval'])
