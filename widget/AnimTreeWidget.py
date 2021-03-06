import xml.etree.ElementTree as ET
import widget.AnimTreeItem

import logging
log = logging.getLogger(__name__)

from enum import Enum
from util.Config import get_config
from widget.QuickyGui import *
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView, QMenu, QTreeWidget, QMessageBox
from PyQt5.QtGui import QCursor


class AnimTreeWidget(QTreeWidget):

    class ROLE(Enum):
        FOLDER = 1001
        SPLITTER = 1002
        ANIMATION = 1003

    class COLUMN(Enum):
        NAME = 0
        ICON = 1
        TYPE = 2
        OPTIONS = 3
        ID = 4
        FILE = 5
        ANIM_OBJ = 6

    def __init__(self, parent=None):
        super().__init__(parent)

        self.header().setDefaultAlignment(Qt.AlignHCenter)
        self.header().setMinimumSectionSize(200)
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.header().setFont(get_normal_font())
        self.setHeaderLabels([AnimTreeWidget.COLUMN.NAME.name,
                              AnimTreeWidget.COLUMN.ICON.name,
                              AnimTreeWidget.COLUMN.TYPE.name,
                              AnimTreeWidget.COLUMN.OPTIONS.name,
                              AnimTreeWidget.COLUMN.ID.name,
                              AnimTreeWidget.COLUMN.FILE.name,
                              AnimTreeWidget.COLUMN.ANIM_OBJ.name])

        self.setColumnWidth(AnimTreeWidget.COLUMN.NAME.value, 400)
        self.setColumnWidth(AnimTreeWidget.COLUMN.ICON.value, 400)
        self.setColumnWidth(AnimTreeWidget.COLUMN.TYPE.value, 100)
        self.setColumnWidth(AnimTreeWidget.COLUMN.ID.value, 200)

        self.hideColumn(self.COLUMN.TYPE.value)
        self.hideColumn(self.COLUMN.OPTIONS.value)
        self.hideColumn(self.COLUMN.FILE.value)
        self.hideColumn(self.COLUMN.ANIM_OBJ.value)

        self.setDragEnabled(True)
        self.setDragDropMode(self.InternalMove)
        self.setDropIndicatorShown(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_menu)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QTreeWidget.DoubleClicked | QTreeWidget.EditKeyPressed)
        self.setSelectionMode(self.ExtendedSelection)

    def action_insert_parent(self):
        items = self.selectedItems()
        newParent = widget.AnimTreeItem.AnimTreeItem()
        newParent.setText(0, "New Parent")

        # We want the lowest parent (Meaning the parent the most close to the root)
        items_parent = []
        for item in items:
            if item in items_parent:
                items_parent.clear()

            item_parent = item.parent()
            if not item_parent:
                item_parent = self.invisibleRootItem()

            if not item_parent in items:
                items_parent.append((item_parent, item))

        parent, item = items_parent[0]

        index = parent.indexOfChild(item)
        parent.insertChild(index, newParent)

        for item in items:
            item_parent = item.parent()
            if not item_parent:
                item_parent = self.invisibleRootItem()

            item_index = item_parent.indexOfChild(item)
            child = item_parent.takeChild(item_index)
            newParent.add_nested_child(child)
        return

    def action_move_up(self, item=None):
        if not item:
            items = self.selectedItems()
            for item in items:
                self.action_move_up(item)
            return True

        n1 = item.parent()
        if not n1:
            return False

        n2 = n1.parent()
        if not n2:
            n2 = self.invisibleRootItem()

        item_index = n1.indexOfChild(item)
        item = n1.takeChild(item_index)
        n2.addChild(item)
        return True

    def action_merge(self):
        items = self.selectedItems()

        items_parent = []
        for item in items:
            item_parent = item.parent()
            if not items_parent:
                items_parent = self.invisibleRootItem()

            if item_parent in items:
                QMessageBox.warning(self, "Merge Action", "One selected folder is a parent of another selected folder !\n"
                                                          "Merging folders with both parent and child selected is not supported !\n"
                                                          "Select only folders from the same level")
                return

            if item.is_anim():
                QMessageBox.warning(self, "Merge Action", "Merging animations is not allowed !\n"
                                                          "Select only folders from the same level")
                return

        parent = items.pop(0)

        p2 = parent.parent()
        if not p2:
            p2 = self.invisibleRootItem()

        for item in items:
            for child_index in range(item.childCount()):
                child = item.takeChild(0)
                parent.add_nested_child(child)
            p2.removeChild(item)

        return True

    def action_remove_from_parent(self, item=None):
        if not item:
            items = self.selectedItems()
            for item in items:
                self.action_remove_from_parent(item)
            return True

        parent = item.parent()
        if not parent:
            parent = self.invisibleRootItem()
        parent.removeChild(item)

    def action_uncheck_all(self):
        root = self.invisibleRootItem()
        for i in range(root.childCount()):
            self.check_children(root.child(i), Qt.Unchecked)

    def animation_count(self, state=Qt.Unchecked):
        root = self.invisibleRootItem()

        counter = 0
        for i in range(root.childCount()):
            child = root.child(i)
            if child.checkState(0) != state:
                try:
                    test = child.bIsSplitter
                except AttributeError:
                    widget.AnimTreeItem.AnimTreeItem.convert_to_anim_tree_item(child)
                counter += child.animation_count(state)
        return counter

    def animations_id(self):
        root = self.invisibleRootItem()

        animations = []
        for i in range(root.childCount()):
            child = root.child(i)
            try:
                test = child.bIsSplitter
            except AttributeError:
                widget.AnimTreeItem.AnimTreeItem.convert_to_anim_tree_item(child)

            animations.extend(child.animations_id())
        return animations

    def check_all(self):
        root = self.invisibleRootItem()
        for i in range(root.childCount()):
            self.check_children(root.child(i), Qt.Checked)

    def check_children(self, item, state):
        item.setCheckState(0, state)
        for i in range(item.childCount()):
            self.check_children(item.child(i), state)

    def cleanup(self, item=None):
        has_been_removed = False
        if not item:
            item = self.invisibleRootItem()

        if not item.text(AnimTreeWidget.COLUMN.ID.value):
            if item.childCount() == 0:
                self.action_remove_from_parent(item)
                has_been_removed = True
            else:
                counter = 0
                for i in range(item.childCount()):
                    if not self.cleanup(item.child(counter)):
                        counter += 1

            if item.childCount() == 1:
                child = item.child(0)
                if self.action_move_up(child):
                    self.action_remove_from_parent(item)
                    has_been_removed = True
                self.cleanup(child)
        return has_been_removed

    def create_from_xml(self, xml_file):

        animations = []

        if self.invisibleRootItem().childCount() > 0:
            box = QMessageBox()
            box.setIcon(QMessageBox.Question)
            box.setWindowTitle('Clear or Append ?')
            box.setText("Do you want to append new animations to the tree"
                        "or clear the tree and build a new one from the new animations ?")
            box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            buttonY = box.button(QMessageBox.Yes)
            buttonY.setText('Clear')
            buttonN = box.button(QMessageBox.No)
            buttonN.setText('Append')
            box.exec_()

            if box.clickedButton() == buttonY:
                self.clear()
            else:
                answer = question(None, "Duplicates ?", "Do you want to ignore already existing animations ?")
                if answer == QMessageBox.Yes:
                    animations = self.animations_id()

        xml = ET.parse(xml_file)
        root = self.invisibleRootItem()
        counter = self.add_item_from_xml(root, xml.getroot(), animations)

        return counter

    def add_item_from_xml(self, parent, elt, animations):
        counter = 0
        duplicate_counter = 0
        for child in elt:
            if child.get("id") in animations:
                duplicate_counter += 1
                log.info("Duplicate found : " + child.get("n"))
            else:
                item = widget.AnimTreeItem.AnimTreeItem()
                item.setText(self.COLUMN.NAME.value, child.get("n"))
                item.setText(self.COLUMN.ICON.value, child.get("i") or get_config().get("PLUGIN", "defaultFolderIcon"))
                if child.get("id"):
                    counter += 1
                    item.setText(self.COLUMN.ID.value, child.get("id"))
                parent.addChild(item)
                counter += self.add_item_from_xml(item, child, animations)
        return counter

    def create_from_packages(self, packages):

        animations = []
        duplicate_counter = 0

        if self.invisibleRootItem().childCount() > 0:
            box = QMessageBox()
            box.setIcon(QMessageBox.Question)
            box.setWindowTitle('Clear or Append ?')
            box.setText("Do you want to append new animations to the tree"
                        "or clear the tree and build a new one from the new animations ?")
            box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            buttonY = box.button(QMessageBox.Yes)
            buttonY.setText('Clear')
            buttonN = box.button(QMessageBox.No)
            buttonN.setText('Append')
            box.exec_()

            if box.clickedButton() == buttonY:
                self.clear()
            elif box.clickedButton() == buttonN:
                answer = question(None, "Duplicates ?", "Do you want to ignore already existing animations ?")
                if answer == QMessageBox.Yes:
                    animations = self.animations_id()
        root = widget.AnimTreeItem.AnimTreeItem(self)
        for package in packages:
            section = widget.AnimTreeItem.AnimTreeItem()
            section.setText(0, package.name)
            root.add_nested_child(section)

            for module in package.items:
                module_section = widget.AnimTreeItem.AnimTreeItem()
                module_section.setText(0, module.name)
                section.add_nested_child(module_section)

                previous_animation = ""
                anim_section = None
                counter = 1
                for animation in module.items:
                    if animation.parse_name() != previous_animation or not anim_section:
                        previous_animation = animation.parse_name()
                        counter = 1
                        anim_section = widget.AnimTreeItem.AnimTreeItem()
                        anim_section.setText(0, animation.parse_name()[slice(0, get_config().getint("PLUGIN", "maxItemStringLength"))])
                        module_section.add_nested_child(anim_section)

                    for i, stage in enumerate(animation.stages):
                        if animation.stages[i] in animations:
                            duplicate_counter += 1
                            log.warning("Duplicate found : " + animation.stages[i] + " in " + package.name + " | " + module.name)
                        else:
                            stage_section = widget.AnimTreeItem.AnimTreeItem()
                            stage_section.set_animation(animation, i)
                            anim_section.add_nested_child(stage_section)
                            counter += 1
                            animations.append(animation.stages[i])

        invisible_root = self.invisibleRootItem()
        for i in range(root.childCount()):
            child = root.takeChild(0)
            invisible_root.addChild(child)
        invisible_root.removeChild(root)

        return duplicate_counter

    def open_menu(self):
        selection = self.selectedItems()
        if selection:
            menu = QMenu()
            menu.addAction("Check All", self.check_all)
            menu.addAction("Uncheck All", self.action_uncheck_all)
            menu.addAction("Cleanup", self.cleanup)
            menu.addSeparator()
            menu.addAction("Insert parent", self.action_insert_parent)
            menu.addAction("Merge", self.action_merge)
            menu.addAction("Remove", self.action_remove_from_parent)
            menu.exec_(QCursor.pos())
        return

    def to_xml(self, plugin_name):
        root = self.invisibleRootItem()
        folder0 = ET.Element("folder0")
        folder0.set("n", plugin_name)
        folder0.set("i", get_config().get("PLUGIN", "defaultPackageIcon"))

        for i in range(root.childCount()):
            child = root.child(i)
            if child.checkState(0) != Qt.Unchecked:
                try:
                    test = child.bIsSplitter
                except AttributeError:
                    log.warning("TreeItem detected ! Should be AnimTreeItem, trying to convert it")
                    widget.AnimTreeItem.AnimTreeItem.convert_to_anim_tree_item(child)

                child.to_xml(folder0, 1)
        return folder0