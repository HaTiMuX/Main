#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore
from math import sqrt
import MySQLdb

db = MySQLdb.connect("localhost","sfcuser","sfc123","SFC")
cursor = db.cursor()
count=0

class MainFrame(QtGui.QFrame):
	def __init__(self, parent):
        	super(MainFrame, self).__init__(parent)

	    	self.vbox = QtGui.QVBoxLayout(self)
		self.vbox.addWidget(self.ClassificationBox())
		self.vbox.addWidget(self.SFCBox())
		self.setLayout(self.vbox)


    	def ClassificationBox(self):
        	groupBox = QtGui.QGroupBox("Classification")
		self.addRules = QtGui.QPushButton("Add &Rules",self)
		self.addRules.setToolTip('Add new classification rules')

		vbox = QtGui.QVBoxLayout()
		vbox.addWidget(self.addRules)
		groupBox.setLayout(vbox)

		return groupBox

	def SFCBox(self):
		groupBox = QtGui.QGroupBox("SFC Management")
		vbox = QtGui.QVBoxLayout()

		self.add = QtGui.QPushButton("Add SF &Map",self)
		self.add.setToolTip('Add new SF Map')
		self.delete = QtGui.QPushButton("&Delete SF Map",self)
		self.delete.setToolTip('Delete an existing SF Map')
		self.update = QtGui.QPushButton("&Update Configuration",self)
		self.update.setToolTip('Update configuration of the SFC Network Nodes')

		vbox.addWidget(self.add)
		vbox.addWidget(self.delete)
		vbox.addWidget(self.update)
		groupBox.setLayout(vbox)

        	return groupBox

class Rules_Frame(QtGui.QFrame):
	def __init__(self, parent):
        	super(Rules_Frame, self).__init__(parent)

	    	self.vbox = QtGui.QVBoxLayout(self)
		self.rules_l = QtGui.QLabel("Here you can add calssification rules!\nNot available right now!!!")
       		self.back = QtGui.QPushButton("Back")
		self.vbox.addWidget(self.rules_l)
		self.vbox.addWidget(self.back)
		self.setLayout(self.vbox)

class SFCadd_Frame(QtGui.QFrame):
	def __init__(self, parent):
        	super(SFCadd_Frame, self).__init__(parent)
    		#self.signal = QtCore.pyqtSignal() 

		#Box1
	    	hbox1 = QtGui.QHBoxLayout()
		self.index_l = QtGui.QLabel("SF_Map_Index")
       		self.index_le = QtGui.QLineEdit()
		hbox1.addWidget(self.index_l)
		hbox1.addWidget(self.index_le)
        	hbox1.addStretch()

		#Box3
	    	hbox3 = QtGui.QHBoxLayout()
       		self.back = QtGui.QPushButton("Back")
       		self.ok = QtGui.QPushButton("OK")
		hbox3.addWidget(self.back)
		hbox3.addWidget(self.ok)


		#Main Box
	    	self.vbox = QtGui.QVBoxLayout()
		self.Label = QtGui.QLabel("Select the SF Functions of the new SF Map:", self)
		self.SFLabel = QtGui.QLabel("New SF Map: ", self)
		self.vbox.addLayout(hbox1)
		self.vbox.addWidget(self.Label)
		self.vbox.addWidget(self.SFCheckList())
		self.vbox.addWidget(self.SFLabel)
		self.vbox.addLayout(hbox3)
		self.setLayout(self.vbox)

	'''def SFCheckList(self):
		groupBox = QtGui.QGroupBox("SF Functions List")
		groupBox.setFlat(True)

		model = QStandardItemModel()

		SFs = ['SF1','SF2','SF3','SF4','SF5','SF6','SF7','SF8']

		for SF in SFs:
			item = QStandardItem('%s' % SF)
			item.setCheckState(Qt.Unchecked)
			item.setCheckable(True)
			model.appendRow(item)

		self.view = QListView()
		self.view.setModel(model)
	    	box = QtGui.QVBoxLayout()
		box.addWidget(self.view)
		groupBox.setLayout(box)

		return groupBox'''

	def SFCheckList(self):
		groupBox = QtGui.QGroupBox("SF Functions List")
		groupBox.setFlat(True)
		
		SFs = ['SF1','SF2','SF3','SF4','SF5','SF6','SF7','SF8']
		self.checkBox = []
		l = sqrt(len(SFs))

		if(l != int(l)):
			l= int(l) + 1

		i=0
		while(i<len(SFs)):
			self.checkBox.append(QtGui.QCheckBox(SFs[i]))
			i+=1
		i=0
		j=0
       		grid = QtGui.QGridLayout()
		for check in self.checkBox:
			grid.addWidget(check, i, j)
			j+=1
			if(j==l):
				i+=1
				j=0

		groupBox.setLayout(grid)

		return groupBox


class SFCdel_Frame(QtGui.QFrame):
	def __init__(self, parent):
        	super(SFCdel_Frame, self).__init__(parent)

		#HBox
	    	hbox = QtGui.QHBoxLayout()
       		self.back = QtGui.QPushButton("Back")
       		self.delete = QtGui.QPushButton("Delete")
		hbox.addWidget(self.back)
		hbox.addWidget(self.delete)

		#Combo Box
		self.combo = QtGui.QComboBox(self)
		sql = "SELECT SF_Map_Index, SFMap FROM SFMaps"			
		try:	
			cursor.execute(sql)
   			results = cursor.fetchall()
		except:
   			print "Error: unable to fecth data"

		i=0
		while(i<len(results)):
			self.combo.addItem(str(results[i][0]) + " {" + str(results[i][1]) + "}")
			i+=1

		#Main Box
	    	self.vbox = QtGui.QVBoxLayout()
		self.label = QtGui.QLabel("Choose the SF Map to delete:", self)
		self.vbox.addWidget(self.label)
		self.vbox.addWidget(self.combo)
		self.vbox.addStretch()
		self.vbox.addLayout(hbox)
		self.setLayout(self.vbox)


class MainWindow(QtGui.QMainWindow):

    	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)

		self.mainFrame = MainFrame(QtGui.QFrame(self))
		self.rulesFrame = Rules_Frame(QtGui.QFrame(self))
		self.addFrame = SFCadd_Frame(QtGui.QFrame(self))
		self.delFrame =	SFCdel_Frame(QtGui.QFrame(self))

		self.central_widget = QtGui.QStackedWidget()
       		self.central_widget.addWidget(self.mainFrame)
       		self.central_widget.addWidget(self.rulesFrame)
       		self.central_widget.addWidget(self.addFrame)
       		self.central_widget.addWidget(self.delFrame)
		self.central_widget.setCurrentWidget(self.mainFrame)
		self.setCentralWidget(self.central_widget)

		####################
		#Events connections#
		####################
		#Main Frame
		self.mainFrame.addRules.clicked.connect(self.addRules_buttonClicked)
		self.mainFrame.add.clicked.connect(self.SFCadd_buttonClicked)  
		self.mainFrame.delete.clicked.connect(self.SFCdel_buttonClicked) 
		self.mainFrame.update.clicked.connect(self.SFCupdate_buttonClicked)                     

		#Rules Frame
		self.rulesFrame.back.clicked.connect(self.back_buttonClicked)   

		#Add Frame
		self.addFrame.back.clicked.connect(self.back_buttonClicked)
		self.addFrame.ok.clicked.connect(self.addOK_buttonClicked)
		for checkbox in self.addFrame.checkBox:
			checkbox.clicked.connect(self.checkBoxClicked) 
   
		#Delete Frame
		self.delFrame.back.clicked.connect(self.back_buttonClicked)
		self.delFrame.delete.clicked.connect(self.del_buttonClicked)
                                                        
		###################
		#Window Parameters#
		###################
		QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10)) 
		self.setWindowIcon(QtGui.QIcon('network.png')) 
		self.setGeometry(300, 300, 300, 200)
		self.setWindowTitle('SFC Solution')
		self.statusBar()


	def addRules_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.rulesFrame)

	def SFCadd_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.addFrame)

	def SFCdel_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.delFrame)

	def SFCupdate_buttonClicked(self):
		#Run python script
		print ""

	def back_buttonClicked(self): 
		self.central_widget.setCurrentWidget(self.mainFrame)

	def del_buttonClicked(self, event): #Deleting an existing SF Map
		try:
			text = self.delFrame.combo.currentText().split(" ")
			sql = "DELETE FROM SFMaps WHERE SF_Map_Index=%d" % int(text[0])

			reply = QtGui.QMessageBox.question(self, 'Message',
				"Are you sure to delete the selected SF Map?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

			if reply == QtGui.QMessageBox.Yes:
				index = self.delFrame.combo.currentIndex()
				self.delFrame.combo.removeItem(index)

				try:	
					cursor.execute(sql)
		   			db.commit()
				except:
	  				db.rollback()
					print "Error Deleting"
		except ValueError:
			print "No remaining SF Map"
			#Message Box to be added Later


	def checkBoxClicked(self):
		global count
        	sender = self.sender()
		ltext = str(self.addFrame.SFLabel.text())

		if sender.isChecked() is True:
			if(count==0):
				self.addFrame.SFLabel.setText("{" + sender.text() + "}")

			else:
				ltext = ltext.rstrip('}')
				self.addFrame.SFLabel.setText(ltext + ", " + sender.text() + "}")

			count+=1
		else:
			count-=1
			if(count==0):
				self.addFrame.SFLabel.setText("")
			else:
 				ltext = ltext.replace(", " + sender.text(), "")
 				ltext = ltext.replace(sender.text() + ", ", "")
				self.addFrame.SFLabel.setText(ltext)


	def addOK_buttonClicked(self,Layout):
		index = self.addFrame.index_le.text()
		ltext = str(self.addFrame.SFLabel.text())

		reply = QtGui.QMessageBox.question(self, 'Message',
		        "Do you really want to add this new SF Map?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

		if reply == QtGui.QMessageBox.Yes:
			sql = "INSERT INTO SFMaps (SF_MAP_INDEX, SFMap) VALUES (%d, '%s')" % (int(index), ltext)
			print sql
			try:	
				cursor.execute(sql)
	   			db.commit()
			except:
	  			db.rollback()
				print "Error"

			self.delFrame.combo.addItem(index + " " + ltext)

def main():
    
	app = QtGui.QApplication(sys.argv)
   	mainw = MainWindow()
   	mainw.show()
   	sys.exit(app.exec_())
	db.close()


if __name__ == '__main__':
    	main()
