# -*- coding: utf-8 -*-
__title__   = {
    "en_us": "ADSK_Этаж",
    "ru": "ADSK_Этаж"
}
__doc__     = """Version = 1.0
Date    = 02.09.2025
________________________________________________________________
Заполнить параметр ADSK_Этаж для стен исходя из имени уровня

Если уровень назван "АР_01_+0.000", то стене на этом уровне будет присвоен ADSK_Этаж - "01"

Принцип работы:
1. Смотрит диапазон высотных отметок уровня. 
2. Смотрит уровень середины элемента
3. Соотносит середину элемента и уровни. В соответствии с этим выставляет ADSK_Этаж
(1,2,3...)

________
Last Updates:
- [05.09.2025] v1.0 Button was made
________________________________________________________________
Author: Ilnur Bikbov"""

import Autodesk.Revit.DB
# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝
#==================================================
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import  Selection
from pyrevit import forms, script




# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
#==================================================
app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document
selection = uidoc.Selection #type:Selection


# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
#==================================================
def ChekIfOwned(el,doc):
    checkOutStatus = WorksharingUtils.GetCheckoutStatus(doc,el.Id)
    if checkOutStatus == CheckoutStatus.OwnedByOtherUser:
        return False
    else:
        return True

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
#==================================================

# Select all levels
levels = FilteredElementCollector(doc).OfClass(Level).WhereElementIsNotElementType().ToElements()
dict_levels = sorted([{level.Elevation: [level]} for level in levels])

# add the range to levels
n = 1
l = len(dict_levels)
for d_l in dict_levels:
    Splitted_Name = d_l.values()[0][0].Name.split('_')[1]
    # print(Splitted_Name)
    if n == 1:
        minimumValue = -1000000
        maximumValue = dict_levels[n].keys()[0]
    elif n < l:
        minimumValue = d_l.keys()[0]
        maximumValue = dict_levels[n].keys()[0]
    else:
        minimumValue = d_l.keys()[0]
        maximumValue = 1000000
    d_l[d_l.keys()[0]].extend([minimumValue,maximumValue,Splitted_Name])
    n += 1


#get all elements
AllWalls   = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
AllWindows = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows).WhereElementIsNotElementType().ToElements()
AllDoors   = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()
AllFloors  = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsNotElementType().ToElements()
AllRooms   = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()

#get dictionary that user can select
dic_options = {'Стены':AllWalls,'Окна':AllWindows,'Двери':AllDoors,'Перекрытия':AllFloors,'Помещения':AllRooms}
options = ['Стены','Окна','Двери','Перекрытия','Помещения']


res = forms.SelectFromList.show(options,
                                multiselect=True,
                                title='Куда заполнить ADSK_Этаж',
                                group_selector_title='Sheet Sets',
                                button_name='Жмяк')
#check if user selected anything
el_to_set_par = []
for cat in res:
    el_to_set_par.extend(dic_options[cat])

if el_to_set_par:
    pass
else:
    forms.alert("Не выбраны элементы \nпопробуйте еще раз", exitscript=True)

#lists for unchanged elements
intact_elements = []
elem_notOwned   = []
#variable for counting changes
changes = 0
#Transaction
with Transaction(doc,'PyRevit заполнил параметр "ADSK_Этаж"') as t:
    t.Start()
    for element in el_to_set_par:
        BBox = element.get_BoundingBox(None)
        MiddlePoint = (BBox.Max.Z+BBox.Min.Z)/2
        element_ADSK_level_p = element.LookupParameter("ADSK_Этаж")
        for level in dict_levels:
            l_MIN  = level.values()[0][1]
            l_MAX  = level.values()[0][2]
            l_Name = level.values()[0][3]
            if MiddlePoint > l_MIN:
                if MiddlePoint < l_MAX:
                    if ChekIfOwned(element,doc):
                        try:
                            element_ADSK_level_p.Set(l_Name)
                            changes += 1
                        except:
                            intact_elements.append(element)
                            # print('DID NOT SET_element {}_id: {}_ on {} level'.format(element.Name,element.Id, l_Name))
                    else:
                        elem_notOwned.append(element)
                        # print('Element is not Owned by user: {}_id: {}_ on {} level'.format(element.Name, element.Id, l_Name))
    t.Commit()

#Show to the user what elements wasn't changed
if intact_elements:
    print('Элементам ниже не были заданы параметры:')
    for elem in intact_elements:
        elem_linkify = script.get_output().linkify(elem.Id,elem.Name)
        print(elem_linkify)
if elem_notOwned:
    print('Вы не владеете элементами ниже. Поэтому параметры не заданы:')
    for elem in elem_notOwned:
        elem_linkify = script.get_output().linkify(elem.Id,elem.Name)
        print(elem_linkify)
if intact_elements or elem_notOwned:
    print("Для остальных {} элементов параметр ADSK_Этаж был заполнен".format(changes))
else:
    print("Параметр ADSK_Этаж был заполнен для {} элементов".format(changes))
