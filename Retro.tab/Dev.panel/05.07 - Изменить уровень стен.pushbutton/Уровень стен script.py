# -*- coding: utf-8 -*-
__title__ = "Изменить привязку стен"
__doc__ = """
_____________________________________________________________________
Описание:
Быстрый способ изменить привязку стен 

_____________________________________________________________________
Author: Erik Frits"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ==================================================
from Autodesk.Revit.DB import *
from pyrevit import forms
from Autodesk.Revit.UI.Selection import ObjectType, ISelectionFilter

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
class Walls_ISelectionFilter(ISelectionFilter):
    def AllowElement(self, element):
        if type(element) == Wall:
            return True


def get_selected_walls():
    # Получить текущий выбор пользователя и выбрать их него только стены
    sel_el_ids = uidoc.Selection.GetElementIds()
    sel_elems  = [doc.GetElement(el_id) for el_id in sel_el_ids]
    # Отфильтровать только стены
    sel_wall = [el for el in sel_elems if type(el) == Wall]

    # Если стены не были выбраны, то выбрать стены
    if not sel_wall:
        try:
            picked_ref = uidoc.Selection.PickObjects(ObjectType.Element,Walls_ISelectionFilter() )
            sel_wall = [doc.GetElement(ref) for ref in picked_ref]
        except:
            pass
    # Если стены все еще не выбраны, то остановить выполнение кода
    if not sel_wall:
        forms.alert('Стены не выбраны. Попробуйте еще раз', exitscript= True)

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
    components = [CheckBox('редактировать_основу', 'Редактировать основу:'),
                  ComboBox('Зависимость_снизу', dict_levels),

                  CheckBox('редактировать_верх', 'Редактировать верх :'),
                  ComboBox('Зависимость_сверху', dict_levels),

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

selected_walls = get_selected_walls()

# for wall in selected_walls:
#     wall_type      = wall.WallType
#     wall_type_name = Element.Name.GetValue(wall_type)
#     print(wall_type_name)



# Запросить информацию у пользователя
user_input = get_user_input()
new_base_level = user_input['Зависимость_снизу']
new_top_level  = user_input['Зависимость_сверху']
modify_base    = user_input['редактировать_основу']
modify_top     = user_input['редактировать_верх']

#Начало транзакции
t = Transaction(doc, "Изменить уровень элемента")
t.Start()


#Вычислить новое смещение для стен
for wall in selected_walls:
    try:
        #Проверить занят ли элемент кем-то еще
        checkoutStatus = WorksharingUtils.GetCheckoutStatus(doc,wall.Id)
        if checkoutStatus == CheckoutStatus.OwnedByOtherUser:
            print('[{}]Стена занята другим пользователем'.format(wall.Id))
            continue
        #Получить параметры
        p_base_level  = wall.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT)
        p_base_offset = wall.get_Parameter(BuiltInParameter.WALL_BASE_OFFSET)
        p_top_level   = wall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE)
        p_top_offset  = wall.get_Parameter(BuiltInParameter.WALL_TOP_OFFSET)
        p_wall_height = wall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM)

        # Значение параметров
        base_level  = doc.GetElement(p_base_level.AsElementId()) #type: Level
        base_offset = p_base_offset.AsDouble()
        wall_heigh  = p_wall_height.AsDouble()

        # Вычислить высотную отметку
        wall_base_elevation = base_level.Elevation + base_offset
        wall_top_elevation  = wall_base_elevation + wall_heigh

    #Редактировать Базовый и Верхний уровни/смещение
        if modify_base:
            new_offset    = wall_base_elevation - new_base_level.Elevation
            p_base_level.Set(new_base_level.Id)
            p_base_offset.Set(new_offset)

        if modify_top:
            new_offset    = wall_top_elevation - new_top_level.Elevation
            p_top_level.Set(new_top_level.Id)
            p_top_offset.Set(new_offset)
    except:
        import traceback
        print(traceback.format_exc(),wall.Id)

t.Commit()