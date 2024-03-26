from calendar import monthrange
from datetime import datetime


class Formula:
    # Индекс месяцев в кварталах
    __month_quarter_indexes = {1: 1, 2: 2, 3: 3,
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
        self.workers_count = workers_count if workers_count is not None else 1

    async def __calculate_quarter_tax(self, val_cell: int, calculate_ad_tax: bool = True):
        quarter = (self.month_ip_open // 4) + 1

        if (self.cells_110_to_113.index(val_cell) + 1) < quarter:
            basic_tax = 0
        elif self.year_ip_open >= self.report_year:
            number_days_in_m_ip_open = monthrange(self.year_ip_open, self.month_ip_open)[1]
            basic_tax = (((45842 // 12) // number_days_in_m_ip_open) *
                         max(1, number_days_in_m_ip_open - self.day_ip_open + 1) +
                         ((45842 // 12) * (3 - self.__month_quarter_indexes[self.month_ip_open])))
        else:
            basic_tax = (45842 // 4) * max(1, 4 - quarter)

        add_tax_no_more_257 = True
        if calculate_ad_tax:
            if val_cell > 300000:
                additional_tax = int((float(val_cell) - 300000.0) * 0.01)
                if (self.workers_count is not None) and (self.workers_count <= 0) and (self.workers_count != 1):
                    if additional_tax > 257061:
                        additional_tax = 257061
                        add_tax_no_more_257 = False
                else:
                    if additional_tax > (257061 // 2):
                        additional_tax = (257061 // 2)
                        add_tax_no_more_257 = False
            else:
                additional_tax = 0
        else:
            additional_tax = 0

        return {'add_tax_no_more_257': add_tax_no_more_257,
                'basic_tax': basic_tax,
                'additional_tax': additional_tax,
                }

    async def __calculate_tax(self) -> dict:
        result_cells = []
        calculate_ad_tax_flag = True

        for val_cell in self.cells_110_to_113:
            quarter_tax = await self.__calculate_quarter_tax(val_cell=val_cell,
                                                             calculate_ad_tax=calculate_ad_tax_flag)

            calculate_ad_tax_flag = quarter_tax['add_tax_no_more_257']
            result_cells.append(quarter_tax)

        code_140_add_tax = result_cells[0]['additional_tax']
        code_141_add_tax = result_cells[1]['additional_tax'] - result_cells[0]['additional_tax']
        code_142_add_tax = (result_cells[2]['additional_tax'] - result_cells[1]['additional_tax'] -
                            result_cells[0]['additional_tax'])
        code_143_add_tax = (result_cells[3]['additional_tax'] - result_cells[2]['additional_tax'] -
                            result_cells[1]['additional_tax'] - result_cells[0]['additional_tax'])

        return {'140': max(0, result_cells[0]['basic_tax'] + code_140_add_tax),
                '141': max(0, result_cells[1]['basic_tax'] + code_141_add_tax),
                '142': max(0, result_cells[2]['basic_tax'] + code_142_add_tax),
                '143': max(0, result_cells[3]['basic_tax'] + code_143_add_tax)
                }

    async def get_codes(self):
        tax_codes = await self.__calculate_tax()

        code_130 = (self.rate * self.cells_110_to_113[0]) // 100
        code_131 = (self.rate * self.cells_110_to_113[1]) // 100
        code_132 = (self.rate * self.cells_110_to_113[2]) // 100
        code_133 = (self.rate * self.cells_110_to_113[3]) // 100
        code_020 = max(0, code_130 - tax_codes['140'])
        code_040 = code_131 - tax_codes['141'] - code_020
        code_050 = code_131 - tax_codes['141'] - code_020
        code_070 = code_132 - tax_codes['142'] - (code_020 + code_040) - code_050
        code_080 = code_132 - tax_codes['142'] - (code_020 + code_040) - code_050

        codes = {'020': code_020,
                 # '030': 1,
                 '040': code_040 if code_040 >= 0 else '',
                 '050': code_050 if code_050 < 0 else '',
                 # '060': 1,
                 '070': code_070 if code_070 >= 0 else '',
                 '080': code_080 if code_080 < 0 else '',
                 # '090': 1,
                 # '100': max(0, base_codes['133'] - tax_codes['143'] - (code_020 + code_040 + code_060)),
                 # '1_110': max(0, base_codes['133'] - tax_codes['143'] - (code_020 + code_040 + code_060)),
                 '2_110': self.cells_110_to_113[0],
                 '111': self.cells_110_to_113[1],
                 '112': self.cells_110_to_113[2],
                 '113': self.cells_110_to_113[3],
                 '120': self.rate,
                 '121': self.rate,
                 '122': self.rate,
                 '123': self.rate,
                 '130': code_130,
                 '131': code_131,
                 '132': code_132,
                 '133': code_133
                 }

        codes.update(tax_codes)

        return codes
