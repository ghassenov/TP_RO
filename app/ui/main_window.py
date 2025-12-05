# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDoubleSpinBox, QFormLayout, QFrame,
    QHBoxLayout, QHeaderView, QLabel, QMainWindow,
    QPushButton, QSizePolicy, QSpinBox, QTableWidget,
    QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.mainLayout = QHBoxLayout(self.centralwidget)
        self.mainLayout.setObjectName(u"mainLayout")
        self.leftPanel = QFrame(self.centralwidget)
        self.leftPanel.setObjectName(u"leftPanel")
        self.leftPanel.setFrameShape(QFrame.StyledPanel)
        self.leftLayout = QVBoxLayout(self.leftPanel)
        self.leftLayout.setObjectName(u"leftLayout")
        self.titleLabel = QLabel(self.leftPanel)
        self.titleLabel.setObjectName(u"titleLabel")
        font = QFont()
        font.setBold(True)
        self.titleLabel.setFont(font)

        self.leftLayout.addWidget(self.titleLabel)

        self.formWidget = QWidget(self.leftPanel)
        self.formWidget.setObjectName(u"formWidget")
        self.formLayout = QFormLayout(self.formWidget)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.lblMailboxes = QLabel(self.formWidget)
        self.lblMailboxes.setObjectName(u"lblMailboxes")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblMailboxes)

        self.spinMailboxes = QSpinBox(self.formWidget)
        self.spinMailboxes.setObjectName(u"spinMailboxes")
        self.spinMailboxes.setMinimum(1)
        self.spinMailboxes.setMaximum(999)
        self.spinMailboxes.setValue(3)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinMailboxes)

        self.lblRadius = QLabel(self.formWidget)
        self.lblRadius.setObjectName(u"lblRadius")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblRadius)

        self.spinRadius = QDoubleSpinBox(self.formWidget)
        self.spinRadius.setObjectName(u"spinRadius")
        self.spinRadius.setMinimum(0.100000000000000)
        self.spinRadius.setMaximum(9999.000000000000000)
        self.spinRadius.setValue(2.000000000000000)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinRadius)

        self.lblBudget = QLabel(self.formWidget)
        self.lblBudget.setObjectName(u"lblBudget")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lblBudget)

        self.spinBudget = QDoubleSpinBox(self.formWidget)
        self.spinBudget.setObjectName(u"spinBudget")
        self.spinBudget.setMinimum(0.000000000000000)
        self.spinBudget.setMaximum(1000000.000000000000000)
        self.spinBudget.setValue(1000.000000000000000)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinBudget)

        self.lblCoverageLevel = QLabel(self.formWidget)
        self.lblCoverageLevel.setObjectName(u"lblCoverageLevel")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lblCoverageLevel)

        self.spinCoverageLevel = QSpinBox(self.formWidget)
        self.spinCoverageLevel.setObjectName(u"spinCoverageLevel")
        self.spinCoverageLevel.setMinimum(1)
        self.spinCoverageLevel.setMaximum(10)
        self.spinCoverageLevel.setValue(1)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.spinCoverageLevel)


        self.leftLayout.addWidget(self.formWidget)

        self.lblDemand = QLabel(self.leftPanel)
        self.lblDemand.setObjectName(u"lblDemand")
        self.lblDemand.setFont(font)

        self.leftLayout.addWidget(self.lblDemand)

        self.tableDemand = QTableWidget(self.leftPanel)
        self.tableDemand.setObjectName(u"tableDemand")

        self.leftLayout.addWidget(self.tableDemand)

        self.lblMailboxParams = QLabel(self.leftPanel)
        self.lblMailboxParams.setObjectName(u"lblMailboxParams")
        self.lblMailboxParams.setFont(font)

        self.leftLayout.addWidget(self.lblMailboxParams)

        self.tableMailboxParams = QTableWidget(self.leftPanel)
        self.tableMailboxParams.setObjectName(u"tableMailboxParams")

        self.leftLayout.addWidget(self.tableMailboxParams)

        self.btnAddDemand = QPushButton(self.leftPanel)
        self.btnAddDemand.setObjectName(u"btnAddDemand")

        self.leftLayout.addWidget(self.btnAddDemand)

        self.btnAddMailboxParams = QPushButton(self.leftPanel)
        self.btnAddMailboxParams.setObjectName(u"btnAddMailboxParams")

        self.leftLayout.addWidget(self.btnAddMailboxParams)

        self.btnSolve = QPushButton(self.leftPanel)
        self.btnSolve.setObjectName(u"btnSolve")

        self.leftLayout.addWidget(self.btnSolve)

        self.status = QLabel(self.leftPanel)
        self.status.setObjectName(u"status")

        self.leftLayout.addWidget(self.status)


        self.mainLayout.addWidget(self.leftPanel)

        self.rightPanel = QFrame(self.centralwidget)
        self.rightPanel.setObjectName(u"rightPanel")
        self.rightPanel.setFrameShape(QFrame.StyledPanel)
        self.rightLayout = QVBoxLayout(self.rightPanel)
        self.rightLayout.setObjectName(u"rightLayout")
        self.lblResults = QLabel(self.rightPanel)
        self.lblResults.setObjectName(u"lblResults")
        self.lblResults.setFont(font)

        self.rightLayout.addWidget(self.lblResults)

        self.textResults = QTextEdit(self.rightPanel)
        self.textResults.setObjectName(u"textResults")
        self.textResults.setReadOnly(True)

        self.rightLayout.addWidget(self.textResults)

        self.graphWidget = QWidget(self.rightPanel)
        self.graphWidget.setObjectName(u"graphWidget")

        self.rightLayout.addWidget(self.graphWidget)


        self.mainLayout.addWidget(self.rightPanel)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Advanced Mailbox Location Optimizer", None))
        self.titleLabel.setText(QCoreApplication.translate("MainWindow", u"Input Parameters", None))
        self.lblMailboxes.setText(QCoreApplication.translate("MainWindow", u"Number of Mailboxes:", None))
        self.lblRadius.setText(QCoreApplication.translate("MainWindow", u"Radius:", None))
        self.lblBudget.setText(QCoreApplication.translate("MainWindow", u"Budget:", None))
        self.lblCoverageLevel.setText(QCoreApplication.translate("MainWindow", u"Max Coverage Level:", None))
        self.lblDemand.setText(QCoreApplication.translate("MainWindow", u"Demand Points (x, y, population, demand, priority)", None))
        self.lblMailboxParams.setText(QCoreApplication.translate("MainWindow", u"Mailbox Parameters (cost, capacity, fixed cost)", None))
        self.btnAddDemand.setText(QCoreApplication.translate("MainWindow", u"Add Demand Point", None))
        self.btnAddMailboxParams.setText(QCoreApplication.translate("MainWindow", u"Add Mailbox Parameter Row", None))
        self.btnSolve.setText(QCoreApplication.translate("MainWindow", u"Solve", None))
        self.status.setText(QCoreApplication.translate("MainWindow", u"Status: Ready", None))
        self.lblResults.setText(QCoreApplication.translate("MainWindow", u"Results", None))
    # retranslateUi

