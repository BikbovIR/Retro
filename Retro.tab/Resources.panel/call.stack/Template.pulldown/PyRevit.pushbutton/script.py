# -*- coding: utf-8 -*-

__title__ = {                                           #Name of the button displayed in Revit UI
    "en_us": "Bikbov's Template",
    "ru": "Шаблон Бикбова"
}

__doc__ = """Version = 1.0
Date = 12.12.2024
-------------------------------------------------------------------------
Description:
This is a template file for pyRevit scripts
-------------------------------------------------------------------------
How-to: (Example)
-> Click on the button
-> Change Settings (optional)
-> Make change

-------------------------------------------------------------------------
Last update:
- [11.12.2024] - 1.1 UPDATE - New Feature
- [10.12.2024] - 1.0 RELEASE

-------------------------------------------------------------------------
To-Do:
- Check Revit 2023
- Add ... Feature

-------------------------------------------------------------------------
Author: Ilnur Bikvov"""                                 #Description of the button displayed in Revit UI

# pyRevit Extra MeraTags (optional)
__author__ = {                                          #Scripts's Author
    "en_us": "Bikbov Ilnur",
    "ru": "Бикбов Ильнур"
}
__helpurl__ = 'https://www.google.ru/?hl=ru'            #Link that opens with F1 when hovered over the button
__min_revit_ver__ = 2021                                #Limit your scripts to certain Revit version
__max_revit_ver__ = 2023                                #Limit your scripts to certain Revit version
__highlight__ = 'new'                                   # 'updated' #Add an Orange Marker in Revit UI to Button.
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
from Autodesk.Revit.DB import *                          # Import DB Classes
from Autodesk.Revit.UI import *                          # Import UI Classes
from Autodesk.Revit.DB.Architecture import *             # Import Discipline Modules

# pyRevit
from pyrevit import forms,revit, script                  # pyRevit modules have lots if useful features

# .Net Imports
import clr
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
t = Transaction(doc,'Change Name')
t.Start                                                # Start Transaction
# Changes Here...
t.Commit()                                             # Commit Transaction

#-------------------------------------------------------------------------
print('-'*50)
print('Script is finished')
print('Template has been developed by Ilnur Bikbov')

