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
    list_val_cells_110_to_113: list[int]
    workers_count: int

    def __init__(self, rate: int, report_year: int, month_ip_open: int, day_ip_open: int,
                 list_val_cells_110_to_113: list[int], workers_count: int = None):
        self.rate = rate
        self.report_year = report_year
        self.month_ip_open = month_ip_open
        self.day_ip_open = day_ip_open
        self.list_cells_110_to_113 = list_val_cells_110_to_113
        self.workers_count = workers_count

    async def __calculate_quarter_tax(self, val_cell: int, quarter: int):
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

    async def calculate_tax(self):
        result_cells = []

        for val_cell in self.list_cells_110_to_113:
            quarter = (self.month_ip_open // 4) + 1
            quarter_tax = await self.__calculate_quarter_tax(val_cell=val_cell, quarter=quarter)
            result_cells.append(quarter_tax)

        return {'140': max(0, result_cells[0]),
                '141': max(0, result_cells[1] - result_cells[0]),
                '142': max(0, result_cells[2] - result_cells[1] - result_cells[0]),
                '143': max(0, result_cells[3] - result_cells[2] - result_cells[1] - result_cells[0])
                }
