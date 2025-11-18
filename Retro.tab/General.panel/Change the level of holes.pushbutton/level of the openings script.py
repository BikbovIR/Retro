# -*- coding: utf-8 -*-
__title__ = "Изменить привязку отверстий"
__doc__ = """
_____________________________________________________________________
Описание:
Быстрый способ изменить привязку отверстий 

_____________________________________________________________________
"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ==================================================
from Autodesk.Revit.DB import *
from pyrevit import forms
from Autodesk.Revit.UI.Selection import ObjectType, ISelectionFilter, Selection


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# ==================================================
doc   = __revit__.ActiveUIDocument.Document #type: Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
# ==================================================
class opening_ISelectionFilter(ISelectionFilter):
    def AllowElement(self, element):
        if element.Category.BuiltInCategory == BuiltInCategory.OST_GenericModel:
                return True


def get_selected_genericForm():
    # Получить текущий выбор пользователя и выбрать их него только отверстия
    sel_el_ids = uidoc.Selection.GetElementIds()
    sel_elems  = [doc.GetElement(el_id) for el_id in sel_el_ids]
    # Отфильтровать только отверстия
    sel_wall = [el for el in sel_elems if type(el) == GenericForm]

    # Если стены не были выбраны, то выбрать стены
    if not sel_wall:
        try:
            picked_ref = uidoc.Selection.PickObjects(ObjectType.Element,opening_ISelectionFilter() )
            sel_wall = [doc.GetElement(ref) for ref in picked_ref]
        except:
            pass
    # Если стены все еще не выбраны, то остановить выполнение кода
    if not sel_wall:
        forms.alert('Обобщенные модели не выбраны. Попробуйте еще раз', exitscript= True)

    return sel_wall

def get_user_input():
    """Функция для получения пользовательского ввода

    :return: Словарь выбранных элементов
    dict_keys = 'Редактировать основу' | 'редактировать основу' | 'Редактировать верх' | 'редактировать верх'
    """
    # Получить все уровни
    all_levels = FilteredElementCollector(doc).OfClass(Level).ToElements()
    dict_levels = {lvl.Name : lvl for lvl in all_levels }
    from rpw.ui.forms import (FlexForm, Label, ComboBox, TextBox, TextBox,
                              Separator, Button, CheckBox)
    components = [ComboBox('Привязка', dict_levels),

                  Separator(),
                  Button('жмяк')]
    form = FlexForm(__title__, components)
    form.show()

    values = form.values
    if not form.values:
        forms.alert("Уровни не выбраны \nпопробуйте еще раз", exitscript=True)
    return values

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ Main
# ==================================================
# Выбрать стены

selected_GenericModels = get_selected_genericForm()


# Запросить информацию у пользователя
user_input = get_user_input()
new_level = user_input['Привязка']

#Начало транзакции
t = Transaction(doc, "Изменить уровень элемента")
t.Start()


#Вычислить новое смещение для стен
for GenericModel in selected_GenericModels:
    try:
        #Проверить занят ли элемент кем-то еще
        checkoutStatus = WorksharingUtils.GetCheckoutStatus(doc,GenericModel.Id)
        if checkoutStatus == CheckoutStatus.OwnedByOtherUser:
            print('[{}]Элемент занят другим пользователем'.format(GenericModel.Id))
            continue
        #Получить параметры
        p_base_level  = GenericModel.get_Parameter(BuiltInParameter.FAMILY_LEVEL_PARAM)
        p_base_offset = GenericModel.get_Parameter(BuiltInParameter.INSTANCE_FREE_HOST_OFFSET_PARAM)
        # Значение параметров
        base_level  = doc.GetElement(p_base_level.AsElementId()) #type: Level
        base_offset = p_base_offset.AsDouble()

        # Вычислить высотную отметку
        GenericModel_base_elevation = base_level.Elevation + base_offset


    #Редактировать уровень/смещение
        new_offset    = GenericModel_base_elevation - new_level.Elevation
        p_base_level.Set(new_level.Id)
        p_base_offset.Set(new_offset)

    except:
        import traceback
        print(traceback.format_exc(),GenericModel.Id)

t.Commit()