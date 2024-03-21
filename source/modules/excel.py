from openpyxl.worksheet.worksheet import Worksheet


class Excel:
    # 80 столбцов для декларации
    cols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
            'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
            'U', 'V', 'W', 'X', 'Y', 'Z', 'AA', 'AB', 'AC', 'AD',
            'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN',
            'AO', 'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX',
            'AY', 'AZ', 'BA', 'BB', 'BC', 'BD', 'BE', 'BF', 'BG', 'BH',
            'BI', 'BJ', 'BK', 'BL', 'BM', 'BN', 'BO', 'BP', 'BQ', 'BR',
            'BS', 'BT', 'BU', 'BV', 'BW', 'BX', 'BY', 'BZ', 'CA', 'CB']
    ws: Worksheet = None

    def __init__(self, worksh: Worksheet):
        self.ws = worksh

    async def insert_row_to_ws(self, text: str, row_options: dict, is_title_list: bool = True) -> None:
        """
        Функция для вставки текста в поле декларации.

        :param is_title_list: флаг титульного листа, в нем в 2 раза больше ячеек
        :param text: слово которое надо вставить в поле декларации
        :param row_options: опции строки (индекс первого столбца, последнего, индекс строки)
        """

        if ('first_col' not in row_options) or ('last_col' not in row_options) or ('index' not in row_options):
            raise ValueError('Не верно заданы опции строки декларации.')

        list_symbols = list(text.upper())
        i = row_options['first_col']
        k = 0
        while (i <= row_options['last_col']) and (k < len(list_symbols)):
            try:
                cell_index = f"{self.cols[i]}{row_options['index']}"
                self.ws[cell_index] = list_symbols[k]
            except IndexError:
                break
            k += 1

            if is_title_list:
                i += 2
            else:
                i += 1

    async def insert_rows_to_ws(self, list_rows: list[dict]) -> None:
        """
        Метод для множественного заполнения полей декларации.

        :param list_rows: список строк со значением типа
        {'text': 'sometext', 'row_options': {'first_col': 1, 'last_col': 1, 'index': 1}}
        """
        for row in list_rows:
            if (('text' not in row) or ('row_options' not in row) or ('first_col' not in row['row_options']) or
                    ('last_col' not in row['row_options']) or ('index' not in row['row_options'])):
                raise ValueError('Не правильно заданы параметры входных данных.')
            await self.insert_row_to_ws(str(row['text']), row['row_options'])
