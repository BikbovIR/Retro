# -*- coding: utf-8 -*-

__title__ = "Создание разрезов окон"

__doc__ = """Version = 1.0
Date = 10.01.2025
-------------------------------------------------------------------------
Description:
После нажатия будут созданы разрезы по всем типам окон в проекте
-------------------------------------------------------------------------
Author: Erik Frits"""                                 #Description of the button displayed in Revit UI

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
from rpw.utils.rlcompleter import builtin_dir

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

# Get and Sort Window Instances of Each Type
windows = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows).WhereElementIsNotElementType().ToElements()

dict_windows = {}
for win in windows:

    family_name = win.Symbol.Family.Name
    type_name = win.Name
    # type_name = Element.Name.GetValue(win.Symbol)
    key_name =  '{}_{}'.format( family_name,type_name)

    host = win.Host
    if type(host) == Wall:
        dict_windows[key_name] = win
    else:
        print('Unsupported window host for Window: {} [{}]'.format(key_name,win.Id))

# #Отображение выделенных окон
# for k,v in dict_windows.items():
#     print(k,v)

# Use Transactions to Modify Document (Avoid placing inside of loops)
t = Transaction(doc,'Generate Window Sections')
t.Start()                                         # Start Transaction

# Create section
for window_name, window in dict_windows.items():
    try:
        #Get Window Origin Point
        win_origin = window.Location.Point            #type: XYZ
        # Calculate Vector based on the Wall
        host_wall  = window.Host
        curve      = host_wall.Location.Curve         #type: Curve
        pt_start   = curve.GetEndPoint(0)             #type: XYZ
        pt_end     = curve.GetEndPoint(1)             #type: XYZ
        vector     = pt_end - pt_start                #type: XYZ

        # Get window size

        win_width   = window.get_Parameter(BuiltInParameter.DOOR_WIDTH).AsDouble()
        cm_40       = UnitUtils.ConvertToInternalUnits(40, UnitTypeId.Centimeters) #40 cm (Revit API takes in FEET)
        offset      = cm_40
        win_depth   = cm_40
        win_height  = window.get_Parameter(BuiltInParameter.CASEWORK_HEIGHT).AsDouble()
        if not win_height:
            win_height = win.Symbol.LookUpParameter('ADSK_Высота').AsDouble() #Adjust to yours parameters!

        # print('-'*50)
        # print(window.Id)
        # print(win_height)
        # print(win_width )
        # print(offset    )
        # print(win_depth )


        #Create Transform (origin point + X,Y,Z Vectors)
        trans = Transform.Identity                  #Create Instance of Transform
        trans.Origin = win_origin                   # Set Origin Point (Window Insertion Point)

        vector = vector.Normalize()

        trans.BasisX = vector
        trans.BasisY = XYZ.BasisZ
        trans.BasisZ = vector.CrossProduct(XYZ.BasisZ) #The cross product is defined as the vector which is perpendicular to

        #Create SectionBox
        section_box = BoundingBoxXYZ() # #XYZ(0,0,0)

        half            = win_width/2
        section_box.Min = XYZ(-half- offset,0          - offset, -win_depth)
        section_box.Max = XYZ(half + offset,win_height + offset, win_depth)
        #                 XYZ( X - Left/Right, Y - Up/Down,     Z - Forward/Backward )

        section_box.Transform = trans #Apply Transform (Origin + XYZ Vectors

        #Create Section View
        section_type_id  = doc.GetDefaultElementTypeId(ElementTypeGroup.ViewTypeSection)
        window_elevation = ViewSection.CreateSection(doc, section_type_id, section_box)

        #New Name
        new_name = 'Retro_{} (Разрез окна)'.format(window_name)



        for i in range(10):
            try:
                window_elevation.Name = new_name
                print('Создан разрез: {}'.format(new_name))
                break
            except:
                new_name += '*'
    except:
        import traceback
        print('---\nError:')
        print(traceback.format_exc())


t.Commit()                                             # Commit Transaction

#-------------------------------------------------------------------------
print('-'*50)
print('Script is finished')
print('Template has been developed by Ilnur Bikbov')

