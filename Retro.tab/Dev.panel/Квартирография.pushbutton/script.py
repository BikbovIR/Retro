# -*- coding: utf-8 -*-
__title__ = "Квартирография"
__doc__ = """Date = 16.12.24
Перед началом работы задайте значения параметров: 
ADSK_Тип помещения
ADSK_Номер квартиры

Заполняет параметры:
ADSK_Площадь квартиры
ADSK_Площадь квартиры общая
ADSK_Площадь квартиры жилая
ADSK_Число комнат
ADSK_Коэффициент площади
ADSK_Площадь с коэффициентом
ADSK_Индекс помещения.
------------------------------------------------------------------
Для работы скрипта в проекте обязательно наличие хотя бы одной из спецификаций ADSK_RU_ШаблонПроекта_АР:

В_Квартиры-02_Заполнение площадей (без Dynamo)_1 знак
В_Квартиры-02_Заполнение площадей (без Dynamo)_2 знака

------------------------------------------------------------------
Округление площадей до 2 знаков после запятой

Типы помещений:
"1" - жилое   коэффициент - 1
"2" - нежилое коэффициент - 1
"3" - лоджия  коэффициент - 0.5
"4" - балкон  коэффициент - 0.3
"5" - общее   коэффициент - 1
------------------------------------------------------------------
Author: Bikbov Ilnur"""

#---------------------------------------------------------------------
# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#---------------------------------------------------------------------
# Regular + Autodesk
from pyrevit import script
from Autodesk.Revit import UI
from Autodesk.Revit import DB

import clr

clr.AddReference('RevitNodes')
import Revit

clr.ImportExtensions(Revit.Elements)
clr.ImportExtensions(Revit.GeometryConversion)

import sys

sys.path.append("c:/Program Files (x86)/IronPython 2.7/Lib")
sys.path.append("c:/Program Files/IronPython 2.7/Lib")

import System


#---------------------------------------------------------------------
# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#---------------------------------------------------------------------
doc          = __revit__.ActiveUIDocument.Document
app          = __revit__.Application


parAptNumber = []  # № КВАРТИРЫ
parAptTip    = []  # Это Тип помещения
rooms        = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms)
#---------------------------------------------------------------------
# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
#---------------------------------------------------------------------

# Получение списков параметров 'ADSK_Номер квартиры' и 'ADSK_Тип помещения''

for room in rooms:
    parAptNumber.append(room.GetParameters('ADSK_Номер квартиры')[0].AsString())
    parAptTip.append(room.GetParameters('ADSK_Тип помещения')[0].AsInteger())

# Проверка заполненности параметров

room_without_AptNumber = []  # квартиры, с незаполненным параметром ADSK_Номер квартиры
room_with_AptNumber    = []  # квартиры, с заполненным параметром ADSK_Номер квартиры
room_without_AptTip    = []  # квартиры, с незаполненным параметром ADSK_Тип помещения
room_with_AptTip       = []  # квартиры, с заполненным параметром ADSK_Тип помещения

count                  = len(list(rooms))

for room, parAptNum, parAptT in zip(rooms, parAptNumber, parAptTip):
    if parAptNum:
        room_with_AptNumber.append(room)
    else:
        room_without_AptNumber.append(room)
    if parAptT:
        room_with_AptTip.append(room)
    else:
        room_without_AptTip.append(room)

set_rooms_difference   = set(room_without_AptTip) - set(room_without_AptNumber)
set_rooms_intersection = list(set(room_with_AptNumber) & set(room_with_AptTip))

# Вывод окна с сообщением

# Функция для отображения сообщений
def show_message(title, message):
    UI.TaskDialog.Show(title, message)

# Текст сообщения
Text = ""

# Логика обработки помещений
if room_without_AptNumber and len(room_without_AptNumber) == count:
    if len([i.Location for i in room_without_AptNumber if i.Location is None]) > 0:
        Text += (
            "Для всех помещений не заполнены параметры ADSK_Номер квартиры и ADSK_Тип помещения. "
            "\nЗаполните этот параметр для каждого помещения в соответствии с тем, к какой квартире оно принадлежит.\n"
            "Тип помещения задается в спецификации:\nВ_Квартиры-01-1_Заполнение типов помещений.\n\n"
            "ID помещений:\n\n" + ",".join(str(i.Id) for i in room_without_AptNumber if i.Location is not None) +
            "\n\nУдалите неразмещенные помещения через спецификацию: В_Помещения_Заполнение данных\n\n" +
            ",".join(str(i.Id) for i in room_without_AptNumber if i.Location is None) + "\n\n"
        )
    else:
        Text += (
            "Для всех помещений не заполнены параметры ADSK_Номер квартиры и ADSK_Тип помещения.\n"
            "Заполните этот параметр для каждого помещения в соответствии с тем, к какой квартире оно принадлежит.\n"
            "Тип помещения задается в спецификации:\nВ_Квартиры-01-1_Заполнение типов помещений.\n\n"
            "ID помещений:\n\n" + ",".join(str(i.Id) for i in room_without_AptNumber if i.Location is not None) + "\n\n"
        )
elif room_without_AptNumber:
    Text += (
        "Для некоторых помещений не заполнены параметры ADSK_Номер квартиры\n"
        "Заполните этот параметр для каждого помещения в соответствии с тем, к какой квартире оно принадлежит\n\n"
        "ID помещений:\n\n" + ",".join(str(i.Id) for i in room_without_AptNumber) + "\n\n"
        "Имена помещений:\n\n" + ",".join(
            str(i.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString()) for i in room_without_AptNumber
        ) + "\n\n"
    )

if set_rooms_difference:
    Text += (
        "Для некоторых помещений не заполнен параметр ADSK_Тип помещения\n"
        "Тип помещения задается в спецификации:\nВ_Квартиры-01-1_Заполнение типов помещений\n\n"
        "ID помещений:\n\n" + ",".join(str(i.Id) for i in room_without_AptTip) + "\n\n"
        "Имена помещений:\n\n" + ",".join(
            str(i.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString()) for i in room_without_AptTip
        ) + "\n\n"
    )

class MainForm(System.Windows.Forms.Form):  # Windows form
    def __init__(self):
        self.InitializeComponent()

    def InitializeComponent(self):
        self._textBox1 = System.Windows.Forms.RichTextBox()
        self._label1 = System.Windows.Forms.Label()
        self._textBox2 = System.Windows.Forms.TextBox()
        self._button1 = System.Windows.Forms.Button()
        self.SuspendLayout()

        # textBox1

        self._textBox1.Location = System.Drawing.Point(50, 50)
        self._textBox1.AppendText(Text)
        self._textBox1.Name = "textBox1"
        self._textBox1.Size = System.Drawing.Size(900, 650)
        self._textBox1.TabIndex = 0

        # label1

        self._label1.Location = System.Drawing.Point(180, 15)
        self._label1.Name = "label1"
        self._label1.Size = System.Drawing.Size(640, 23)
        self._label1.TabIndex = 1
        self._label1.Text = "ВНИМАНИЕ! Не все параметры для помещений заполнены!"
        self._label1.TextAlign = System.Drawing.ContentAlignment.MiddleCenter

        # button1

        self._button1.DialogResult = System.Windows.Forms.DialogResult.OK
        self._button1.Location = System.Drawing.Point(460, 730)
        self._button1.Name = "button1"
        self._button1.Size = System.Drawing.Size(80, 40)
        self._button1.TabIndex = 2
        self._button1.Text = "OK"
        self._button1.UseVisualStyleBackColor = True

        # MainForm

        self.ClientSize = System.Drawing.Size(1000, 800)
        self.Controls.Add(self._button1)
        self.Controls.Add(self._label1)
        self.Controls.Add(self._textBox1)
        self.CenterToScreen()
        self.Location = System.Drawing.Point(1000, 600)
        self.Name = ""
        self.Text = "Отчет"
        self.ResumeLayout(False)
        self.PerformLayout()

if room_without_AptNumber or set_rooms_difference:
    dialog = MainForm()
    dialog.ShowDialog()
else:
    show_message("Отчет по помещениям", "Супер! Параметры заполнены корректно")
# Получение списка помещений для обработки, в зависимости от исходных данных.
# Все помещения (False), только тех, которые относятся к квартирам (True)

bool = 1
itog_rooms = []  # Итоговый список помещений для заполнения параметров

if bool:
    itog_rooms.extend(set_rooms_intersection)
else:
    itog_rooms.extend(rooms)

# Назначение параметров


roundCount = 2 # Округление площади
koefLogia  = 0.5  # Коэффициент площади лоджии
koefBalkon = 0.3  # Коэффициент площади балкона

dict_aparts = {}  # Словарь квартир с помещениями
dict_aparts_number = {}  # Словарь квартир с количеством комнат
room_values = []  # Список помещений в квартире


if itog_rooms:
    t = DB.Transaction(doc, 'Квартирография') # Открытие транзакции
    t.Start()
    #Получение словаря квартир
    for itog_room in itog_rooms:
        aptNum = itog_room.GetParameters('ADSK_Номер квартиры')[0].AsString()
        if aptNum in dict_aparts:
            room_values = dict_aparts[aptNum]
            room_values.append(itog_room)
            dict_aparts[aptNum] = room_values
        else:
            room_values = [itog_room]
            dict_aparts[aptNum] = room_values

        # Назначение коэффициента площади

        apart_tip_room = itog_room.GetParameters('ADSK_Тип помещения')[0].AsInteger()
        if apart_tip_room == 1:
            itog_room.GetParameters('ADSK_Коэффициент площади')[0].Set(1)
        elif apart_tip_room == 2:
            itog_room.GetParameters('ADSK_Коэффициент площади')[0].Set(1)
        elif apart_tip_room == 3:
            itog_room.GetParameters('ADSK_Коэффициент площади')[0].Set(koefLogia)
        elif apart_tip_room == 4:
            itog_room.GetParameters('ADSK_Коэффициент площади')[0].Set(koefBalkon)


    # Определение количества жилых комнат

    for apart_number in dict_aparts:
        apart_count_room = 0  # количество жилых комнат в квартире
        for apart_room in dict_aparts[apart_number]:
            if apart_room.GetParameters('ADSK_Тип помещения')[0].AsInteger() == 1:
                apart_count_room += 1
        dict_aparts_number[apart_number] = apart_count_room

    doc.Regenerate()
    t.Commit() # Закрытие транзакции

    # получение спецификации для извлечения значений

    room_schedule = [schedule for schedule in DB.FilteredElementCollector(doc).OfClass(DB.ViewSchedule)
                     if '(без Dynamo)_' + str(roundCount) + ' знак' in schedule.Name].pop()

    s_definition = room_schedule.Definition
    # получение табличных данных спецификации
    tabel_data = room_schedule.GetTableData()
    # получение одного раздела таблицы
    body_section_data = tabel_data.GetSectionData(DB.SectionType.Body)
    # получение диапазонов номеров строк таблицы
    row_numbers = list(range(
        body_section_data.FirstRowNumber,
        body_section_data.LastRowNumber + 1))
    # получение диапазонов номеров столбцов таблицы
    column_numbers = list(range(
        body_section_data.FirstColumnNumber,
        body_section_data.LastColumnNumber + 1))
    # получения текста всех ячеек раздела таблицы
    body_cells_text = {
        (row_number, column_number): room_schedule
        .GetCellText(
            DB.SectionType.Body,
            row_number,
            column_number
        )
        for row_number in row_numbers
        for column_number in column_numbers
    }

    t = DB.Transaction(doc, 'Квартирография') # Открытие транзакции
    t.Start()
    for row_number in row_numbers:
        apart_number = body_cells_text[row_number, 0]
        if apart_number in dict_aparts:
            for apart_room in dict_aparts[apart_number]:

                apart_room.GetParameters('ADSK_Количество комнат')[0].Set(dict_aparts_number[apart_number])

                apart_tip_room = apart_room.GetParameters('ADSK_Тип помещения')[0].AsInteger()
                apart_ind_room = apart_number + '_' + str(apart_tip_room)
                apart_room.GetParameters('ADSK_Индекс помещения')[0].Set(apart_ind_room)

                koef_room = apart_room.GetParameters('ADSK_Коэффициент площади')[0].AsDouble()
                area_room = round(DB.UnitUtils.ConvertFromInternalUnits(
                    apart_room.Area, DB.UnitTypeId.SquareMeters), roundCount)
                area_room_round = round(area_room * koef_room, roundCount)
                apart_room.GetParameters('ADSK_Площадь с коэффициентом')[0].Set(
                    DB.UnitUtils.ConvertToInternalUnits(area_room_round, DB.UnitTypeId.SquareMeters))

                for column_number in column_numbers:
                    if body_cells_text[0, column_number] == 'S жилая':
                        area = body_cells_text[row_number, column_number]  # жилая площадь квартиры
                        apart_room.GetParameters('ADSK_Площадь квартиры жилая')[0].Set(
                            DB.UnitUtils.ConvertToInternalUnits(float(area.replace(',', '.')),
                                                                DB.UnitTypeId.SquareMeters))
                    elif body_cells_text[0, column_number] == 'S квартиры':
                        area = body_cells_text[row_number, column_number]  # площадь квартиры
                        apart_room.GetParameters('ADSK_Площадь квартиры')[0].Set(
                            DB.UnitUtils.ConvertToInternalUnits(float(area.replace(',', '.')),
                                                                DB.UnitTypeId.SquareMeters))
                    elif body_cells_text[0, column_number] == 'S Общая':
                        area = body_cells_text[row_number, column_number]  # Площадь квартиры общая (с коэффициентом)
                        apart_room.GetParameters('ADSK_Площадь квартиры общая')[0].Set(
                            DB.UnitUtils.ConvertToInternalUnits(float(area.replace(',', '.')),
                                                                DB.UnitTypeId.SquareMeters))

    t.Commit()  # Закрытие транзакции