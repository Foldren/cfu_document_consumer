from datetime import datetime


class Formula:
    # Индекс месяцев в кварталах
    __month_quarter_indexes = {1: 1, 2: 2, 3: 3,
                               4: 1, 5: 2, 6: 3,
                               7: 1, 8: 2, 9: 3,
                               10: 1, 11: 2, 12: 3}
    rate: int
    report_year: int
    month_ip_open: int
    day_ip_open: int
    cells_110_to_113: list[int]
    workers_count: int

    def __init__(self, rate: int, report_year: int, month_ip_open: int, day_ip_open: int,
                 cells_110_to_113: list[int], workers_count: int = None):
        self.rate = rate
        self.report_year = report_year
        self.month_ip_open = month_ip_open
        self.day_ip_open = day_ip_open
        self.cells_110_to_113 = cells_110_to_113
        self.workers_count = workers_count if workers_count is not None else 1

    async def __calculate_quarter_tax(self, val_cell: int, quarter: int) -> int:
        current_date = datetime.now()

        if self.report_year != current_date.year:
            basic_tax = ((45842 // 12) // 31) * max(1, 3 - self.__month_quarter_indexes[self.month_ip_open])
        else:
            basic_tax = (45842 // 4) * max(1, 4 - quarter)

        if val_cell > 300000:
            additional_tax = int((float(val_cell) - 300000.0) * 0.01)
            if (self.workers_count is not None) and (self.workers_count != 0):
                if additional_tax > 257061:
                    additional_tax = 257061
            else:
                if additional_tax > (257061 // 2):
                    additional_tax = (257061 // 2)
        else:
            additional_tax = 0

        return basic_tax + additional_tax

    async def __calculate_tax(self) -> dict:
        result_cells = []

        for val_cell in self.cells_110_to_113:
            quarter = (self.month_ip_open // 4) + 1
            quarter_tax = await self.__calculate_quarter_tax(val_cell=val_cell, quarter=quarter)
            result_cells.append(quarter_tax)

        return {'140': max(0, result_cells[0]),
                '141': max(0, result_cells[1] - result_cells[0]),
                '142': max(0, result_cells[2] - result_cells[1] - result_cells[0]),
                '143': max(0, result_cells[3] - result_cells[2] - result_cells[1] - result_cells[0])
                }

    async def get_codes(self):
        tax_codes = await self.__calculate_tax()
        base_codes = {'2_110': self.cells_110_to_113[0],
                      '111': self.cells_110_to_113[1],
                      '112': self.cells_110_to_113[2],
                      '113': self.cells_110_to_113[3],
                      '120': self.rate,
                      '121': self.rate,
                      '122': self.rate,
                      '123': self.rate,
                      '130': (self.rate * self.cells_110_to_113[0]) // 100,
                      '131': (self.rate * self.cells_110_to_113[1]) // 100,
                      '132': (self.rate * self.cells_110_to_113[2]) // 100,
                      '133': (self.rate * self.cells_110_to_113[3]) // 100
                      }

        code_020 = max(0, base_codes['130'] - tax_codes['140'])
        code_040 = base_codes['131'] - tax_codes['141'] - code_020
        code_050 = base_codes['131'] - tax_codes['141'] - code_020
        code_070 = base_codes['132'] - tax_codes['142'] - (code_020 + code_040) - code_050
        code_080 = base_codes['132'] - tax_codes['142'] - (code_020 + code_040) - code_050

        result_codes = {'020': code_020,
                        # '030': 1,
                        '040': code_040 if code_040 >= 0 else '',
                        '050': code_050 if code_050 < 0 else '',
                        # '060': 1,
                        '070': code_070 if code_070 >= 0 else '',
                        '080': code_080 if code_080 < 0 else '',
                        # '090': 1,
                        # '100': max(0, base_codes['133'] - tax_codes['143'] - (code_020 + code_040 + code_060)),
                        # '1_110': self.cells_110_to_113[0],
                        }

        result_codes.update(tax_codes)
        result_codes.update(base_codes)

        return result_codes
