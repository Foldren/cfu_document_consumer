from datetime import datetime


class XML:
    @staticmethod
    async def form_xml_bytes_file(inn: int, last_name: str, first_name: str, patronymic: str, phone_number: str,
                                  report_year: str, authority_code: str, octmo_code: str, rate: int, workers_count: int,
                                  codes: dict[str, int | str]) -> bytearray:
        date_form = datetime.now().strftime("%d.%m.%Y")
        prize_np = (1 if workers_count > 0 else 2) if workers_count is not None else 2

        code_040 = 0 if codes['040'] == '' else int(codes['040'])
        code_070 = 0 if codes['070'] == '' else int(codes['070'])
        code_100 = 0 if codes['100'] == '' else int(codes['100'])

        avpuumen_6m = code_040 if code_040 >= 0 else codes['050']
        avpuumen_9m = code_070 if code_070 >= 0 else codes['080']
        avpuumen_12m = code_100 if code_100 >= 0 else codes['1_110']
        patronymic = ' Отчество="' + patronymic + '"' if patronymic is not None else ''

        xml_str = \
f"""<Файл xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ИдФайл="NO_USN_5100_5100_519035208616_20240401_fc755932-e3ac-4725-a8d1-66d11225292a" ВерсПрог="1С:БУХГАЛТЕРИЯ 3.0.147.25" ВерсФорм="5.07">
    <Документ КНД="1152017" ДатаДок="{date_form}" Период="34" ОтчетГод="{report_year}" КодНО="{authority_code}" НомКорр="0" ПоМесту="120">
        <СвНП Тлф="{phone_number}">
            <НПФЛ ИННФЛ="{inn}">
                <ФИО Фамилия="{last_name}" Имя="{first_name}"{patronymic}/>
            </НПФЛ>
        </СвНП>
        <Подписант ПрПодп="1"/>
        <УСН>
            <СумНалПУ_НП ОКТМО="{octmo_code}" АвПУКв="{codes['020']}" АвПУУменПг="{avpuumen_6m}" АвПУУмен9м="{avpuumen_9m}" НалПУУменПер="{avpuumen_12m}">
                <РасчНал1 ПризСтав="1" ПризНП="{prize_np}">
                    <Доход СумЗаКв="{codes['2_110']}" СумЗаПг="{codes['111']}" СумЗа9м="{codes['112']}" СумЗаНалПер="{codes['113']}"/>
                    <Ставка СтавкаКв="{rate}" СтавкаПг="{rate}" Ставка9м="{rate}" СтавкаНалПер="{rate}" КодЛьгот="3462010/000300000000"/>
                    <Исчисл СумЗаКв="{codes['130']}" СумЗаПг="{codes['131']}" СумЗа9м="{codes['132']}" СумЗаНалПер="{codes['133']}"/>
                    <УменНал СумЗаКв="{codes['140']}" СумЗаПг="{codes['141']}" СумЗа9м="{codes['142']}" СумЗаНалПер="{codes['143']}"/>
                </РасчНал1>
            </СумНалПУ_НП>
        </УСН>
    </Документ>
</Файл>"""

        return bytearray(xml_str, 'utf-8')
