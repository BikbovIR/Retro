# -*- coding: utf-8 -*-

__title__ = {                                           #Name of the button displayed in Revit UI
    "en_us": "Rename views",
    "ru": "Переименовать виды"
}

__doc__ = """Version = 1.0
Date = 24.12.2024
-------------------------------------------------------------------------
Description:
Переименовать виды в Ревит используя логику Найти/Заменить

Как работает:
-> Нажать на кнопку
-> Выбрать виды
-> Определить правила переименования 
-> Переименовать виды



button made via a lesson https://www.youtube.com/watch?v=B1CJTK-4U8g
-------------------------------------------------------------------------

----------------------------------------------------------------------
Last update:
- 24.12.2024 - 1.0 Release
----------------------------------------------------------------------

Author: Ilnur Bikvov"""                                 #Description of the button displayed in Revit UI

# pyRevit Extra MeraTags (optional)
__author__ = {                                          #Scripts's Author
    "en_us": "Bikbov Ilnur",
    "ru": "Бикбов Ильнур"
}
__helpurl__ = 'https://www.google.ru/?hl=ru'            #Link that opens with F1 when hovered over the button
__min_revit_ver__ = 2021                                #Limit your scripts to certain Revit version
__max_revit_ver__ = 2023                                #Limit your scripts to certain Revit version
# __highlight__ = 'new'                                   # 'updated' #Add an Orange Marker in Revit UI to Button.
#__context__ = ["selection", "active-section-view"]      #Activate Button only: 1. Selection not empty 2. ActiveView:  Selection
#__context__ = ['Doors', 'Walls', 'Floors']              #Activate Button only if Doors/Wall/Floor selected
#__context__ = 'doc-project' #'doc-family'               #Activate Button only if Project/Family file
#__context__ = ['active-plan-view', 'active-legend']     #Activate Button only if ViewPlan or Legend active


#-------------------------------------------------------------------------
# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#-------------------------------------------------------------------------
import  os, sys, datetime                                # Regular imports
from sys import prefix

from Autodesk.Revit.DB import *                          # Import DB Classes
from Autodesk.Revit.UI import *                          # Import UI Classes
from Autodesk.Revit.DB.Architecture import *             # Import Discipline Modules

# pyRevit
from pyrevit import forms,revit, script                  # pyRevit modules have lots if useful features

# .Net Imports
import clr
from select import select

clr.AddReference('System')
from System.Collections.Generic import List
# List_example = List[ElementId]()



#-------------------------------------------------------------------------
# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#-------------------------------------------------------------------------
doc   = __revit__.ActiveUIDocument.Document             #type: Document
uidoc = __revit__.ActiveUIDocument                      #type: UIDocument
app   = __revit__.Application                           # Application class

active_view  = doc.ActiveView                           # Get Currently open View
active_level = active_view.GenLevel                     # Only ViewPlan views have associated Level/
rvt_year     = int(app.VersionNumber)                   # e.g. 2023
PATH_SCRIPT  = os.path.dirname(__file__)                #Absolute path to the folder where script is located

# GLOBAL  VARIABLES

# Place global variables...




#-------------------------------------------------------------------------
# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
#-------------------------------------------------------------------------

# Place global functions here... Consider adding to custom lib if you want to reuse


#-------------------------------------------------------------------------
# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝ CLASSES
#-------------------------------------------------------------------------

# Place global classes here... Consider adding to custom lib if you want to reuse

#-------------------------------------------------------------------------
# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
#-------------------------------------------------------------------------

# START CODE HERE

# Use Transactions to Modify Document (Avoid placing inside of loops)
# t = Transaction(doc,'Change Name')
# t.Start                                                # Start Transaction
# # Changes Here...
# t.Commit()                                             # Commit Transaction

#-------------------------------------------------------------------------
print('-'*50)
print('Script is finished')
print('Template has been developed by Ilnur Bikbov')

# 1. Select views
# Get views - Selected in ProjectBrowser
sel_el_ids = uidoc.Selection.GetElementIds()
sel_elem   = [doc.GetElement(e_id) for e_id in sel_el_ids]
sel_views  = [el for el in sel_elem if issubclass(type(el),View)]

# if None selected - Prom SelectViews from pyrevit.forms.select_views()
if not sel_views:
    sel_views = forms.select_views()
# Ensure Views are Selected
if not sel_views:
    forms.alert('Виды не выбраны. Попробуйте еще раз', exitscript=True)

# # 2. Define Renaming Rules
# prefix  = 'pre'
# find    = 'Т_АР_ПЭ'
# replace = 'Retro-Level'
# suffix  = '-suf'
#Docs: https://revitpythonwrapper.readthedocs.io/en/latest/ui.forms.html#flexform

from rpw.ui.forms import (FlexForm, Label, TextBox, Separator,Button)
components = [ Label('Prefix:'),  TextBox('prefix'),
               Label('Find:'),    TextBox('find'),
               Label('Replace:'), TextBox('replace'),
               Label('Suffix:'),  TextBox('suffix'),
               Separator(), Button('Rename Views')]
form = FlexForm('Title', components)
form.show()

users_inputs = form.values #type: dict
prefix  = users_inputs['prefix']
find    = users_inputs['find']
replace = users_inputs['replace']
suffix  = users_inputs['suffix']


# Start Transaction to make changes in the project
t = Transaction(doc, 'py_Rename views')

t.Start()

for view in sel_views:

    # 3. Create new View Name
    old_name = view.Name
    new_name = prefix + old_name.replace(find, replace) + suffix

    # 4. Rename Views (Ensure unique name)
    for i in range(20):
        try:
            view.Name = new_name
            print('{} -> {}'.format(old_name,new_name))
            break
        except:
            new_name += '*'


t.Commit()

print('-'*50)
print('Готово')