# -*- coding: utf-8 -*-
__title__   = {
    "en_us": "Lists numering",
    "ru": "Нумерация листов"
}
__doc__     = """Version = 2.1
Date    = 11.09.2026
________________________________________________________________
Прописать в системный параметр "Номер листа" значение "Номер альбома + Номер листа"

Пример:
AР1_1, AР1_2, AР1_3...
AР2_1, AР2_2, AР2_3...

Далее запустить функцию "Нумерация листов", для того чтобы заполнить параметр ADSK_Штамп Номер страницы

________
Last Updates:
- [11.09.2026] v1.1 The numerical  parameter was changed
- [03.02.2026] v1.0 Button was made
________________________________________________________________
Author: Ilnur Bikbov"""

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

PARAM_NAME = "ADSK_Штамп Номер страницы"
TITLE = "Номера страниц"
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

# 1. Собираем листы и подготавливаем значения.
sheets = FilteredElementCollector(doc).OfClass(ViewSheet).ToElements()
changes = []
skipped = 0
unchanged = 0

for sheet in sheets:
    # АР1_2 -> 2; АР2_15 -> 15; АР1_01 -> 01.
    album, separator, page = (sheet.SheetNumber or u"").rpartition(u"_")
    page = page.strip()

    if not separator or not album.strip() or not page.isdigit():
        skipped += 1
        continue

    parameter = sheet.LookupParameter(PARAM_NAME)
    if (parameter is None
            or parameter.IsReadOnly
            or parameter.StorageType != StorageType.String):
        skipped += 1
        continue

    if parameter.AsString() == page:
        unchanged += 1
        continue

    changes.append((parameter, page))

# 2. Записываем значения одной транзакцией.
if changes:
    with Transaction(doc, u"Заполнить номера страниц") as transaction:
        try:
            transaction.Start()
            for parameter, page in changes:
                if not parameter.Set(page):
                    raise RuntimeError(u"Не удалось записать номер страницы.")
            status = transaction.Commit()

        except Exception as error:
            if transaction.GetStatus() == TransactionStatus.Started:
                transaction.RollBack()
            forms.alert(
                u"Ошибка записи:\n{}".format(error),
                title=TITLE, exitscript=True,
            )

        if status != TransactionStatus.Committed:
            forms.alert(
                u"Revit не подтвердил сохранение изменений.",
                title=TITLE, exitscript=True,
            )

# 3. Показываем результат.
message = (
    u"Параметр: {}\n\n"
    u"Обновлено листов: {}\n"
    u"Уже заполнено верно: {}\n"
    u"Пропущено: {}"
).format(PARAM_NAME, len(changes), unchanged, skipped)

if skipped:
    message += (
        u"\n\nПропущены листы с неподходящим номером или параметром."
        u"\nОжидается номер вида АР1_2 и доступный для записи текстовый параметр."
    )

forms.alert(message, title=TITLE)

