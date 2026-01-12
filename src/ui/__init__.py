# -*- coding: utf-8 -*-
"""UI Package - Giao diện người dùng"""

from .theme import COLORS, FONTS, DIMENSIONS
from .components import (
    ModernFrame, ModernLabelFrame, ModernLabel, ModernEntry,
    ModernButton, ModernCombobox, ModernCheckbutton, ModernScale,
    ModernListbox, ModernScrollbar, StatusBar, SectionHeader,
    IconButton, Separator
)
from .dialogs import DialogManager, RegionCaptureDialog
from .main_window import MainWindow

__all__ = [
    'COLORS', 'FONTS', 'DIMENSIONS',
    'ModernFrame', 'ModernLabelFrame', 'ModernLabel', 'ModernEntry',
    'ModernButton', 'ModernCombobox', 'ModernCheckbutton', 'ModernScale',
    'ModernListbox', 'ModernScrollbar', 'StatusBar', 'SectionHeader',
    'IconButton', 'Separator',
    'DialogManager', 'RegionCaptureDialog',
    'MainWindow'
]
