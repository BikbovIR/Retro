# -*- coding: utf-8 -*-
__title__ = {
    "en_us": "Copy wall/floor info",
    "ru": "Копировать стены/перекрытия"
}
__doc__ = """Инструмент для копирования параметров стены/перекрытия из одного открытого проекта в другой
как работает:
1.Выбрать категорию стены или перекрытия
2.Выбрать тип стены/перекрытия которые надо скопировать
3.Выбрать параметр который надо скопировать
4.Инструмент скопирует выбранный параметр в такой же тип стены/перекрытие. Если выбранного типа нет в проекте, то тип будет полностью.

Ограничения:
- Инструмент не копирует геометрические настройки : Толщина, материал, структура
- Инструмент параметры с изображением
- Инструмент не может копировать нулевые значения. 

Автор: Бикбов Ильнур

"""
#-------------------------------------------------------------------------
# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#-------------------------------------------------------------------------
# Regular + Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import UIDocument
from rpw.ui.forms import SelectFromList, CommandLink, TaskDialog
from pyrevit import forms, script

import clr
clr.AddReference('System')
from System.Collections.Generic import List
#-------------------------------------------------------------------------
# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#-------------------------------------------------------------------------

doc   = __revit__.ActiveUIDocument.Document # type: Document
uidoc = __revit__.ActiveUIDocument          # type: UIDocument
app   = __revit__.Application               # type: Application

# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
#==================================================
def get_param_value(param):
    """Get a value from a Parameter based on its StorageType."""
    value = None
    if param.StorageType == StorageType.Double:
        value = param.AsDouble()
    elif param.StorageType == StorageType.ElementId:
        value = param.AsElementId()
    elif param.StorageType == StorageType.Integer:
        value = param.AsInteger()
    elif param.StorageType == StorageType.String:
        value = param.AsString()
    return value


#-------------------------------------------------------------------------
# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
#-------------------------------------------------------------------------
#What are we going to copy Wall or Floors
commands= [CommandLink('Стены', return_value='Walls'),
           CommandLink('Перекрытия', return_value='Floors')]

dialog = TaskDialog('Что хотите скопировать? ',
                 title_prefix= False,
                content="Выберите категорию",
                commands=commands,
                # verification_text='Add Verification Checkbox',
                # expanded_content='Add Expanded Content',
                show_close=True)
CategoryToCopy = dialog.show()
if not CategoryToCopy:
    forms.alert("Категория не выбрана \nпопробуйте еще раз", exitscript=True)


#Get all opened RVT files
docs    = app.Documents
DocsDic = {d.Title:d for d in docs}

# for d in DocsDic:
#     print(d)


#Get the file to copy from and to
CopyFromDoc = SelectFromList("Откуда копировать", DocsDic, description=None, sort=True, exit_on_close=True)
DocsDic.pop(CopyFromDoc.Title)
CopyToDoc = SelectFromList("Куда копировать", DocsDic, description=None, sort=True, exit_on_close=True)

# for d in DocsDic:
#     print(d)
# print("Откуда копировать {}".format(CopyFromDoc))
# print("Куда копировать {}".format(CopyToDoc))




if CategoryToCopy == 'Walls':
    #Get the walls to copy
    WallsFrom       = FilteredElementCollector(CopyFromDoc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsElementType().ToElements()
    dict_wallsFrom  = { w.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString(): w for w in WallsFrom}
    wallListFrom    = sorted([el for el in dict_wallsFrom.keys()])
    SelWallsFrom    = forms.SelectFromList.show(wallListFrom, button_name='Выбрать стены',multiselect = True, width=1000,height=1000)
    SelWallsFrom    = [dict_wallsFrom[w] for w in SelWallsFrom]

    if SelWallsFrom:
        #Get parameters to copy
        wallParameters  = SelWallsFrom[0].GetOrderedParameters()
        wallParameters_filtered  = [p for p in wallParameters if not p.IsReadOnly]
        wallParameters_filtered_2 = [p for p in wallParameters_filtered if not p.StorageType == StorageType.ElementId]

        dict_parameters = { p.Definition.Name: p for p in wallParameters_filtered_2 }
        ParList         = sorted([el for el in dict_parameters.keys()])
        SelParam        = forms.SelectFromList.show(ParList, button_name='Выбрать параметры',multiselect = True, width=800,height=900)
        SelParam        = [dict_parameters[p] for p in SelParam]
    else:
        forms.alert("Элементы не выбраны \nпопробуйте еще раз", exitscript=True)

    # for p in SelParam:
    #     print(p)
    #     print(p.StorageType)
    #     print(p.IsReadOnly)
    #     print('*'*10)



    #Match the walls to copy
    WallsTo         = FilteredElementCollector(CopyToDoc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsElementType().ToElements()
    dict_wallsTo    = { w.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString(): w for w in WallsTo}
    wallListTo      = sorted([el for el in dict_wallsTo.keys()])
    MatchedWalls    = [w for w in SelWallsFrom if w.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString() in wallListTo]
    UnMatchedWalls  = [w for w in SelWallsFrom if w.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString() not in wallListTo]

    UnMatchedWallsId = List[ElementId]()
    for wall in UnMatchedWalls:
        UnMatchedWallsId.Add(wall.Id)
    # for w in MatchedWalls:
    #     print(w.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString())


    # print('Selected parameters:')
    # for par in SelParam:
    #     print(get_param_value(par))
    # print('Selected Walls')

    copypasteoption = CopyPasteOptions()

    # with Transaction(CopyToDoc,"Копировать стены") as t:
    #     t.Start()
    #     ElementTransformUtils.CopyElements(CopyFromDoc, UnMatchedWallsId, CopyToDoc, None, copypasteoption)
    #     t.Commit()

    with Transaction(CopyToDoc, 'параметры стен изменены') as t:
        t.Start()
        if UnMatchedWallsId:
            CopiedWalls = []
            ElementTransformUtils.CopyElements(CopyFromDoc, UnMatchedWallsId, CopyToDoc, None, copypasteoption)
            for wall in UnMatchedWalls:
                CopiedWalls.append([wall.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM),True])
            output = script.get_output()
            output.print_table(table_data=CopiedWalls,
                               title="Скопированные стены",
                               columns=["Тип стены", "Результат"],
                               formats=['', ''])


        for wall in MatchedWalls:
            result = []
            WallName = wall.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
            # print('Тип изменяемой стены: {}'.format(WallName))
            if WallName in dict_wallsTo.keys():
                WallCopyTo = dict_wallsTo[WallName]
                for par in SelParam:
                    parName = par.Definition.Name
                    parCopyTo = WallCopyTo.LookupParameter(parName)
                    try:
                        parCopyTo.Set(get_param_value(par))
                        # print('"{}" был скопирован. Значение "{}" задано'.format(parName, get_param_value(par)))
                        result.append([parName,True,get_param_value(par),])
                    except:
                        # print('"{}" НЕ СКОПИРОВАН. Возможно параметр пустой'.format(parName,get_param_value(par)))
                        result.append([parName,False ,get_param_value(par)])

            output = script.get_output()
            output.print_table(table_data=result,
                               title="Измененная стена: {}".format(WallName),
                               columns=["Имя параметра", "Результат","Копируемое значение"],
                               formats=['', '', ''])

        t.Commit()

if CategoryToCopy == 'Floors':
    # Get the Floors to copy
    FloorsFrom = FilteredElementCollector(CopyFromDoc).OfCategory(
        BuiltInCategory.OST_Floors).WhereElementIsElementType().ToElements()
    dict_FloorsFrom = {w.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString(): w for w in FloorsFrom}
    FloorsListFrom = sorted([el for el in dict_FloorsFrom.keys()])
    SelFloorsFrom = forms.SelectFromList.show(FloorsListFrom, button_name='Выбрать перекрытия', multiselect=True, width=1000,
                                             height=1000)
    SelFloorsFrom = [dict_FloorsFrom[w] for w in SelFloorsFrom]

    if SelFloorsFrom:
        # Get parameters to copy
        FloorsParameters = SelFloorsFrom[0].GetOrderedParameters()
        FloorsParameters_filtered = [p for p in FloorsParameters if not p.IsReadOnly]
        FloorsParameters_filtered_2 = [p for p in FloorsParameters_filtered if not p.StorageType == StorageType.ElementId]

        dict_parameters = {p.Definition.Name: p for p in FloorsParameters_filtered_2}
        ParList = sorted([el for el in dict_parameters.keys()])
        SelParam = forms.SelectFromList.show(ParList, button_name='Выбрать параметры', multiselect=True, width=800,
                                             height=900)
        SelParam = [dict_parameters[p] for p in SelParam]
    else:
        forms.alert("Элементы не выбраны \nпопробуйте еще раз", exitscript=True)

    # for p in SelParam:
    #     print(p)
    #     print(p.StorageType)
    #     print(p.IsReadOnly)
    #     print('*'*10)

    # Match the walls to copy
    FloorsTo = FilteredElementCollector(CopyToDoc).OfCategory(
        BuiltInCategory.OST_Floors).WhereElementIsElementType().ToElements()
    dict_FloorsTo = {f.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString(): f for f in FloorsTo}
    FloorsListTo = sorted([el for el in dict_FloorsTo.keys()])
    MatchedFloors = [f for f in SelFloorsFrom if
                    f.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString() in FloorsListTo]
    UnMatchedFloors = [f for f in SelFloorsFrom if
                      f.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString() not in FloorsListTo]

    UnMatchedFloorsId = List[ElementId]()
    for floor in UnMatchedFloors:
        UnMatchedFloorsId.Add(floor.Id)
    # for w in MatchedWalls:
    #     print(w.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString())

    # print('Selected parameters:')
    # for par in SelParam:
    #     print(get_param_value(par))
    # print('Selected Walls')

    copypasteoption = CopyPasteOptions()

    # with Transaction(CopyToDoc,"Копировать стены") as t:
    #     t.Start()
    #     ElementTransformUtils.CopyElements(CopyFromDoc, UnMatchedWallsId, CopyToDoc, None, copypasteoption)
    #     t.Commit()

    with Transaction(CopyToDoc, 'параметры перекрытий изменены') as t:
        t.Start()
        if UnMatchedFloorsId:
            CopiedFloors = []
            ElementTransformUtils.CopyElements(CopyFromDoc, UnMatchedFloorsId, CopyToDoc, None, copypasteoption)
            for floor in UnMatchedFloors:
                CopiedFloors.append([floor.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM), True])
            output = script.get_output()
            output.print_table(table_data=CopiedFloors,
                               title="Скопированные перекрытия",
                               columns=["Тип перекрытия", "Результат"],
                               formats=['', ''])

        for floor in MatchedFloors:
            result = []
            FloorName = floor.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
            # print('Тип изменяемой стены: {}'.format(WallName))
            if FloorName in dict_FloorsTo.keys():
                FloorsCopyTo = dict_FloorsTo[FloorName]
                for par in SelParam:
                    parName = par.Definition.Name
                    parCopyTo = FloorsCopyTo.LookupParameter(parName)
                    try:
                        parCopyTo.Set(get_param_value(par))
                        # print('"{}" был скопирован. Значение "{}" задано'.format(parName, get_param_value(par)))
                        result.append([parName, True, get_param_value(par), ])
                    except:
                        # print('"{}" НЕ СКОПИРОВАН. Возможно параметр пустой'.format(parName,get_param_value(par)))
                        result.append([parName, False, get_param_value(par)])

            output = script.get_output()
            output.print_table(table_data=result,
                               title="Измененное перекрытие: {}".format(FloorName),
                               columns=["Имя параметра", "Результат", "Копируемое значение"],
                               formats=['', '', ''])

        t.Commit()