# -*- coding: utf-8 -*-

__title__ = "Windows extend Rooms"
__doc__ = u"""
Date = 23.09.2026
_________________________________________________________________
Добавляет площадь вырезания окна в площадь помещения.
Параметр окна      - 'Площадь вырезания стены'
Параметр помещения - 'RETRO_Площадь помещения'

ИЗМЕНЕНО [11] 24.09.2026: сводка, ошибки и таблица объединены в одном окне.
ИЗМЕНЕНО [12] 24.09.2026: пустой результат также показывается в этом окне.

_________________________________________________________________
Author: Bikbov Ilnur"""


# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ==================================================
from Autodesk.Revit.DB import *
from pyrevit import forms
from room_area_report import show_room_area_report
# ИЗМЕНЕНО [02]: проверка недопустимых числовых значений перед расчётом.
import math

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# ==================================================
doc   = __revit__.ActiveUIDocument.Document #type: Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# Global Variables
# ИЗМЕНЕНО [02]: имена параметров — Unicode-строки для IronPython 2.7.
p_name_window_area              = u'Площадь вырезания стены'
p_name_RetroArea                = u'RETRO_Площадь помещения'
# ИЗМЕНЕНО [01]: последняя стадия сохранена как в исходнике,
# но теперь по ней отбираются и помещения, и существующие на ней окна.
phase = doc.Phases[doc.Phases.Size - 1]
# ИЗМЕНЕНО [11]: стадия отображается в общем окне, без отдельного вывода pyRevit.
#Functions

# ИЗМЕНЕНО [02]: уточнён комментарий; алгоритм округления сохранён.
# Внутренние кв. футы -> м² -> округление до 0,01 м² -> внутренние кв. футы.
def RoundingFunction(area):
    room_area_m2 = UnitUtils.ConvertFromInternalUnits(area, UnitTypeId.SquareMeters)
    room_area_m2_rounded = round(room_area_m2, 2)
    room_area_ft = UnitUtils.ConvertToInternalUnits(room_area_m2_rounded, UnitTypeId.SquareMeters)
    return room_area_ft


# ИЗМЕНЕНО [02]: Double сам по себе не означает площадь — это может быть длина.
def check_area_parameter(parameter, parameter_name, require_value=False):
    if parameter is None:
        raise ValueError(u"Не найден параметр '{}'".format(parameter_name))
    if parameter.StorageType != StorageType.Double:
        raise ValueError(u"Параметр '{}' должен хранить число Double".format(parameter_name))
    if not parameter.Definition.GetDataType().Equals(SpecTypeId.Area):
        raise ValueError(u"Тип данных параметра '{}' должен быть 'Площадь'".format(parameter_name))
    if require_value and not parameter.HasValue:
        raise ValueError(u"Параметр '{}' не заполнен".format(parameter_name))


# ИЗМЕНЕНО [02]: не выбираем случайный параметр при совпадении имён.
def get_parameter(element, parameter_name):
    parameters = list(element.GetParameters(parameter_name))
    if len(parameters) > 1:
        raise ValueError(u"Найдено несколько параметров '{}' — нужны разные имена или GUID".format(
            parameter_name
        ))
    return parameters[0] if parameters else None


# ИЗМЕНЕНО [08, 10]: ошибки накапливаются для итогового списка и не запрещают запись.
issues = []


def add_issue(element, message):
    text = (u"ID {}: {}".format(element.Id.IntegerValue, message)
            if element is not None else message)
    issues.append(text)


# ИЗМЕНЕНО [11]: текст для резервного сообщения, без открытия консоли.
def format_issues():
    return u"\n".join(
        u"{}. {}".format(index, message)
        for index, message in enumerate(issues, 1)
    )

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
# ==================================================


# 1. Получить помещения выбранной стадии
room_candidates = (FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements())
all_rooms = []

for room in room_candidates:
    try:
        room_phase = room.get_Parameter(BuiltInParameter.ROOM_PHASE_ID)                                         # Определить стадию помещения
        if room_phase is None:                                                                                  # Отфильтровать помещения без стадии
            raise ValueError(u"Не удалось определить стадию помещения")
        if room_phase.AsElementId() != phase.Id:                                                                # Отфильтровать помещения стадия которых не соответствует выбранной
            continue
        if room.Location is None or room.Area <= 0:
            continue
        if room.DesignOption is not None:
            raise ValueError(u"Помещение в варианте проектирования: нужна отдельная фильтрация вариантов")      # Получить предупреждение, если в проекте включены варианты проектирования
        all_rooms.append(room)
    except Exception as error:                                                                                  # Показать предупреждение если есть ошибки
        add_issue(room, u"Чтение помещения: {}".format(error))

# 2. Создать временный словарь: ID помещения -> стандартная площадь
rooms_dict = {}

for room in all_rooms:
    rooms_dict[room.Id.IntegerValue] = room.Area

# 3. Получить экземпляры окон
all_windows = (FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows).       #Получить все экземпляры окон в модели
               OfClass(FamilyInstance).WhereElementIsNotElementType().ToElements())
active_statuses = (ElementOnPhaseStatus.New, ElementOnPhaseStatus.Existing)                 #Создать кортеж из стадий окна: 1)Создан на текущей стадии 2)Существует на текущей стадии.
count_added = 0
count_zero = 0                                                                              #Количество окон с нулевыми значением параметра вырезания

# 4. Добавить во временный словарь помещений площади от окон
for window in all_windows:
    try:
        #Фильтрация лишних окон
        if window.GetPhaseStatus(phase.Id) not in active_statuses:  #Отфильтровать окна, которые не присутствуют на текущей стадии.
            continue
        if window.DesignOption is not None:                         #Получить предупреждение если окно в варианте проектирования.
            raise ValueError(u"Окно в варианте проектирования: нужна отдельная фильтрация вариантов")

        #Получить параметр вырезания окна
        window_instance_par = get_parameter(window, p_name_window_area)                    # Получить значение параметра вырезания у экземпляра или типоразмера
        if window_instance_par is None:
            window_instance_par = get_parameter(window.Symbol, p_name_window_area)
        check_area_parameter(window_instance_par, p_name_window_area, require_value=True)  # Проверить наличие параметра и проверить есть значение параметра.
        window_area = window_instance_par.AsDouble()                                       # Получить значение вырезания окна
        if math.isnan(window_area) or math.isinf(window_area) or window_area < 0:          # Проверить если значение площади не равно NaN, не равна бесконечности, не меньше нуля.
            raise ValueError(u"Площадь вырезания должна быть конечным неотрицательным числом")
        if window_area == 0:
            count_zero += 1
            continue

        # Определить вектор расположения окна
        if not window.HasSpatialElementFromToCalculationPoints:                               # Проверить есть ли расчетные точки у окна
            raise ValueError(u"Не настроены расчётные точки; добавка площади больше нуля")
        points = list(window.GetSpatialElementFromToCalculationPoints())                      # Проверить что есть 2 расчетные точки
        if len(points) != 2:
            raise ValueError(u"Ожидались две расчётные точки")
        direction = window.FacingOrientation                                                   # Получить направление окна
        if direction.GetLength() < 0.000001:                                                   # Получить предупреждением, если длина вектора слишком маленькая.
            raise ValueError(u"Не удалось определить направление окна")
        direction = direction.Normalize()                                                      # Сделать вектор равным единице

        #Определить помещение к которому относится окно
        origin = points[0]                                                             # Взять первую точку
        points.sort(key=lambda point: point.Subtract(origin).DotProduct(direction))    # Отсортировать точки по направлению окна изнутри наружу
        distance = points[1].Subtract(points[0]).DotProduct(direction)                 # Получить расстояние между расчетными точками и вызвать предупреждение если расстояние слишком маленькое.
        if distance < 0.000001:
            raise ValueError(u"Не удалось различить стороны расчётных точек")

        room = doc.GetRoomAtPoint(points[0], phase)                                                     # Получить помещение из которого это окно расположено.
        if room is None:                                                                                # Вызвать предупреждение если окно выходит в пространство без помещения.
            raise ValueError(u"В точке против FacingOrientation нет помещения на выбранной стадии")
        room_id = room.Id.IntegerValue
        if room_id not in rooms_dict:                                                                   # Проверить входит ли данная комната в выбранный список помещений
            raise ValueError(u"Найденное помещение {} не входит в набор помещений выбранной стадии".format(room_id))

        # Добавить площадь вырезания окна в помещение к которому оно относится.
        rooms_dict[room_id] += window_area
        count_added += 1
    except Exception as error:                                                                          # Показать предупреждение если оно возникло.
        add_issue(window, u"Семейство '{}': {}".format(window.Symbol.FamilyName, error))

# 5. Подготовить помещения к записи
room_parameters = {}
for room in all_rooms:
    try:
        room_id = room.Id.IntegerValue
        total_area = rooms_dict[room_id]
        if math.isnan(total_area) or math.isinf(total_area):                                        # Проверить является ли значение площади равным NaN или бесконечности.
            raise ValueError(u"Итоговая площадь не является конечным числом")
        rooms_dict[room_id] = RoundingFunction(total_area)                                          # Округлить значение площади
        room_parameter = get_parameter(room, p_name_RetroArea)                                      # Получить параметр площади
        check_area_parameter(room_parameter, p_name_RetroArea)                                      # Проверить подходит ли параметр
        if room_parameter.IsReadOnly:                                                               # Проверить доступность параметра для записи
            raise ValueError(u"Параметр '{}' доступен только для чтения".format(p_name_RetroArea))
        room_parameters[room.Id.IntegerValue] = room_parameter                                      # Записать в словарь значение параметра
    except Exception as error:                                                                      # Показать предупреждение если есть.
        add_issue(room, u"Помещение '{}': {}".format(room.Number, error))

# Записываем все подготовленные помещения даже при ошибках других элементов.
rooms_to_write = [room for room in all_rooms if room.Id.IntegerValue in room_parameters]

# ИЗМЕНЕНО [12]: при пустой выборке цикл записи будет пустым,
# а сводка и ошибки всё равно попадут в единое окно в конце скрипта.

# 6. Внести изменения в Revit

completed_rooms = []
count_saved = 0
count_unchanged = 0

for room in rooms_to_write:
    t = None
    stop_writing = False
    try:
        room_id = room.Id.IntegerValue
        room_parameter = room_parameters[room_id]
        new_area = rooms_dict[room_id]
        # Уже правильное значение входит в отчёт без новой транзакции.
        if room_parameter.HasValue and abs(room_parameter.AsDouble() - new_area) < 0.000000001: # Если значение не поменялось, то значение не записывается
            count_unchanged += 1
            completed_rooms.append(room)
            continue

        t = Transaction(doc, u"Площадь помещения {} (ID {})".format(room.Number, room_id)) # Записать значение в помещение
        if t.Start() != TransactionStatus.Started:
            raise Exception(u"Не удалось начать транзакцию")
        if not room_parameter.Set(new_area):
            raise Exception(u"Не удалось записать площадь помещения {}".format(room.Number))

        commit_status = t.Commit()
        if commit_status != TransactionStatus.Committed:
            raise Exception(u"Запись не подтверждена Revit. Статус: {}".format(commit_status))
        count_saved += 1
        completed_rooms.append(room)
    except Exception as error:
        add_issue(room, u"Запись помещения '{}': {}".format(room.Number, error))
        if t is not None:
            if t.GetStatus() == TransactionStatus.Started:
                try:
                    rollback_status = t.RollBack()
                    if rollback_status != TransactionStatus.RolledBack:
                        stop_writing = True
                        add_issue(room, u"Откат транзакции не завершён: {}".format(rollback_status))
                except Exception as rollback_error:
                    stop_writing = True
                    add_issue(room, u"Не удалось завершить откат: {}".format(rollback_error))
            if t.GetStatus() == TransactionStatus.Pending:
                # Pending — ожидание обработки ошибки самим Revit.
                # До завершения этого состояния новые транзакции запрещены.
                stop_writing = True
                add_issue(room, u"Revit ожидает завершения обработки ошибки; дальнейшая запись остановлена")
    finally:
        if t is not None and t.GetStatus() in (
                TransactionStatus.Committed, TransactionStatus.RolledBack,
                TransactionStatus.Uninitialized):
            t.Dispose()
    if stop_writing:
        # Подтверждённые ранее отдельные транзакции уже сохранены.
        break

# ИЗМЕНЕНО [11]: сначала подготовить все итоги, затем открыть одно общее окно.
# В таблице остаются только успешно записанные / уже актуальные помещения.
count_skipped = len(all_rooms) - len(completed_rooms)


def format_summary():
    # Повторный вызов учитывает и ошибку открытия окна, если она возникнет.
    return (u"Записано помещений: {}\n"
            u"Уже имели актуальную площадь: {}\n"
            u"Не обновлено из отобранных помещений: {}\n"
            u"Учтено окон в расчёте: {}\n"
            u"Окон с нулевой добавкой: {}\n"
            u"Ошибок: {}").format(
                count_saved, count_unchanged, count_skipped,
                count_added, count_zero, len(issues)
            )


result_note = u""
if not all_rooms:
    result_note = u"На стадии '{}' нет доступных для расчёта помещений.".format(phase.Name)
elif not rooms_to_write:
    result_note = u"Нет помещений, доступных для записи результата. Причины указаны в списке ошибок."
elif issues:
    result_note = (u"В записанные площади включены только успешно обработанные окна. "
                   u"Помещения с неподтверждённой записью не включены в таблицу.")

try:
    show_room_area_report(
        completed_rooms, p_name_RetroArea,
        summary=format_summary(), issues=issues,
        phase_name=phase.Name, result_note=result_note,
    )
except Exception as error:
    # ИЗМЕНЕНО [12]: резервное сообщение только при сбое самого окна отчёта.
    # Уже подтверждённые транзакции помещений не отменяются.
    add_issue(None, u"Не удалось открыть окно результатов: {}".format(error))
    forms.alert(
        u"Стадия расчёта: {}\n\n{}\n\n"
        u"Не удалось показать таблицу помещений. Успешные записи сохранены в модели.\n"
        u"Разверните подробности, чтобы посмотреть список ошибок.".format(
            phase.Name, format_summary()
        ),
        title=u"Результаты расчёта площадей",
        expanded=format_issues(),
    )
