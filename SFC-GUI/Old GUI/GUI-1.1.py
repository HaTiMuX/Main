#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from math import sqrt
import re
from PyQt4 import QtGui, QtCore
import MySQLdb

db = MySQLdb.connect("localhost","sfcuser","sfc123","SFC")
cursor = db.cursor()
count=0

###########
#Functions#
###########
def Update_Add(Index, rowMap):
	SFMap = rowMap.lstrip('{')
	SFMap = SFMap.rstrip('}')
	SF_Map = SFMap.split(', ')
	print "New SF Map to add: " + str(SF_Map)
	for SF in SF_Map:
		if(SF==SF_Map[0]):
			try:
				#Reading locator of the first SF Node 
				sql1 = "SELECT ip FROM SFIP WHERE sf = '%s'" % (SF)
				cursor.execute(sql1)
			   	result = cursor.fetchone()
				IPx = result[0]
				
			except:
				print "Error: unable to read data from local server!"

			try:
				#Inserting new entry 
				sql = "INSERT INTO SFCRoutingTable (SF_MAP_INDEX, NextSFHop, Encap) VALUES ('%d','%s', NULL)" % (Index,IPx)
				print sql
				cursor.execute(sql)
				print "Adding data to local server: Success!"

			except:
				db.rollback()
				print "Error: unable to add data to local server!"


		print "Adding configuration for the SF Node embedding Function: %s" % SF 
		#Looking for the Locator of the next SF
		if(SF!=SF_Map[len(SF_Map)-1]):
			try:
				inext = SF_Map.index(SF) + 1
				sql1 = "SELECT ip FROM SFIP WHERE sf = '%s'" % (SF)
				sql2 = "SELECT ip FROM SFIP WHERE sf = '%s'" % SF_Map[inext] 
				cursor.execute(sql1)
			   	result = cursor.fetchone()
				IP = result[0] #Converting from tuple to normal string: SF node IP
				cursor.execute(sql2)
			   	result = cursor.fetchone()
				IPx = result[0] #Next SF Node IP
				print "Node IP = " + IP
			  	print "Next SF Hop @IP = " + IPx
				sql = "INSERT INTO SFCRoutingTable (SF_MAP_INDEX, NextSFHop, Encap) VALUES ('%d','%s', NULL)" % (Index,IPx)
			except:
				print "Error: unable to fecth data (IP addresses)"

		#Last node in the Map
		else: 
			try:
				sql1 = "SELECT ip FROM SFIP WHERE sf = '%s'" % (SF)
				cursor.execute(sql1)
			   	result = cursor.fetchone()
				IP = result[0] #SF node IP
				print "The Node is the last Node in the SF Map"
				sql = "INSERT INTO SFCRoutingTable (SF_MAP_INDEX, NextSFHop, Encap) VALUES ('%d', NULL, NULL)" % Index
			except:
				print "Error: unable to fecth data (IP addresses)"

		#Adding row to the remote table 'SFCRoutingTable' of the SF Node 
		try:
			remoteDB = MySQLdb.connect(IP,"sfcuser","sfc123","SFC")
			remoteCursor = remoteDB.cursor()
			try:
				remoteCursor.execute(sql)
				remoteDB.commit()
				print "Adding data to remote Node %s: Success!" % IP
			except:
				remoteDB.rollback()
				print "Error: unable to add data to remote server!"

			remoteDB.close()
		except:
			print "Error: connecting to remote server %s failed! (SFCRoutingTable add update failed)" % IP

		print ""


def Update_Del(Index, rowMap):
	SFMap = rowMap.lstrip('{')
	SFMap = SFMap.rstrip('}')
	SF_Map = SFMap.split(', ')

	sql = "DELETE FROM SFCRoutingTable WHERE SF_Map_Index=%d" % Index
	try:
		cursor.execute(sql)
		db.commit()
	except:
		db.rollback()
		print "Error: unable to remove data from local server"
	

	for SF in SF_Map:
		try:
			sql = "SELECT ip FROM SFIP WHERE sf = '%s'" % (SF)
			cursor.execute(sql)
			result = cursor.fetchone()
			IP = result[0] #SF node IP
		except:
				print "Error: unable to fecth data (IP addresses for remove)"

		#Deleting row from the remote table 'SFCRoutingTable' of the SF Node 
		try:
			sql = "DELETE FROM SFCRoutingTable WHERE SF_Map_Index=%d" % Index
			remoteDB = MySQLdb.connect(IP,"sfcuser","sfc123","SFC")
			remoteCursor = remoteDB.cursor()
			try:
				remoteCursor.execute(sql)
				remoteDB.commit()
				print "Removing data from remote Node %s: Success!" % IP
			except:
				remoteDB.rollback()
				print "Error: unable to remove data from remote server %d!" % IP

			remoteDB.close()
		except:
			print "Error: connecting to remote server %s failed!" % IP


##########################
##########Frames##########
##########################
class MainFrame(QtGui.QFrame):
	def __init__(self, parent):
        	super(MainFrame, self).__init__(parent)

	    	self.vbox = QtGui.QVBoxLayout(self)
		self.vbox.addWidget(self.ClassificationBox())
		self.vbox.addWidget(self.SFBox())
		self.vbox.addWidget(self.MapBox())
		self.setLayout(self.vbox)


    	def ClassificationBox(self):
        	groupBox = QtGui.QGroupBox("Classification")
		self.addRules = QtGui.QPushButton("Add &Rules",self)
		self.addRules.setToolTip('Add new classification rules')

		vbox = QtGui.QVBoxLayout()
		vbox.addWidget(self.addRules)
		groupBox.setLayout(vbox)

		return groupBox

    	def SFBox(self):
        	groupBox = QtGui.QGroupBox("SF Functions Management")
		self.addSF = QtGui.QPushButton("Add SF &Function",self)
		self.addSF.setToolTip('Add new Service Function')
		self.delSF = QtGui.QPushButton("Delete &SF Function",self)
		self.delSF.setToolTip('Delete Existing Service Function')

		vbox = QtGui.QVBoxLayout()
		vbox.addWidget(self.addSF)
		vbox.addWidget(self.delSF)
		groupBox.setLayout(vbox)

		return groupBox

	def MapBox(self):
		groupBox = QtGui.QGroupBox("SF Maps Management")
		vbox = QtGui.QVBoxLayout()

		self.addMap = QtGui.QPushButton("Add SF &Map",self)
		self.addMap.setToolTip('Add new SF Map')
		self.delMap = QtGui.QPushButton("&Delete SF Map",self)
		self.delMap.setToolTip('Delete an existing SF Map')
		#self.update = QtGui.QPushButton("&Update Configuration",self)
		#self.update.setToolTip('Update configuration of the SFC Network Nodes')

		vbox.addWidget(self.addMap)
		vbox.addWidget(self.delMap)
		#vbox.addWidget(self.update)
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

class addFunction_Frame(QtGui.QFrame):
	def __init__(self, parent):
        	super(addFunction_Frame, self).__init__(parent)

		#Box1
	    	hbox1 = QtGui.QHBoxLayout()
		self.func_l = QtGui.QLabel("SF Function")
       		self.func_le = QtGui.QLineEdit()
		self.func_le.setMaxLength(20)
		self.func_le.sizeHint()
		hbox1.addWidget(self.func_l)
		hbox1.addWidget(self.func_le)
        	hbox1.addStretch()

		#Box2
	    	hbox2 = QtGui.QHBoxLayout()
		self.loc_l = QtGui.QLabel("SF Locator  ")
       		self.loc_le = QtGui.QLineEdit()
		self.loc_le.setMaxLength(20)
		self.loc_le.sizeHint()
		#Restriction d'introduire une adresse IP
		hbox2.addWidget(self.loc_l)
		hbox2.addWidget(self.loc_le)
        	hbox2.addStretch()

		#Box3
	    	hbox3 = QtGui.QHBoxLayout()
       		self.back = QtGui.QPushButton("Back")
       		self.addFunc = QtGui.QPushButton("OK")
		hbox3.addWidget(self.back)
		hbox3.addWidget(self.addFunc)

		#Main Box
	    	self.vbox = QtGui.QVBoxLayout()
		self.vbox.addLayout(hbox1)
		self.vbox.addLayout(hbox2)
        	self.vbox.addStretch()
		self.vbox.addLayout(hbox3)
		self.setLayout(self.vbox)


class delFunction_Frame(QtGui.QFrame):
	def __init__(self, parent):
        	super(delFunction_Frame, self).__init__(parent)

		#HBox
	    	hbox = QtGui.QHBoxLayout()
       		self.back = QtGui.QPushButton("Back")
       		self.delFunc = QtGui.QPushButton("Delete")
		hbox.addWidget(self.back)
		hbox.addWidget(self.delFunc)

		#Combo Box
		self.combo = QtGui.QComboBox(self)
		sql = "SELECT SF, Locator FROM Locators"			
		try:	
			cursor.execute(sql)
   			results = cursor.fetchall()
		except:
   			print "Error: unable to fecth data"

		i=0
		while(i<len(results)):
			self.combo.addItem(str(results[i][0]) + " => " + str(results[i][1]))
			i+=1

		#Main Box
	    	self.vbox = QtGui.QVBoxLayout()
		self.label = QtGui.QLabel("Choose the SF Function to delete:", self)
		self.vbox.addWidget(self.label)
		self.vbox.addWidget(self.combo)
		self.vbox.addStretch()
		self.vbox.addLayout(hbox)
		self.setLayout(self.vbox)


class addMap_Frame(QtGui.QFrame):
	def __init__(self, parent):
        	super(addMap_Frame, self).__init__(parent)

		#Box1
	    	hbox1 = QtGui.QHBoxLayout()
		self.index_l = QtGui.QLabel("SF_Map_Index")
		self.msg = QtGui.QLabel("")
       		self.index_le = QtGui.QLineEdit()
		self.index_le.setMaxLength(4)
		self.index_le.sizeHint()
		hbox1.addWidget(self.index_l)
		hbox1.addWidget(self.index_le)
		hbox1.addWidget(self.msg)
        	hbox1.addStretch()

		#Box3
	    	hbox3 = QtGui.QHBoxLayout()
       		self.back = QtGui.QPushButton("Back")
       		self.addMap = QtGui.QPushButton("OK")
		hbox3.addWidget(self.back)
		hbox3.addWidget(self.addMap)


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

	def SFCheckList(self):
		groupBox = QtGui.QGroupBox("SF Functions List")
		groupBox.setFlat(True)

		#Reading supported SF functions
		try:
			sql = "SELECT SF FROM Locators"
			cursor.execute(sql)
			results = cursor.fetchall()
		except:
			print "Error: unable to fecth data (SF Functions)"

		self.checkBox = []
		SFs = []
		for SF in results:
			SFs.append(SF[0])
			self.checkBox.append(QtGui.QCheckBox(SF[0])) 
		

		l = sqrt(len(SFs))
		if(l!=int(l)):
			l= int(l) + 1

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


class delMap_Frame(QtGui.QFrame):
	def __init__(self, parent):
        	super(delMap_Frame, self).__init__(parent)

		#HBox
	    	hbox = QtGui.QHBoxLayout()
       		self.back = QtGui.QPushButton("Back")
       		self.delMap = QtGui.QPushButton("Delete")
		hbox.addWidget(self.back)
		hbox.addWidget(self.delMap)

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
		self.addFuncFrame = addFunction_Frame(QtGui.QFrame(self))
		self.delFuncFrame = delFunction_Frame(QtGui.QFrame(self))
		self.addMapFrame = addMap_Frame(QtGui.QFrame(self))
		self.delMapFrame = delMap_Frame(QtGui.QFrame(self))


		self.central_widget = QtGui.QStackedWidget()
       		self.central_widget.addWidget(self.mainFrame)
       		self.central_widget.addWidget(self.rulesFrame)
       		self.central_widget.addWidget(self.addFuncFrame)
       		self.central_widget.addWidget(self.delFuncFrame)
       		self.central_widget.addWidget(self.addMapFrame)
       		self.central_widget.addWidget(self.delMapFrame)
		self.central_widget.setCurrentWidget(self.mainFrame)
		self.setCentralWidget(self.central_widget)

		####################
		#Events connections#
		####################
		#Main Frame
		self.mainFrame.addRules.clicked.connect(self.addRules_buttonClicked)
		self.mainFrame.addSF.clicked.connect(self.addSF_buttonClicked)  
		self.mainFrame.delSF.clicked.connect(self.delSF_buttonClicked)  
		self.mainFrame.addMap.clicked.connect(self.addSFC_buttonClicked) 
		self.mainFrame.delMap.clicked.connect(self.delSFC_buttonClicked) 


		#Rules Frame
		self.rulesFrame.back.clicked.connect(self.back_buttonClicked)   

		#Add Function Frame
		self.addFuncFrame.back.clicked.connect(self.back_buttonClicked)
		self.addFuncFrame.addFunc.clicked.connect(self.addFunc_buttonClicked)

		#Delete Function Frame
		self.delFuncFrame.back.clicked.connect(self.back_buttonClicked)
		self.delFuncFrame.delFunc.clicked.connect(self.delFunc_buttonClicked)

		#Add Map Frame
		self.addMapFrame.back.clicked.connect(self.back_buttonClicked)
		self.addMapFrame.addMap.clicked.connect(self.addMap_buttonClicked)
		for checkbox in self.addMapFrame.checkBox:
			checkbox.clicked.connect(self.checkBoxClicked) 

		#Delete Map Frame
		self.delMapFrame.back.clicked.connect(self.back_buttonClicked)
		self.delMapFrame.delMap.clicked.connect(self.delMap_buttonClicked)
                                                        
		###################
		#Window Parameters#
		###################
		QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10)) 
		self.setWindowIcon(QtGui.QIcon('network.png')) 
		self.setGeometry(300, 300, 300, 200)
		self.setWindowTitle('SFC GUI')
		self.statusBar()


	def addRules_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.rulesFrame)

	def addSF_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.addFuncFrame)

	def delSF_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.delFuncFrame)

	def addSFC_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.addMapFrame)

	def delSFC_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.delMapFrame)

	def SFCupdate_buttonClicked(self):
		#Run python script
		print ""

	def back_buttonClicked(self): 
		self.central_widget.setCurrentWidget(self.mainFrame)

	def addFunc_buttonClicked(self): #Adding an existing SF Function
		print ""

	def delFunc_buttonClicked(self): #Deleting an existing SF Function
		print ""

	def delMap_buttonClicked(self): #Deleting an existing SF Map
		try:
			index = self.delMapFrame.combo.currentText().split(" ")
			index = index[0]
			SFMap = str(self.delMapFrame.combo.currentText()) #Strip the index 
			SFMap = SFMap.lstrip(str(index) + " ")

			reply = QtGui.QMessageBox.question(self, 'Message',
				"Are you sure to delete the selected SF Map?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

			if reply == QtGui.QMessageBox.Yes:
				sql = "DELETE FROM SFMaps WHERE SF_Map_Index=%d" % int(index)
				index = self.delMapFrame.combo.currentIndex()	
				self.delMapFrame.combo.removeItem(index)

				try:	
					cursor.execute(sql)
		   			db.commit()
				except:
	  				db.rollback()
					print "Error Deleting"

				#Updating SFC Routing Tables of the Nodes involved in the deleted SF Map
				Update_Del(int(index), SFMap)

		except ValueError:
			print "No remaining SF Map"
			#Message Box to be added Later


	def addMap_buttonClicked(self):
		text = self.addMapFrame.index_le.text()
		exp = r"^[0-99]"
		if re.search(exp, text) is None:
			self.addMapFrame.msg.setText("Type a number!")
			self.addMapFrame.msg.setStyleSheet('color: red')


		else:
			self.addMapFrame.msg.setText("")
			index = int(text)
			text = str(self.addFrame.SFLabel.text()) 
			chaine = text.split('{')
			newSFMap = '{' + chaine[1]

			#Checking if the SF_Map_index already exists
			sql = "SELECT SF_MAP_INDEX FROM SFMaps WHERE SF_MAP_INDEX=%d" % int(index)
			try:	
				cursor.execute(sql)
	   			result = cursor.fetchone()
			except:
				print "Error While Testing if the typed SF_Map_Index already exists!!"

			if result is None:
				reply = QtGui.QMessageBox.question(self, 'Message',
				"Do you really want to add this new SF Map?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

				if reply == QtGui.QMessageBox.Yes:
					sql = "INSERT INTO SFMaps (SF_MAP_INDEX, SFMap) VALUES (%d, '%s')" % (index, newSFMap)
					try:	
						cursor.execute(sql)
			   			db.commit()
					except:
			  			db.rollback()
						print "Error Adding new SF Map"
	

					self.delMapFrame.combo.addItem(str(index) + " " + newSFMap)

					#Updating SFC Routing Tables of the Nodes involved in the new SF Map
					Update_Add(index, newSFMap)

			else:
				self.addMapFrame.msg.setText("Index already exists!")
				self.addMapFrame.msg.setStyleSheet('color: red')
				print "SF_Map_Index already exists!! Try again."
		

	def checkBoxClicked(self):
		global count
        	sender = self.sender()
		ltext = str(self.addMapFrame.SFLabel.text())

		if sender.isChecked() is True:
			if(count==0):
				self.addMapFrame.SFLabel.setText("New SF Map:  " + "{" + sender.text() + "}")

			else:
				ltext = ltext.rstrip('}')
				self.addMapFrame.SFLabel.setText(ltext + ", " + sender.text() + "}")

			count+=1
		else:
			count-=1
			if(count==0):
				self.addMapFrame.SFLabel.setText("New SF Map:  ")
			else:
 				ltext = ltext.replace(", " + sender.text(), "")
 				ltext = ltext.replace(sender.text() + ", ", "")
				self.addMapFrame.SFLabel.setText(ltext)

def main():
    
	app = QtGui.QApplication(sys.argv)
   	mainw = MainWindow()
   	mainw.show()
   	sys.exit(app.exec_())
	db.close()


if __name__ == '__main__':
    	main()
