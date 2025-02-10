# -*- coding: utf-8 -*-

"""
SelectMirroredWindows
Selects All Window Instances that have been Mirrored.
TESTED REVIT API: 2015 | 2016

Copyright (c) 2014-2016 Gui Talarico
github.com/gtalarico

This script is part of PyRevitPlus: Extensions for PyRevit
github.com/gtalarico

--------------------------------------------------------
PyRevit Notice:
Copyright (c) 2014-2016 Ehsan Iran-Nejad
pyRevit: repository at https://github.com/eirannejad/pyRevit

"""

#-------------------------------------------------------
__title__ = "Выделить отзеркаленные\nОкна"

__doc__ = """
Выделить все отзеркаленные окна в проекте

Selects All Window Instances that have been Mirrored."""

__author__ = "@gtalarico"

from rpw import db, ui

windows = db.Collector(of_category='Windows').elements
mirrored_windows = [x for x in windows if getattr(x, 'Mirrored', False)]

msg = "Mirrored: {} of {} Windows".format(len(mirrored_windows), len(windows))
ui.forms.Alert(msg, title="Mirrored Windows")

selection = ui.Selection(mirrored_windows)
