# -*- coding: utf-8 -*-

__title__ = "Windows extend Rooms"
__doc__ = """
Date = 10.09.2026
_________________________________________________________________
Добавляет площадь площадь вырезания окна в площадь помещения
Параметр окна      - 'Площадь вырезания стены'
Параметр помещения - 'RETRO_Площадь помещения'

_________________________________________________________________
Author: Bikbov Ilnur"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ==================================================
from Autodesk.Revit.DB import *
from pyrevit import forms
from room_area_report import show_room_area_report
import sys

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# ==================================================
doc   = __revit__.ActiveUIDocument.Document #type: Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# Global Variables
p_name_window_area              = 'Площадь вырезания стены'                     # Параметр окна показывает площадь вырезания из стены
p_name_RetroArea                = 'RETRO_Площадь помещения'                     #- Параметр площади если надо складывать параметр площади в спеке
phase = doc.Phases[doc.Phases.Size - 1]
#Functions

#Получить площадь -> перевести в метрическую систему -> округлить до 2 десятых -> перевести в футы
def RoundingFunction(area):
    room_area_m2 = UnitUtils.ConvertFromInternalUnits(area, UnitTypeId.SquareMeters)
    room_area_m2_rounded = round(room_area_m2, 2)
    room_area_ft = UnitUtils.ConvertToInternalUnits(room_area_m2_rounded, UnitTypeId.SquareMeters)
    return room_area_ft

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
# ==================================================


# 1. Получить все помещения
all_rooms = (FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements())

# 2. Создать словарь: ID помещения → сумма площадей окон
rooms_dict = {}

for room in all_rooms:
    rooms_dict[room.Id.IntegerValue] = room.Area

# 3. Получить экземпляры окон
all_windows = (FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows).WhereElementIsNotElementType().ToElements())

# 4. Суммировать площади окон по помещениям
for window in all_windows:
    if window.FacingFlipped: #Если параметр True то получить значение "в комнату", если False то "из комнаты"
        room = window.get_FromRoom(phase)
    else:
        room = window.get_ToRoom(phase)

    if room is None: #Проверка наличие комнаты
        continue

    room_id = room.Id.IntegerValue

    # Получить параметр экземпляра
    window_instance_par = window.LookupParameter(p_name_window_area)

    if window_instance_par is None or not window_instance_par.HasValue: #Проверка наличия параметра вырезания площади
        print(u"Окно {}: параметр площади отсутствует или пуст".format(window.Id.IntegerValue))
        continue

    # Получить значение параметра и прибавить к сумме
    window_area = window_instance_par.AsDouble()
    rooms_dict[room_id] += window_area

#5 Округлить значения до 2 десятых
for room in all_rooms:
    room_id = room.Id.IntegerValue
    # print("Было: {}ft").format(rooms_dict[room_id])
    rooms_dict[room_id] = RoundingFunction (rooms_dict[room_id])
    # print("Стало: {}ft").format(rooms_dict[room_id])

# #Внести изменения в ревит
t = Transaction(doc, "Window areas add to Rooms")
t.Start()

try:
    for room in all_rooms:
        room_id = room.Id.IntegerValue
        room_parameter = room.LookupParameter(p_name_RetroArea)

        if room_parameter is None:
            raise Exception("У помещения {} не найден параметр '{}'.".format(room.Number, p_name_RetroArea))

        room_parameter.Set(rooms_dict[room_id])

    t.Commit()

except Exception as error:
    if t.GetStatus() == TransactionStatus.Started:
        t.RollBack()

    forms.alert(u"Ошибка записи:\n{}".format(error))


# 5. Напечатать результат
if t.GetStatus() == TransactionStatus.Committed:
    show_room_area_report(all_rooms, p_name_RetroArea)

# for room_id, area in rooms_dict.items():
#     room_area_m2 = UnitUtils.ConvertFromInternalUnits(area, UnitTypeId.SquareMeters)
#     print("ID помещения: {} | Площадь c вырезанием окон: {} м²".format(room_id, room_area_m2))
