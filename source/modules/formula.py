from calendar import monthrange


class Formula:
    # Индекс месяцев в кварталах
    __month_quarter_indexes: dict[int, int] = {1: 1, 2: 2, 3: 3,
                                               4: 1, 5: 2, 6: 3,
                                               7: 1, 8: 2, 9: 3,
                                               10: 1, 11: 2, 12: 3}
    rate: int
    report_year: int
    year_ip_open: int
    month_ip_open: int
    day_ip_open: int
    cells_110_to_113: list[int]
    workers_count: int

    def __init__(self, rate: int, report_year: int, year_ip_open: int, month_ip_open: int, day_ip_open: int,
                 cells_110_to_113: list[int], workers_count: int = None):
        self.rate = rate
        self.report_year = report_year
        self.year_ip_open = year_ip_open
        self.month_ip_open = month_ip_open
        self.day_ip_open = day_ip_open
        self.cells_110_to_113 = cells_110_to_113
        self.workers_count = workers_count

    async def __calculate_quarter_basic_tax(self, val_cell: int) -> float:
        """
        Метод подсчета основного налога в декларации для полей 140-143
        :param val_cell: значение поля (110-113)
        :return: величина основного налога
        """

        quarter_open = (self.month_ip_open // 4) + 1
        quarter_cell = self.cells_110_to_113.index(val_cell) + 1

        if self.year_ip_open >= self.report_year:
            if quarter_cell < quarter_open:
                basic_tax = 0
            elif quarter_cell == quarter_open:
                number_days_in_m_ip_open = monthrange(self.year_ip_open, self.month_ip_open)[1]
                basic_tax = ((((45842 / 12) / number_days_in_m_ip_open) * max(1,
                                                                              number_days_in_m_ip_open - self.day_ip_open + 1)) +
                             ((45842 / 12) * (3 - self.__month_quarter_indexes[self.month_ip_open])))
            else:  # quarter_cell != quarter_open
                basic_tax = 45842 / 4
        else:
            basic_tax = 45842 / 4  # * max(1, 4 - quarter_open)

        return basic_tax

    async def __calculate_quarter_add_tax(self, val_cell: int) -> dict[str, float | bool]:
        """
        Метод подсчета дополнительного налога в декларации для полей 140-143
        :param val_cell: значение поля (110-113)
        :return: величина дополнительного налога
        """

        calculate_next_ad_tax = True
        if val_cell > 300000:
            additional_tax = (float(val_cell) - 300000.0) * 0.01
            if self.workers_count is not None:
                if self.workers_count > 0:
                    if additional_tax > (257061 / 2):
                        additional_tax = (257061 / 2)
                        calculate_next_ad_tax = False
                else:
                    raise ValueError("Не может быть <= 0 сотрудников.")
            else:
                if additional_tax > 257061:
                    additional_tax = 257061
                    # Если доп. налог превысил максимальное значение, последующие не считаем
                    calculate_next_ad_tax = False

        else:
            additional_tax = 0

        return {'add_tax': additional_tax, 'calculate_next_ad_tax': calculate_next_ad_tax}

    async def __calculate_tax(self) -> dict[str, int]:
        """
        Метод подсчета налога в декларации - поля 140-143
        :return: поля 140-143 в формате dict
        """

        calculate_ad_tax_flag = True
        basic_tax_cells = []
        add_tax_cells = []

        for val_cell in self.cells_110_to_113:
            basic_tax = await self.__calculate_quarter_basic_tax(val_cell=val_cell)
            add_tax = 0.0

            # Если доп. налог превысил максимальное значение, последующие не считаем
            if calculate_ad_tax_flag:
                add_tax_opts = await self.__calculate_quarter_add_tax(val_cell=val_cell)
                calculate_ad_tax_flag = add_tax_opts['calculate_next_ad_tax']
                add_tax = add_tax_opts['add_tax']

            basic_tax_cells.append(basic_tax)
            add_tax_cells.append(add_tax)

        # В базовом налоге суммируем за предыдущие кварталы
        code_140_143_basic_tax = [basic_tax_cells[0],
                                  basic_tax_cells[1] + basic_tax_cells[0],
                                  basic_tax_cells[2] + basic_tax_cells[1] + basic_tax_cells[0],
                                  basic_tax_cells[3] + basic_tax_cells[2] + basic_tax_cells[1] + basic_tax_cells[0]]

        # В доп. налоге суммируем за предыдущие кварталы с ограничением
        code_140_143_add_tax = []
        for i, add_tax in enumerate(add_tax_cells):
            if i > 0:
                add_tax = sum(add_tax_cells[0:i])

            if self.workers_count is not None:
                if self.workers_count > 0:
                    if add_tax > (257061 / 2):
                        add_tax = (257061 / 2)
                else:
                    raise ValueError("Не может быть <= 0 сотрудников.")
            else:
                if add_tax > 257061:
                    add_tax = 257061

            code_140_143_add_tax.append(add_tax)

        return {'140': max(0, round(code_140_143_basic_tax[0] + code_140_143_add_tax[0])),
                '141': max(0, round(code_140_143_basic_tax[1] + code_140_143_add_tax[1])),
                '142': max(0, round(code_140_143_basic_tax[2] + code_140_143_add_tax[2])),
                '143': max(0, round(code_140_143_basic_tax[3] + code_140_143_add_tax[3]))
                }

    async def get_codes(self) -> dict[str, int | str]:
        """
        Метод для подсчета полей декларации 020-144
        :return: поля 020-144 в формате dict
        """

        # Считаем поля 140-143
        tax_codes = await self.__calculate_tax()

        code_130 = round((self.rate * self.cells_110_to_113[0]) / 100)
        code_131 = round((self.rate * self.cells_110_to_113[1]) / 100)
        code_132 = round((self.rate * self.cells_110_to_113[2]) / 100)
        code_133 = round((self.rate * self.cells_110_to_113[3]) / 100)
        code_020 = max(0, code_130 - tax_codes['140'])
        code_040 = code_131 - tax_codes['141'] - code_020
        code_050 = code_131 - tax_codes['141'] - code_020
        code_070 = code_132 - tax_codes['142'] - (code_020 + code_040) - code_050
        code_080 = code_132 - tax_codes['142'] - (code_020 + code_040) - code_050
        code_100 = (code_133 - tax_codes['143']) - (code_020 + code_040 - code_050 + code_070 - code_080)  # - 101
        code_101 = 0
        code_110 = code_100  # (code_020 + code_040 - code_050 + code_070 - code_080) - (code_133 - tax_codes['143'])

        codes = {'020': code_020,
                 # '030': код налоговой (пока не надо),
                 '040': code_040 if code_040 >= 0 else '',
                 '050': code_050 if code_050 < 0 else '',
                 # '060': код налоговой (пока не надо),
                 '070': code_070 if code_070 >= 0 else '',
                 '080': code_080 if code_080 < 0 else '',
                 # '090': код налоговой (пока не надо),
                 '100': code_100 if code_100 >= 0 else '',
                 '101': code_101,
                 '1_110': code_110 if code_110 < 0 else '',
                 '2_110': self.cells_110_to_113[0],
                 '111': self.cells_110_to_113[1],
                 '112': self.cells_110_to_113[2],
                 '113': self.cells_110_to_113[3],
                 '120': self.rate,
                 '121': self.rate,
                 '122': self.rate,
                 '123': self.rate,
                 # '124': код налоговой (пока не надо),
                 '130': code_130,
                 '131': code_131,
                 '132': code_132,
                 '133': code_133
                 }

        codes.update(tax_codes)

        return codes
