# -*- coding: utf-8 -*-

__title__ = {
    "en_us": "Bikbov's Template",
    "ru": "Шаблон Бикбова"
}

__doc__ = """Version = 1.0
Date = 12.12.2024
-------------------------------------------------------------------------
Description:
This is a template file for pyRevit scripts
-------------------------------------------------------------------------
To-Do:
- Check Revit 2023
- Add ... Feature

-------------------------------------------------------------------------
Author: Ilnur Bikvov"""

#-------------------------------------------------------------------------
# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#-------------------------------------------------------------------------
from Autodesk.Revit.DB import *
from pyrevit import forms

# .Net Imports
import clr
clr.AddReference('System')
from System.Collections.Generic import List                # List_example = List[ElementId]()


#-------------------------------------------------------------------------
# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#-------------------------------------------------------------------------
doc   = __revit__.ActiveUIDocument.Document             #type: Document
uidoc = __revit__.ActiveUIDocument                      #type: UIDocument
app   = __revit__.Application                           # Application class

active_view  = doc.ActiveView
active_level = active_view.GenLevel
rvt_year     = int(app.VersionNumber)

#-------------------------------------------------------------------------
# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
#-------------------------------------------------------------------------

# START CODE HERE


#-------------------------------------------------------------------------
print('-'*50)
print('Script is finished')
print('Template has been developed by Ilnur Bikbov')

