# -*- coding: utf-8 -*-
__title__ = "Узнать соотношение квартир к общей площади"
__doc__   = """Version = 1.0
----------------------------------------------------------------
Эту кнопку спросил Паша
Apartment = round(Apartment,2)
MOP = round(MOP,2)
SUM = round(Apartment+MOP,2)
percentage = round(Apartment/SUM,2)
----------------------------------------------------------------
Author = Bikbov Ilnur"""

#Import
from Autodesk.Revit.DB import *
from pyrevit import forms
#Variables
app     = __revit__.Application
uidoc   = __revit__.ActiveUIDocument
doc     = __revit__.ActiveUIDocument.Document

par_apartment = 'Квартира'
par_MOP = 'МОП, ШАХТЫ'
#MAIN
#Указать параметры по умолчанию

par_apartment = forms.ask_for_string(
    default= par_apartment,
    prompt='Введите параметр по которому находятся квартиры:',
    title='Квартиры '
)
par_MOP =  forms.ask_for_string(
    default= par_MOP,
    prompt='Введите параметр по которому находятся МОПы:',
    title='Квартиры '
)

#Найти все помещения
AllRooms = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()
Apartment = 0
MOP = 0
for room in AllRooms:
    RoomType = room.get_Parameter(BuiltInParameter.ROOM_DEPARTMENT).AsString()
    Area_ft  = room.Area
    Area_sqm = UnitUtils.ConvertFromInternalUnits(room.Area, UnitTypeId.SquareMeters)
    if RoomType == par_apartment:
        Apartment += Area_sqm
    elif RoomType == par_MOP:
        MOP += Area_sqm
Apartment = round(Apartment,2)
MOP = round(MOP,2)
SUM = round(Apartment+MOP,2)
percentage = round(Apartment/SUM,2)
print("Площадь квартир: {}        ".format(Apartment))
print("Площадь МОП: {}        ".format(MOP))
print("Площадь квартир и МОП: {}        ".format(SUM))
print("Процент квартир: {}        ".format(Apartment))
