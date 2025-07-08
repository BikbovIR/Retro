# -*- coding: utf-8 -*-

__title__ = {                                           #Name of the button displayed in Revit UI
    "en_us": "Pick linked elements",
    "ru": "Выбрать элементы связи"
}

__doc__ = """Version = 1.0
Date = 04.04.2025
-------------------------------------------------------------------------
Description:
Code from lessons 03.06 - Pick Linked Element
----------------------------------------------------------------------
Author: Erik Frits"""                                 #Description of the button displayed in Revit UI

#-------------------------------------------------------------------------
# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#-------------------------------------------------------------------------
from Autodesk.Revit.DB import *                          # Import DB Classes
from Autodesk.Revit.DB.Architecture import Room
from Autodesk.Revit.UI.Selection import ObjectType, Selection, ISelectionFilter

#.NET Imports
import clr
clr.AddReference('System')
from System.Collections.Generic import List

#-------------------------------------------------------------------------
# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#-------------------------------------------------------------------------
doc       = __revit__.ActiveUIDocument.Document             #type: Documentы
uidoc     = __revit__.ActiveUIDocument                      #type: UIDocument
selection = uidoc.Selection                                 #type: Selection
#-------------------------------------------------------------------------
# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
#-------------------------------------------------------------------------

#1️⃣ Pick Linked objects


# ref_picked_objects = selection.PickObjects(ObjectType.LinkedElement)
# picked_objects     = [doc.GetElement(ref) for ref in ref_picked_objects]
#-------------------------------------------------------------------------

#2️⃣ Read Linked Element
# ref_picked_objects = selection.PickObjects(ObjectType.LinkedElement)
# for ref in ref_picked_objects:
#     revit_link_instance = doc.GetElement(ref)
#     linked_doc          = revit_link_instance.GetLinkDocument()
#     linked_el           = linked_doc.GetElement(ref.LinkedElementId)
#     # print(linked_el)

#-------------------------------------------------------------------------

#3️⃣ Limit linked selection (IselectionFilter for Linked Models)

class LinkedRoomSelectionFilter(ISelectionFilter):
    def AllowElement(self, elem):
        return True

    def AllowReference(self, ref, position):
        revit_link_instance = doc.GetElement(ref)
        linked_doc = revit_link_instance.GetLinkDocument()
        linked_el = linked_doc.GetElement(ref.LinkedElementId)

        if type(linked_el) == Room:
            return True

#-------------------------------------------------------------------------

#4️⃣ Pick and Read Linked Elements with IselectionFilter

ref_picked_objects = selection.PickObjects(ObjectType.LinkedElement, LinkedRoomSelectionFilter()) #type: List[Reference]

for ref in ref_picked_objects:
    revit_link_instance = doc.GetElement(ref)
    linked_doc          = revit_link_instance.GetLinkDocument()
    linked_el           = linked_doc.GetElement(ref.LinkedElementId)
    print(linked_el)