# -*- coding: utf-8 -*-
__title__   = {
    "en_us": "Lists numering",
    "ru": "Нумерация листов"
}
__doc__     = """Version = 1.1
Date    = 21.01.2026
________________________________________________________________
Пронумеровать листы в стандартный параметр "Номер листа" как "Альбом + Номер листа"

Пример:
A1, A2, A3...
B1, B2, B3...

Далее запустить функцию "Нумерация листов", для того чтобы заполнить параметр RETRO_Номер листа

________
Last Updates:
- [03.02.2026] v1.0 Button was made
________________________________________________________________
Author: Ilnur Bikbov"""

import sys

import Autodesk.Revit.DB
import pyrevit.forms
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

# Select all lists
lists = FilteredElementCollector(doc).OfClass(ViewSheet).WhereElementIsNotElementType().ToElements()

#check if par in project
for l in lists:
    try:
        adsk_par =  l.LookupParameter('ADSK_Штамп Номер страницы')
    except:
        forms.alert("у листов отсутствует параметр 'ADSK_Штамп Номер страницы'")
        break



#Transaction
t = Transaction(doc,'PyRevit заполнил параметр "ADSK_Штамп Номер страницы"')


t.Start()

for l in lists:
    adsk_par = l.LookupParameter('ADSK_Штамп Номер страницы')
    num = l.get_Parameter(BuiltInParameter.SHEET_NUMBER).AsString()
    new = ''.join(ch for ch in num if ch.isdigit())
    adsk_par.Set(new)

t.Commit()

forms.alert("Параметр ADSK_Номер страницы перенесен")
