# -*- coding: utf-8 -*-
__title__ = "Cat"
__doc__   = """
It's just a cat
"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#====================================================================================================
from Autodesk.Revit.DB import *
from pyrevit import forms   # By importing forms you also get references to WPF package! IT'S Very IMPORTANT !!!
import wpf, os, clr, sys    # wpf can be imported only after pyrevit.forms!

# .NET Imports
clr.AddReference("System")
from System.Windows import Window, Visibility
from System import Uri
from System.Windows.Media.Imaging import BitmapImage

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#====================================================================================================
PATH_SCRIPT = os.path.dirname(__file__)
doc     = __revit__.ActiveUIDocument.Document #type: Document
uidoc   = __revit__.ActiveUIDocument
app     = __revit__.Application

# ╔╦╗╔═╗╦╔╗╔  ╔═╗╔═╗╦═╗╔╦╗
# ║║║╠═╣║║║║  ╠╣ ║ ║╠╦╝║║║
# ╩ ╩╩ ╩╩╝╚╝  ╚  ╚═╝╩╚═╩ ╩ MAIN FORM
#====================================================================================================
# Inherit .NET Window for your UI Form Class


class AlertForm(Window):
    def __init__(self, msg, sub_msg="", image_path="", title='CreateAlert.xaml', exitscript=False):
        #⬇️ Connect to .xaml File (in the same folder!)
        path_xaml_file = os.path.join(PATH_SCRIPT, 'CreateAlert.xaml')
        wpf.LoadComponent(self, path_xaml_file)

        #🟦 Change Main Message
        self.UI_msg.Text    = msg

        #🟦 Sub-Message
        if sub_msg:
            self.UI_submsg.Text = sub_msg

        #🟦 Image
        path_image_file = os.path.join(PATH_SCRIPT, image_path)
        if image_path:
            # self.UI_img.Source     = BitmapImage(Uri(image_path))
            self.UI_img.Source     = Uri(image_path)
            self.UI_img.Visibility = Visibility.Visible

        #🟦 Change Title
        self.Title          = title

        #🟧 Store Exitscript value
        self.exitscript = exitscript


        # Show Form
        self.ShowDialog()

    # ╔╗ ╦ ╦╔╦╗╔╦╗╔═╗╔╗╔╔═╗
    # ╠╩╗║ ║ ║  ║ ║ ║║║║╚═╗
    # ╚═╝╚═╝ ╩  ╩ ╚═╝╝╚╝╚═╝ BUTTONS
    #==================================================
    def UIe_btn_run(self, sender, e):
        """Button action: Rename view with given """
        self.Close()

        if self.exitscript:
            sys.exit()

# ╦ ╦╔═╗╔═╗  ╔═╗╔═╗╦═╗╔╦╗
# ║ ║╚═╗║╣   ╠╣ ║ ║╠╦╝║║║
# ╚═╝╚═╝╚═╝  ╚  ╚═╝╩╚═╩ ╩
#====================================================================================================
path_image_file        = os.path.join(PATH_SCRIPT, 'working cat.gif')
AlertForm('Cat',sub_msg="",image_path=path_image_file,title="Cat", exitscript=False)
