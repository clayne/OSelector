import math
import widget.AnimTreeWidget
import xml.etree.ElementTree as ET

from util.Config import get_config

import logging
log = logging.getLogger(__name__)

from util.Config import get_config
from PyQt5.QtGui import QBrush
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidgetItem


class AnimTreeItem(QTreeWidgetItem):

    def __init__(self, *__args):
        super().__init__(*__args)
        self.setFlags(self.flags())
        self.setText(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.ICON.value, get_config().get("PLUGIN", "defaultFolderIcon"))
        self.setTextAlignment(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.ICON.value, Qt.AlignCenter)
        self.setCheckState(0, Qt.Checked)
        self.splitterCounter = 0
        self.splitterIndex = 0
        self.levelTwoCounter = 0
        self.maxChildCount = get_config().getint("PLUGIN", "maxItemStringLength")
        self.bIsSplitter = False

    @classmethod
    def convert_to_anim_tree_item(cls, obj):
        obj.__class__ = cls
        if obj.is_anim():
            obj.setFlags(obj.flags() ^ Qt.ItemIsDropEnabled)
        else:
            obj.setFlags(obj.flags())

        obj.bIsSplitter = False
        obj.splitterCounter = 0
        obj.splitterIndex = 0
        obj.levelTwoCounter = 0
        obj.maxChildCount = get_config().get("PLUGIN", "maxItemStringLength")

    def add_nested_child(self, item):
        # If there are already splitter let's try to add the item to the first available
        for i in range(self.childCount()):
            splitter = self.child(i)
            try:
                test = splitter.bIsSplitter
            except AttributeError:
                AnimTreeItem.convert_to_anim_tree_item(splitter)
            if splitter.bIsSplitter:
                if splitter.childCount() < splitter.maxChildCount:
                    return splitter.addChild(item)

        # If none is available, add an other splitter, if needed
        if 0 < self.next_splitter_index() < self.maxChildCount:
            index = self.next_splitter_index()
            splitter = self.insert_splitter(index)

            return splitter.addChild(item)

        if self.childCount() == self.maxChildCount:
            index = self.next_splitter_index()
            if self.splitter_level() > 1:
                self.levelTwoCounter += 1
                index = self.levelTwoCounter
            splitter = self.insert_splitter(index)
            for i in range(self.childCount()):
                child = self.takeChild(index+1)
                if not child:
                    child = AnimTreeItem()

                try:
                    test = child.bIsSplitter
                except AttributeError:
                    AnimTreeItem.convert_to_anim_tree_item(child)

                if child.bIsSplitter:
                    child.setText(0, "Set " + str(i+1))

                splitter.addChild(child)

            splitter = self.insert_splitter()
            splitter.addChild(item)
            return True

        return self.addChild(item)

    def animation_count(self, state=Qt.Unchecked):
        if self.bIsSplitter or not self.is_anim():
            counter = 0
            for i in range(self.childCount()):
                child = self.child(i)
                if child.checkState(0) != state:
                    try:
                        test = child.bIsSplitter
                    except AttributeError:
                        AnimTreeItem.convert_to_anim_tree_item(child)
                    counter += child.animation_count(state)

            return counter
        else:
            return 1

    def animations_id(self):
        if self.bIsSplitter or not self.is_anim():
            animations = []
            for i in range(self.childCount()):
                child = self.child(i)
                try:
                    test = child.bIsSplitter
                except AttributeError:
                    AnimTreeItem.convert_to_anim_tree_item(child)
                animations.extend(child.animations_id())
            return animations
        else:
            return [self.text(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.ID.value)]

    def to_xml(self, parent, level):
        if self.bIsSplitter or not self.is_anim():
            elt = ET.SubElement(parent, "folder" + str(level))
            elt.set("n", self.text(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.NAME.value))
            if self.bIsSplitter:
                elt.set("i", self.text(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.ICON.value) or get_config().get("PLUGIN", "defaultSetIcon"))
            else:
                elt.set("i", self.text(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.ICON.value) or get_config().get("PLUGIN", "defaultFolderIcon"))

            for i in range(self.childCount()):
                child = self.child(i)
                if child.checkState(0) != Qt.Unchecked:
                    try:
                        test = child.bIsSplitter
                    except AttributeError:
                        AnimTreeItem.convert_to_anim_tree_item(child)
                    child.to_xml(elt, level + 1)
        else:
            entry = ET.SubElement(parent, "entry")
            entry.set("n", self.text(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.NAME.value))
            entry.set("i", self.text(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.ICON.value) or get_config().get("PLUGIN", "defaultAnimationIcon"))
            entry.set("id", self.text(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.ID.value))

    def flags(self):
        return super().flags() | Qt.ItemIsTristate | Qt.ItemIsEditable | Qt.ItemIsUserCheckable

    def next_splitter_index(self):
        return self.splitterIndex

    def set_next_splitter_index(self, num=-1):
        if num == -1:
            self.splitterIndex = (self.splitterIndex+1 % self.maxChildCount)
        else:
            self.splitterIndex = (num % self.maxChildCount)
        return

    def splitter_level(self):
        return math.floor(self.splitterCounter / self.maxChildCount)

    def insert_splitter(self, index=-1):
        if index == -1:
            index = self.next_splitter_index()
        splitter = AnimTreeItem()
        splitter.setText(0, "Set " + str(index+1))
        splitter.setText(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.ICON.value, get_config().get("PLUGIN", "defaultSetIcon"))
        splitter.bIsSplitter = True
        self.insertChild(index, splitter)
        self.splitterCounter += 1
        self.set_next_splitter_index(index + 1)
        return splitter

    def is_anim(self):
        if self.text(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.ID.value):
            return True
        return False

    def set_color(self, color=Qt.black):
        brush = QBrush(color)
        self.setForeground(0, brush)

    def set_animation(self, animation, i):
        self.setFlags(self.flags() ^ Qt.ItemIsDropEnabled)
        self.setText(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.NAME.value, animation.parse_stage_name(i)[slice(-get_config().getint("PLUGIN", "maxItemStringLength"), None)])
        self.setText(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.ICON.value, get_config().get("PLUGIN", "defaultAnimationIcon"))
        self.setText(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.TYPE.value, animation.type.name)
        self.setText(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.OPTIONS.value, str([x.name for x in animation.options]))
        self.setText(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.ID.value, str(animation.stages[i]))
        self.setText(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.FILE.value, str(animation.stages_file[i]))
        self.setText(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.ANIM_OBJ.value, str(animation.stages_obj[i]))

