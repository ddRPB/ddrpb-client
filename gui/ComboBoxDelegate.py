import sys

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtGui import QMainWindow


class ComboBoxDelegate(QtGui.QItemDelegate):

    def __init__(self, owner, itemlist):
        QtGui.QItemDelegate.__init__(self, owner)
        self.itemslist = itemlist


    def createEditor(self, parent, option, index):
        self.editor = QtGui.QComboBox(parent)

        for i in range(0, len(self.itemslist)):
            self.editor.addItem(str(self.itemslist[i]))

        self.editor.installEventFilter(self)
        self.connect(self.editor, QtCore.SIGNAL("currentIndexChanged(int)"), self.editorChanged)

        return self.editor


    def setEditorData(self, editor, index):
        value = index.data(QtCore.Qt.DisplayRole).toInt()[0]
        editor.setCurrentIndex(value)


    def setModelData(self, editor, model, index):
        # Puting index into model value
        #value = editor.currentIndex()

        # Puting string into model value
        value = editor.itemText(int(str(editor.currentIndex())))
        model.setData(index, QtCore.QVariant(value))


    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


    def paint(self, painter, option, index):

        value = index.data(QtCore.Qt.DisplayRole).toInt()[0]
        opt = QtGui.QStyleOptionComboBox()
        opt.text = str(self.itemslist[value])
        opt.rect = option.rect

        QtGui.QApplication.style().drawControl(QtGui.QStyle.CE_ItemViewItem, opt, painter)


    def editorChanged(self, index):
        check = self.editor.itemText(index)
        #check print