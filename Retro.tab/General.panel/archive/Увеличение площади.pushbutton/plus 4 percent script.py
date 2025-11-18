# -*- coding: utf-8 -*-
__title__ = "Увеличение площади"
__doc__ = """
Date = 08.08.2025
_________________________________________________________________
Увеличивает площадь на определенный коэфициент и записывает в 
- ADSK_Площадь с коэффициентом 
- ADSK_Коэффициент площади
_________________________________________________________________
Округление площадей до 2 знаков после запятой

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

p_name_koef          = 'ADSK_Коэффициент площади'     #- Коэффициент площади
p_name_AreaWithKoef  = 'ADSK_Площадь с коэффициентом' #- Площадь помещения с коэффициентом


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
# ==================================================

# 1. Get All Rooms
all_rooms = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).ToElements()
#Получить коэфициент


Room_Koef =  forms.ask_for_string(
    default='1.04',
    prompt='Введите нужный коэфициент увеличения площади',
    title='Коэффициент'
)

try:
    Room_Koef = float(Room_Koef)
except:
    forms.alert("Что-то не получилось свяжитесь с бимщиком", exitscript=True)



# #❗ Check the unplaced areas
for room in all_rooms:
    if room.Location == None:
        print(
            ":clown_face: :clown_face: :clown_face: В проекте имеются не размещенные. Удалите их и попробуйте еще раз. :clown_face: :clown_face: :clown_face:")
        sys.exit()
    elif not (room.Area > 0):
        print(
            ":clown_face: :clown_face: :clown_face: В проекте имеются излишние или не окруженные помещения. Удалите их и попробуйте еще раз. :clown_face: :clown_face: :clown_face:")
        sys.exit()

# 2. Увеличить площадь на коэффициент
t = Transaction(doc, 'Увеличить площадь на коэфициент')
t.Start()
for room in all_rooms:
    try:
        # Получить параметр площади
        room_area_m2 = UnitUtils.ConvertFromInternalUnits(room.Area, UnitTypeId.SquareMeters)
        p_koef = room.LookupParameter(p_name_koef)
        p_AreaWithKoef = room.LookupParameter(p_name_AreaWithKoef)

        # Получить значения
        AreaWithKoef_m2 = round(room_area_m2 * Room_Koef, 2)
        AreaWithKoef_ft = UnitUtils.ConvertToInternalUnits(AreaWithKoef_m2, UnitTypeId.SquareMeters)

        # Задать значения
        p_koef.Set(Room_Koef)
        p_AreaWithKoef.Set(AreaWithKoef_ft)

    except:
        forms.alert("Что-то не получилось свяжитесь с бимщиком", exitscript=True)
print("Готово")
t.Commit()