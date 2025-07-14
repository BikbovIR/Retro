# -*- coding: utf-8 -*-
__title__ = "Cleaning model"
__doc__   = """Version = 1.0
----------------------------------------------------------------
Description =
Learn how to create reusable code with pyRevit
----------------------------------------------------------------
Author = Erik Frits"""

#Import
from Autodesk.Revit.DB import *
from pyrevit import forms
#Variables
app     = __revit__.Application
uidoc   = __revit__.ActiveUIDocument
doc     = __revit__.ActiveUIDocument.Document

LoadBearingNames = ['Несущ','Монолит']
WorkingName = 'Т_АР_'
#MAIN
#Проверить отсоединен ли файл от хранилища
if doc.IsWorkshared:
    forms.alert('Модель должна быть отсоединена от файла хранилища', exitscript=True)

# Найти все виды в модели
all_views = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).WhereElementIsNotElementType().ToElements()
#Отфильтровать из всех видов рабочие виды
WorkingViews = []
ViewForDeleting = []
for view in all_views:
    if view.Name.__contains__(WorkingName):
        WorkingViews.append(view)
    else:
        ViewForDeleting.append(view)

# for view in WorkingViews:
#     print(view.Name)
#
# print('*' * 20 + ' Удаляем эти виды ' + '*' * 20)
# for view in ViewForDeleting:
#     print(view.Name)
AllSheets = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
SheetsToDelete = [sheet for sheet in AllSheets if sheet.Name != 'Начальный вид']


#Найти все помещения
AllRooms = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()


#Найти все типы стен и отфильтровать все кроме монолитных
AllWalls     = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsElementType().ToElements()
WallToDelete = []

for wall in AllWalls:
    modelGroup = str(wall.get_Parameter(BuiltInParameter.ALL_MODEL_MODEL).AsString()).lower()
    LoadBearingWall = any(name.lower() in modelGroup for name in LoadBearingNames)

    if str(wall.Kind) == 'Curtain':
        pass
    elif LoadBearingWall:
        pass
    else:
        WallToDelete.append(wall)

# print('-----Эти стены будем удалять------')
# for dwall in WallToDelete:
#     print(dwall.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString())

#Найти все типы перекрытий и отфильтровать все кроме монолитных
AllFloors = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsElementType().ToElements()
FloorsToDelete = []
for floor in AllFloors:
    modelGroup = str(floor.get_Parameter(BuiltInParameter.ALL_MODEL_MODEL).AsString()).lower()
    LoadBearinFloor = any(name.lower() in modelGroup for name in LoadBearingNames)
    if LoadBearinFloor:
        pass
    else:
        FloorsToDelete.append(floor)
# print('-----Эти перекрытия будем удалять------')
# for dfloor in FloorsToDelete:
#     print(dfloor.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString())



# #Варианты удаления

t = Transaction(doc,'PyRevit очищаем модель для закачика')
t.Start()

items = ['Удалить виды', 'Удалить листы', 'Удалить помещения','Удалить не несущие перекрытия', 'Удалить не несущие стены' ]
res = forms.SelectFromList.show(items, button_name='Удалить выбранное', multiselect=True)
if not res:  # пользователь ничего не выбрал или нажал Отмена
    t.RollBack()
    print("Ничего не выбрано")
else:
    if  'Удалить виды' in res:
        for view in ViewForDeleting:
            doc.Delete(view.Id)
        print("Удалены не рабочие виды")
    if 'Удалить листы' in res:
        for sheet in SheetsToDelete:
            doc.Delete(sheet.Id)
        print("Удалены листы")
    if 'Удалить помещения' in res:
        for room in AllRooms:
            doc.Delete(room.Id)
        print("Удалены помещения")
    if 'Удалить не несущие перекрытия' in res:
        for floor in FloorsToDelete:
            doc.Delete(floor.Id)
        print("Удалены не несущие перекрытия")
    if 'Удалить не несущие стены' in res:
        for wall in WallToDelete:
            doc.Delete(wall.Id)
        print("Удалены не несущие стены")

    t.Commit()