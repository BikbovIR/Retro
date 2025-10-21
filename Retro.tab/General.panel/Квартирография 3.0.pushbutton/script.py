# -*- coding: utf-8 -*-
__title__ = "Квартирография 3.0"
__doc__ = """
Date = 21.10.2025
_________________________________________________________________
Перед началом работы задайте значения параметров: 
ADSK_Тип помещения
ADSK_Номер квартиры

Заполняет параметры:
ADSK_Площадь квартиры
ADSK_Площадь квартиры общая
ADSK_Площадь квартиры жилая
ADSK_Количество комнат
ADSK_Коэффициент площади
ADSK_Площадь с коэффициентом
ADSK_Индекс помещения
RETRO_Площадь квартиры общая без коэф
_________________________________________________________________
Округление площадей до 2 знаков после запятой

Типы помещений:
"1" - жилое   коэффициент - 1
"2" - нежилое коэффициент - 1
"3" - лоджия  коэффициент - 0.5
"4" - балкон  коэффициент - 0.3
"5" - общее   коэффициент - 1
_________________________________________________________________
Author: Bikbov Ilnur"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ==================================================
from Autodesk.Revit.DB import *
from pyrevit import forms

import sys

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# ==================================================
doc   = __revit__.ActiveUIDocument.Document #type: Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# Global Variables
p_name_room_sorting     = 'ADSK_Номер квартиры'
p_name_room_type        = 'ADSK_Тип помещения'

p_name_LivingRoom               = 'ADSK_Площадь квартиры жилая'                 #- Сумма жилых помещений квартиры
p_name_ApartmentArea            = 'ADSK_Площадь квартиры'                       #- Сумма отапливаемых помещений квартиры
p_name_TotalArea                = 'ADSK_Площадь квартиры общая'                 #- Сумма всех помещений квартиры с коэффициентом
p_name_NumberOfRooms            = 'ADSK_Количество комнат'                      #- Количество комнат
p_name_koef                     = 'ADSK_Коэффициент площади'                    #- Коэффициент площади
p_name_AreaWithKoef             = 'ADSK_Площадь с коэффициентом'                #- Площадь помещения с коэффициентом
p_name_RoomIndex                = 'ADSK_Индекс помещения'                       #- Индекс помещения (Номер квартиры+Тип помещения)
p_name_TotalAreaWithoutKoef     = 'RETRO_Площадь квартиры общая без коэф'       #- Сумма всех помещений без коэффициента

koef_balkony = 0.3
koef_loggia  = 0.5
# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
# ==================================================

# 1. Get All Rooms
all_rooms = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).ToElements()

# #❗ Check the unplaced areas
for room in all_rooms:
    if room.Location == None:
        print(":clown_face: :clown_face: :clown_face: В проекте имеются не размещенные. Удалите их и попробуйте еще раз. :clown_face: :clown_face: :clown_face:")
        sys.exit()
    elif not(room.Area >0) :
        print(":clown_face: :clown_face: :clown_face: В проекте имеются излишние или не окруженные помещения. Удалите их и попробуйте еще раз. :clown_face: :clown_face: :clown_face:")
        sys.exit()

# 2. Sort By Apartment Number
from collections import defaultdict
dict_rooms = defaultdict(list)

for room in all_rooms:
    try:
        apartment_num = room.LookupParameter(p_name_room_sorting).AsString()
        if apartment_num:
            dict_rooms[apartment_num].append(room)
    except:
        forms.alert("Не получилось считать параметр {}. Проверьте его наличие.".format(p_name_room_sorting), exitscript=True)

# # Check Dictionary
# for k,v in dict_rooms.items():
#     print(k,v)

t = Transaction(doc, 'Sum Apartments')
t.Start()

for apartment_num, rooms in dict_rooms.items():
    sum_LivingRoom_m2           = 0 #- Сумма жилых помещений квартиры
    sum_ApartmentArea_m2        = 0 #- Сумма отапливаемых помещений квартиры
    sum_TotalArea_m2            = 0 #- Сумма всех помещений квартиры с коэффициентом
    NumberOfRooms               = 0 #- Количество комнат
    sum_TotalAreaWithoutKoef_m2 = 0 #- Сумма всех помещений без коэффициента


    # 3. Sum Apartment Area
    for room in rooms:
        room_type       = room.LookupParameter(p_name_room_type).AsInteger()
        room_area_m2    = UnitUtils.ConvertFromInternalUnits(room.Area, UnitTypeId.SquareMeters)
        room_area_m2    = round(room_area_m2, 2)

        Room_Koef       = koef_loggia if room_type == 3 else (koef_balkony if room_type == 4 else 1)
        AreaWithKoef_m2 = round(room_area_m2*Room_Koef,2)
        RoomIndex       = str(apartment_num) + '_' + str(room_type)
        sum_TotalAreaWithoutKoef_m2 += room_area_m2

        if room_type == 1:
            # sum_LivingRoom_ft += room.Area
            sum_LivingRoom_m2    += AreaWithKoef_m2
            sum_ApartmentArea_m2 += AreaWithKoef_m2
            sum_TotalArea_m2     += AreaWithKoef_m2
            NumberOfRooms        += 1
        elif room_type == 2:
            # sum_TotalArea_ft += room.Area
            sum_ApartmentArea_m2 += AreaWithKoef_m2
            sum_TotalArea_m2     += AreaWithKoef_m2
        elif room_type == 3:
            # sum_TotalArea_ft   += room.Area
            sum_TotalArea_m2     += AreaWithKoef_m2
        elif room_type == 4:
            # sum_TotalArea_ft   += room.Area
            sum_TotalArea_m2     += AreaWithKoef_m2
        elif room_type == 5:
            # sum_TotalArea_ft   += room.Area
            sum_TotalArea_m2     += AreaWithKoef_m2

        AreaWithKoef_ft = UnitUtils.ConvertToInternalUnits(AreaWithKoef_m2, UnitTypeId.SquareMeters)
        try:
            p_koef = room.LookupParameter(p_name_koef)
            p_AreaWithKoef = room.LookupParameter(p_name_AreaWithKoef)
            p_RoomIndex = room.LookupParameter(p_name_RoomIndex)

            p_koef.Set(Room_Koef)
            p_AreaWithKoef.Set(AreaWithKoef_ft)
            p_RoomIndex.Set(RoomIndex)

        except:
            forms.alert("Не нашел какие-то параметры. проверьте их наличие всех параметров", exitscript=True)
    # Preview Results
    print('Номер квартиры: {}'.format(apartment_num))
    print('Количество комнат: {}'.format(NumberOfRooms))
    print('Жилая площадь квартиры: {}'.format(sum_LivingRoom_m2))
    print('Общая площадь квартиры: {}'.format(sum_TotalArea_m2))
    print('Общая площадь квартиры без коэф.: {}'.format(sum_TotalAreaWithoutKoef_m2))
    print('---')
    # Converting M2 to FT
    sum_LivingRoom_ft           = UnitUtils.ConvertToInternalUnits(sum_LivingRoom_m2,          UnitTypeId.SquareMeters)
    sum_ApartmentArea_ft        = UnitUtils.ConvertToInternalUnits(sum_ApartmentArea_m2,       UnitTypeId.SquareMeters)
    sum_TotalArea_ft            = UnitUtils.ConvertToInternalUnits(sum_TotalArea_m2,           UnitTypeId.SquareMeters)
    sum_TotalAreaWithoutKoef_ft = UnitUtils.ConvertToInternalUnits(sum_TotalAreaWithoutKoef_m2,UnitTypeId.SquareMeters)


    # 4. Write Results to Output Parameter
    for room in rooms:
        try:
            p_LivingRoom           = room.LookupParameter(p_name_LivingRoom)
            P_ApartmentArea        = room.LookupParameter(p_name_ApartmentArea)
            p_TotalArea            = room.LookupParameter(p_name_TotalArea)
            p_NumberOfRooms        = room.LookupParameter(p_name_NumberOfRooms)
            p_TotalAreaWithoutKoef = room.LookupParameter(p_name_TotalAreaWithoutKoef)

            p_LivingRoom.Set(sum_LivingRoom_ft)
            P_ApartmentArea.Set(sum_ApartmentArea_ft)
            p_TotalArea.Set(sum_TotalArea_ft)
            p_NumberOfRooms.Set(NumberOfRooms)
            p_TotalAreaWithoutKoef.Set(sum_TotalAreaWithoutKoef_ft)

        except:
            forms.alert("Не нашел какие-то параметры. проверьте их наличие всех параметров", exitscript=True)
t.Commit()