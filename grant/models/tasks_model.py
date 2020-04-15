""" Provides a proxy model to pick only the leaf tasks from the Tree Model """

from PyQt5.QtCore import QSortFilterProxyModel
from PyQt5.QtCore import Qt
# from PyQt5.QtCore import QModelIndex
from grant.models.task_matcher import TaskMatcher


class TasksModel(QSortFilterProxyModel):
    """ Filters the input TreeModel to a table model of only the tasks """

    def __init__(self):
        super(TasksModel, self).__init__()
        self.task_matcher = TaskMatcher()
        self.task_matcher.filters_updated.connect(self.invalidateFilter)

    def filterAcceptsRow(self, row, parent):  # pylint: disable=invalid-name
        """ Whether this row is part of the filtered view """

        index = self.sourceModel().index(row, 0, parent)
        if not index.isValid():
            return False

        node = index.internalPointer()
        if node.type != "task":
            return False

        return self.task_matcher.match(node.data)

    def setSourceModel(self, model):  # pylint: disable=invalid-name
        """ Connect to source model signals """
        super().setSourceModel(model)
        self.sourceModel().modelReset.connect(self.invalidate)
        self.sourceModel().dataChanged.connect(self.invalidate)

    def headerData(self, section, orientation, role):  # pylint: disable=invalid-name, no-self-use
        """ Set the header information """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole \
                and section == 0:
            return "Task List"
        return None

    def data(self, proxy_index, role):  # pylint: disable= no-self-use
        """ Return the data associated with the specific index for the role """
        index = self.mapToSource(proxy_index)
        if not index.isValid() or index.column() > 2:
            return None
        node = index.internalPointer()
        if role in [Qt.DisplayRole]:
            if index.column() == 0:
                return node.get_text()
            if index.column() == 1:
                return node.get_description()
            if index.column() == 2:
                return node.get_result()
        if role == Qt.FontRole:
            return node.get_font()
        return None
