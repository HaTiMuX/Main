#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from math import sqrt
import re
from PyQt4 import QtGui, QtCore
import MySQLdb

count=0


db = MySQLdb.connect("localhost","sfcuser","sfc123","SFC")
cursor = db.cursor()

DSCP = []
i=1
while(i<=63):
	DSCP.append(i)
	i += 1

sql = "SELECT SF_MAP_INDEX FROM SFMaps"
try:	
	cursor.execute(sql)
	results = cursor.fetchall()
	for val in results:
		DSCP.remove(val[0])
except:
	print "Error updating DSCP available values!!"

print DSCP


###########
#Functions#
###########
def Update_Add(Index, rowMap):
	SFMap = rowMap.lstrip('{')
	SFMap = SFMap.rstrip('}')
	SF_Map = SFMap.split(', ')
	print "New SF Map to add: " + str(SF_Map) + "\n"

	#Adding configuration to the Ingress Node
	SF = SF_Map[0]
	try:
		#Reading locator of the first SF Node 
		sql1 = "SELECT Locator1 FROM Locators WHERE SF = '%s'" % (SF)
		cursor.execute(sql1)
		result = cursor.fetchone()
		IPx = result[0]
				
	except:
		print "Error: unable to read data from the local server!"


	try:
		remoteDB = MySQLdb.connect("10.1.0.99","sfcuser","sfc123","SFC") #IP address of the Ingress Node
		remoteCursor = remoteDB.cursor()
		try:
			#Inserting new entry 
			sql = "INSERT INTO SFCRoutingTable (SF_MAP_INDEX, NextSFHop, Encap) VALUES (%d,'%s', NULL)" % (Index,IPx)
			remoteCursor.execute(sql)
			remoteDB.commit()
			print "Adding data to the Ingress Node: Success!"
		except:
			print sql
			remoteDB.rollback()
			print "Error: unable to add data to the Ingress Node!"
			remoteDB.close()

		remoteDB.close()
	except:
		print "Error: connecting to remote server %s failed! (SFCRoutingTable add update failed)" % IP

	print ""


	#Adding configuration to the Involved Nodes
	for SF in SF_Map:
		print "Adding configuration to the SF Node embedding Function: %s" % SF 
		#Looking for the Locator of the next SF
		if(SF!=SF_Map[len(SF_Map)-1]):
			try:
				sql1 = "SELECT Locator1 FROM Locators WHERE sf = '%s'" % (SF)
				sql2 = "SELECT Locator1 FROM Locators WHERE sf = '%s'" % SF_Map[SF_Map.index(SF) + 1] 
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
				sql1 = "SELECT Locator1 FROM Locators WHERE sf = '%s'" % (SF)
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
				print sql
				remoteCursor.execute(sql)
				remoteDB.commit()
				print "Adding data to remote Node %s: Success!" % IP
			except:
				remoteDB.rollback()
				print "Error: unable to add data to remote Node %s!" % IP
				remoteDB.close()

			remoteDB.close()
		except:
			print "Error: connecting to remote server %s failed! (SFCRoutingTable add update failed)" % IP

		print ""


def Update_Del(Index, rowMap):
	SFMap = rowMap.lstrip('{')
	SFMap = SFMap.rstrip('}')
	SF_Map = SFMap.split(', ')

	#Deleting row from the 'SFCRoutingTable' of the Ingress Node
	try:
		remoteDB = MySQLdb.connect("10.1.0.99","sfcuser","sfc123","SFC") #IP address of the Ingress Node
		remoteCursor = remoteDB.cursor()
		sql = "DELETE FROM SFCRoutingTable WHERE SF_Map_Index=%d" % Index
		try:
			print sql
			remoteCursor.execute(sql)
			remoteDB.commit()
			print "Deleting data from the Ingress Node: Success!"
		except:
			remoteDB.rollback()
			print "Error: unable to delete data from the Ingress Node!"
			remoteDB.close()

		remoteDB.close()
	except:
		print "Error: connecting to the Ingress Node failed! (SFCRoutingTable delete update failed)"
	

	#Deleting row from the remote 'SFCRoutingTable' of each SF Node 
	for SF in SF_Map:
		try:
			sql = "SELECT Locator1 FROM Locators WHERE SF = '%s'" % (SF)
			cursor.execute(sql)
			result = cursor.fetchone()
			IP = result[0] #SF node IP
		except:
			print "Error: unable to fecth data (IP addresses for remove)"

		try:
			sql = "DELETE FROM SFCRoutingTable WHERE SF_Map_Index=%d" % Index
			remoteDB = MySQLdb.connect(IP,"sfcuser","sfc123","SFC")
			remoteCursor = remoteDB.cursor()
			try:
				print sql
				remoteCursor.execute(sql)
				remoteDB.commit()
				print "Removing data from remote Node %s: Success!" % IP
			except:
				remoteDB.rollback()
				print "Error: unable to remove data from remote server %d!" % IP
				remoteDB.close()

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
		self.addRule = QtGui.QPushButton("Add &Rules",self)
		self.addRule.setToolTip('Add new classification rule')
		self.delRule = QtGui.QPushButton("&Delete Rules",self)
		self.delRule.setToolTip('Delete an existing rule')

		vbox = QtGui.QVBoxLayout()
		vbox.addWidget(self.addRule)
		vbox.addWidget(self.delRule)
		groupBox.setLayout(vbox)

		return groupBox

    	def SFBox(self):
        	groupBox = QtGui.QGroupBox("SF Functions Management")
		self.addSF = QtGui.QPushButton("Add SF &Function",self)
		self.addSF.setToolTip('Add new Service Function')
		self.delSF = QtGui.QPushButton("Delete &SF Function",self)
		self.delSF.setToolTip('Delete Existing Service Function')
		self.updateSF = QtGui.QPushButton("&Update Locators",self)
		self.updateSF.setToolTip('Update Locator of an existing SF Function')

		vbox = QtGui.QVBoxLayout()
		vbox.addWidget(self.addSF)
		vbox.addWidget(self.delSF)
		vbox.addWidget(self.updateSF)
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

class addRule_Frame(QtGui.QFrame):
	def __init__(self, parent):
        	super(addRule_Frame, self).__init__(parent)

	    	self.vbox = QtGui.QVBoxLayout(self)

		#Grid Layout
       		grid = QtGui.QGridLayout()
		rules_IP_l = QtGui.QLabel("IP Source")
       		self.rules_IP_le = QtGui.QLineEdit()
		rules_port_l = QtGui.QLabel("Destination Port")
       		self.rules_port_le = QtGui.QLineEdit()

		grid.addWidget(rules_IP_l, 0, 0)
		grid.addWidget(self.rules_IP_le, 0, 1)
		grid.addWidget(rules_port_l, 1, 0)
		grid.addWidget(self.rules_port_le, 1, 1)

		#HBox
	    	hbox = QtGui.QHBoxLayout()
      		self.back = QtGui.QPushButton("Back")
       		self.addRule = QtGui.QPushButton("Add")
		hbox.addWidget(self.back)
		hbox.addWidget(self.addRule)

		#Combo Box
		self.combo = QtGui.QComboBox(self)
		sql = "SELECT SF_MAP_INDEX FROM SFMaps"			
		try:	
			cursor.execute(sql)
   			results = cursor.fetchall()
		except:
   			print "Error: unable to fecth data (SF_MAP_INDEX)"

		for result in results:
			self.combo.addItem(str(result[0]))

		self.error = QtGui.QLabel("")
		self.error.setStyleSheet('color: red')


 		#Main Box
		self.vbox.addLayout(grid)
		self.vbox.addWidget(self.combo)
		self.vbox.addWidget(self.error)
        	self.vbox.addStretch()
		self.vbox.addLayout(hbox)
		self.setLayout(self.vbox)


class delRule_Frame(QtGui.QFrame):
	def __init__(self, parent):
        	super(delRule_Frame, self).__init__(parent)

		#HBox
	    	hbox = QtGui.QHBoxLayout()
       		self.back = QtGui.QPushButton("Back")
       		self.delRule = QtGui.QPushButton("Delete")
		hbox.addWidget(self.back)
		hbox.addWidget(self.delRule)

		#Combo Box
		self.combo = QtGui.QComboBox(self)
		sql = "SELECT SF_MAP_INDEX, IP, port FROM Rules"			
		try:	
			cursor.execute(sql)
   			results = cursor.fetchall()
		except:
   			print "Error: unable to fecth data (Reading Rules)"

		for result in results:
			if(str(result[1])!= None):
				IP = "IP=" + str(result[1])

			if(str(result[2])!= None):
				port = "Port=" + str(result[2])

			self.combo.addItem(str(result[0]) + ": " + IP + ", " + port)
			IP = ""
			port = ""

		#Main Box
	    	self.vbox = QtGui.QVBoxLayout()
		self.label = QtGui.QLabel("Choose the Rule to delete:", self)
		self.vbox.addWidget(self.label)
		self.vbox.addWidget(self.combo)
		self.vbox.addStretch()
		self.vbox.addLayout(hbox)
		self.setLayout(self.vbox)

class addFunction_Frame(QtGui.QFrame):
	def __init__(self, parent):
        	super(addFunction_Frame, self).__init__(parent)

		#Grid Layout
       		grid = QtGui.QGridLayout()

		func_l = QtGui.QLabel("SF Function")
       		self.func_le = QtGui.QLineEdit()
		self.func_le.setMaxLength(30)

		loc1_l = QtGui.QLabel("SF Locator 1 ")
       		self.loc1_le = QtGui.QLineEdit()
		self.loc1_le.setMaxLength(15)

		loc2_l = QtGui.QLabel("SF Locator 2 ")
       		self.loc2_le = QtGui.QLineEdit()
		self.loc2_le.setMaxLength(15)

		loc3_l = QtGui.QLabel("SF Locator 3 ")
       		self.loc3_le = QtGui.QLineEdit()
		self.loc3_le.setMaxLength(15)

		grid.addWidget(func_l, 0, 0)
		grid.addWidget(self.func_le, 0, 1)
		grid.addWidget(loc1_l, 1, 0)
		grid.addWidget(self.loc1_le, 1, 1)
		grid.addWidget(loc2_l, 2, 0)
		grid.addWidget(self.loc2_le, 2, 1)
		grid.addWidget(loc3_l, 3, 0)
		grid.addWidget(self.loc3_le, 3, 1)

		#Box3
	    	hbox3 = QtGui.QHBoxLayout()
       		self.back = QtGui.QPushButton("Back")
       		self.addFunc = QtGui.QPushButton("OK")
		hbox3.addWidget(self.back)
		hbox3.addWidget(self.addFunc)

		#Main Box
		self.msg = QtGui.QLabel("")
		self.msg.setStyleSheet('color: red')
	    	self.vbox = QtGui.QVBoxLayout()
		self.vbox.addLayout(grid)
		self.vbox.addWidget(self.msg)
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
		sql = "SELECT SF, Locator1, Locator2, locator3 FROM Locators"			
		try:	
			cursor.execute(sql)
   			results = cursor.fetchall()
		except:
   			print "Error: unable to fecth data"

		for result in results:
			self.combo.addItem(str(result[0]))

		#Main Box
	    	self.vbox = QtGui.QVBoxLayout()
		self.label = QtGui.QLabel("Choose the SF Function to delete:", self)
		self.vbox.addWidget(self.label)
		self.vbox.addWidget(self.combo)
		self.vbox.addStretch()
		self.vbox.addLayout(hbox)
		self.setLayout(self.vbox)

class updateFunction_Frame(QtGui.QFrame):
	def __init__(self, parent):
        	super(updateFunction_Frame, self).__init__(parent)

		self.SFList = []
		self.loc1 = []
		self.loc2 = []
		self.loc3 = []

		#Grid
       		grid = QtGui.QGridLayout()

		newLoc1_l = QtGui.QLabel("New SF Locator 1 ")
       		self.newLoc1_le = QtGui.QLineEdit()
		self.newLoc1_le.setMaxLength(15)

		newLoc2_l = QtGui.QLabel("New SF Locator 2 ")
       		self.newLoc2_le = QtGui.QLineEdit()
		self.newLoc2_le.setMaxLength(15)

		newLoc3_l = QtGui.QLabel("New SF Locator 3 ")
       		self.newLoc3_le = QtGui.QLineEdit()
		self.newLoc3_le.setMaxLength(15)

		grid.addWidget(newLoc1_l, 0, 0)
		grid.addWidget(self.newLoc1_le, 0, 1)
		grid.addWidget(newLoc2_l, 1, 0)
		grid.addWidget(self.newLoc2_le, 1, 1)
		grid.addWidget(newLoc3_l, 2, 0)
		grid.addWidget(self.newLoc3_le, 2, 1)

		#HBox
	    	hbox = QtGui.QHBoxLayout()
       		self.back = QtGui.QPushButton("Back")
       		self.updateFunc = QtGui.QPushButton("Update")
		hbox.addWidget(self.back)
		hbox.addWidget(self.updateFunc)

		#Combo Box
		self.combo = QtGui.QComboBox(self)
		sql = "SELECT SF, Locator1, Locator2, Locator3, LocNum FROM Locators"
		try:	
			cursor.execute(sql)
   			results = cursor.fetchall()
		except:
   			print "Error: unable to fecth data"

		for result in results:
			self.SFList.append(str(result[0]))
			self.loc1.append(result[1])
			self.loc2.append(result[2])
			self.loc3.append(result[3])
			if result[4]==3:
				self.combo.addItem(str(result[0]) + " => " + str(result[1]) + "|" + str(result[2]) + "|" + str(result[3]))
			elif result[4]==2:	
				self.combo.addItem(str(result[0]) + " => " + str(result[1]) + "|" + str(result[2]))
			else:
				self.combo.addItem(str(result[0]) + " => " + str(result[1]))


		#Main Box
	    	self.vbox = QtGui.QVBoxLayout()
		self.msg = QtGui.QLabel("")
		self.msg.setStyleSheet('color: red')
		self.label = QtGui.QLabel("Choose the Entry to update:", self)
		self.vbox.addWidget(self.label)
		self.vbox.addWidget(self.combo)
		self.vbox.addLayout(grid)
		self.vbox.addWidget(self.msg)
		self.vbox.addStretch()
		self.vbox.addLayout(hbox)
		self.setLayout(self.vbox)


class addMap_Frame(QtGui.QFrame):
	def __init__(self, parent):
        	super(addMap_Frame, self).__init__(parent)

		#Box1
	    	hbox1 = QtGui.QHBoxLayout()
		self.index_l2 = QtGui.QLabel("SF_Map_Index")
		self.msg = QtGui.QLabel("")
		self.msg.setStyleSheet('color: red')
       		self.index_le = QtGui.QLineEdit()
		self.index_le.setMaxLength(2)
		self.index_le.sizeHint()
		self.index_le.setToolTip("Type the SF Map Index or just leave it empty \n(In this case, a new valid value is automatically affected)")
		hbox1.addWidget(self.index_l2)
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
		self.SFLabel = QtGui.QLabel("New SF Map: ", self)
       		self.resetMap = QtGui.QPushButton("Reset Map")
		self.vbox.addLayout(hbox1)
		self.vbox.addWidget(self.SFCheckList())
		self.vbox.addWidget(self.resetMap)
		self.vbox.addWidget(self.SFLabel)
        	hbox1.addStretch()
		self.vbox.addLayout(hbox3)
		self.setLayout(self.vbox)

	def SFCheckList(self):
		groupBox = QtGui.QGroupBox("SF Functions List")
       		self.grid = QtGui.QGridLayout()
		self.checkBoxList = [[], []]

		#Reading supported SF functions
		try:
			sql = "SELECT SF FROM Locators"
			cursor.execute(sql)
			results = cursor.fetchall()
		except:
			print "Error: unable to fecth data (SF Functions)"


		#Building the Checkbox List
		for SF in results:
			self.checkBoxList[0].append(QtGui.QCheckBox(SF[0])) 
			self.checkBoxList[1].append(SF[0])
		
		self.SFCheckListDisplay()
		groupBox.setLayout(self.grid)

		return groupBox
		
	def SFCheckListDisplay(self):
		l = sqrt(len(self.checkBoxList[0]))
		if(l!=int(l)):
			l= int(l) + 1

		i=0
		j=0
		for cb in self.checkBoxList[0]:
			self.grid.addWidget(cb, i, j)
			j+=1
			if(j==l):
				i+=1
				j=0
		




class delMap_Frame(QtGui.QFrame):
	def __init__(self, parent):
        	super(delMap_Frame, self).__init__(parent)

		self.SFMapIndexesList = []

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

		for result in results:
			self.SFMapIndexesList.append(result[0])
			self.combo.addItem(str(result[0]) + " " + str(result[1]))

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

		self.addRuleFrame = addRule_Frame(QtGui.QFrame(self))
		self.delRuleFrame = delRule_Frame(QtGui.QFrame(self))

		self.addFuncFrame = addFunction_Frame(QtGui.QFrame(self))
		self.delFuncFrame = delFunction_Frame(QtGui.QFrame(self))
		self.updateFuncFrame = updateFunction_Frame(QtGui.QFrame(self))

		self.addMapFrame = addMap_Frame(QtGui.QFrame(self))
		self.delMapFrame = delMap_Frame(QtGui.QFrame(self))



		self.central_widget = QtGui.QStackedWidget()
       		self.central_widget.addWidget(self.mainFrame)

       		self.central_widget.addWidget(self.addRuleFrame)
       		self.central_widget.addWidget(self.delRuleFrame)

       		self.central_widget.addWidget(self.addFuncFrame)
       		self.central_widget.addWidget(self.delFuncFrame)
       		self.central_widget.addWidget(self.updateFuncFrame)

       		self.central_widget.addWidget(self.addMapFrame)
       		self.central_widget.addWidget(self.delMapFrame)

		self.central_widget.setCurrentWidget(self.mainFrame)
		self.setCentralWidget(self.central_widget)

		####################
		#Events connections#
		####################
		#Main Frame
		self.mainFrame.addRule.clicked.connect(self.addRules_buttonClicked)
		self.mainFrame.delRule.clicked.connect(self.delRules_buttonClicked)

		self.mainFrame.addSF.clicked.connect(self.addSF_buttonClicked)  
		self.mainFrame.delSF.clicked.connect(self.delSF_buttonClicked)  
		self.mainFrame.updateSF.clicked.connect(self.updateSF_buttonClicked) 
 
		self.mainFrame.addMap.clicked.connect(self.addSFC_buttonClicked) 
		self.mainFrame.delMap.clicked.connect(self.delSFC_buttonClicked) 


		#Add Rule Frame
		self.addRuleFrame.back.clicked.connect(self.back_buttonClicked) 
		self.addRuleFrame.addRule.clicked.connect(self.addRule_buttonClicked)  
		#Delete Rule Frame
		self.delRuleFrame.back.clicked.connect(self.back_buttonClicked) 
		self.delRuleFrame.delRule.clicked.connect(self.delRule_buttonClicked)  


		#Add Function Frame
		self.addFuncFrame.back.clicked.connect(self.back_buttonClicked)
		self.addFuncFrame.addFunc.clicked.connect(self.addFunc_buttonClicked)
		#Delete Function Frame
		self.delFuncFrame.back.clicked.connect(self.back_buttonClicked)
		self.delFuncFrame.delFunc.clicked.connect(self.delFunc_buttonClicked)
		#Update Function Frame
		self.updateFuncFrame.back.clicked.connect(self.back_buttonClicked)
		self.updateFuncFrame.updateFunc.clicked.connect(self.updateFunc_buttonClicked)

		#Add Map Frame
		self.addMapFrame.resetMap.clicked.connect(self.resetMap_buttonClicked)
		self.addMapFrame.back.clicked.connect(self.back_buttonClicked)
		self.addMapFrame.addMap.clicked.connect(self.addMap_buttonClicked)
		for checkbox in self.addMapFrame.checkBoxList[0]:
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



	#********************#
	#*Main Frame FEvents*#
	#********************#
	def addRules_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.addRuleFrame)
		self.statusBar().showMessage("Adding Classification Rules",0)

	def delRules_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.delRuleFrame)
		self.statusBar().showMessage("Deleting Classification Rules",0)

	def addSF_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.addFuncFrame)
		self.statusBar().showMessage("Adding New SF Function",0)

	def delSF_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.delFuncFrame)
		self.statusBar().showMessage("Deleting an existing SF Function",0)

	def updateSF_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.updateFuncFrame)
		self.statusBar().showMessage("Updating an existing SF Function",0)

	def addSFC_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.addMapFrame)
		self.statusBar().showMessage("Adding New SF Map",0)

	def delSFC_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.delMapFrame)
		self.statusBar().showMessage("Deleting an existing SF Map",0)

	def back_buttonClicked(self): 
		self.central_widget.setCurrentWidget(self.mainFrame)
		self.statusBar().showMessage("Welcome Window",0)

	#******************************#
	#*Classification Rules FEvents*#
	#******************************#
	def addRule_buttonClicked(self): #Adding a new rule
		ruleIP = self.addRuleFrame.rules_IP_le.text()
		ruleport = self.addRuleFrame.rules_port_le.text()
		mark  = int(self.addRuleFrame.combo.currentText())
		IPexp = "^((25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)$"
		portExp = "^[0-9][0-9]?[0-9]?[0-9]?$"

		
		if(ruleIP=="" and ruleport==""):
			self.addRuleFrame.error.setText("fill at least one field for the rule!")

		elif (re.search(IPexp, ruleIP) is None) and ruleport=="":
			self.addRuleFrame.error.setText("Type a valid IP address!")
			
		elif (re.search(portExp, ruleport) is None) and ruleIP=="":
			self.addRuleFrame.error.setText("Type a valid Port Number!")

		elif (re.search(IPexp, ruleIP) is None) and (re.search(portExp, ruleport) is None):
			self.addRuleFrame.error.setText("Type valid Information!")

		else:
			reply = QtGui.QMessageBox.question(self, 'Confirmation', "Confirm add rule operation?",
				QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

			if reply == QtGui.QMessageBox.Yes:
				try:
					sql = "INSERT INTO Rules (SF_MAP_INDEX, IP, port) VALUES ('%d','%s', '%s')" % (mark, ruleIP, ruleport)
					cursor.execute(sql)
			   		db.commit()

				except:
			  		db.rollback()
					print "Error inserting New Rule"

	def delRule_buttonClicked(self): #Deleting an existing Rule
		if self.delRuleFrame.combo.count() != 0:
			curtext = self.delRuleFrame.combo.currentText()
			mark = curtext.split(':')
			msg = "Are you sure to delete the selected Entry?"
			reply = QtGui.QMessageBox.question(self, 'Confirmation', msg , QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
			'''
			if reply == QtGui.QMessageBox.Yes:
				sql = "DELETE FROM Rules WHERE SF_MAP_INDEX='%s'" % SF[0]
				try:	
					cursor.execute(sql)
			   		db.commit()
					index = self.delFuncFrame.combo.currentIndex()	
					self.delFuncFrame.combo.removeItem(index)
					self.updateFuncFrame.combo.removeItem(index)

	
				except:
	  				db.rollback()
					print "Error Deleting (Rule)"
			'''		
		else:
			QtGui.QMessageBox.critical(self, 'Error', "No Entry remaining!" , QtGui.QMessageBox.Ok)

	#***********************#
	#*SF Management FEvents*#
	#***********************#
	def addFunc_buttonClicked(self): #Adding a new SF Function
		locNum = 3
		sf = self.addFuncFrame.func_le.text()
		locator1 = self.addFuncFrame.loc1_le.text()
		locator2 = self.addFuncFrame.loc2_le.text()
		locator3 = self.addFuncFrame.loc3_le.text()
		SFExp = "^[a-z,A-Z]{2}[a-z,A-Z,0-9]?([a-z,A-Z,0-9,_]?){27}$"
		IPExp = "^((25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)$"
		emptyExp = "^( ?){15}$"

		IPCond1= re.search(IPExp, locator1) is not None
		IPCond2= re.search(IPExp, locator2) is not None
		IPCond3= re.search(IPExp, locator3) is not None
		emptyCond1 = re.search(emptyExp, locator1) is not None 
		emptyCond2 = re.search(emptyExp, locator2) is not None 
		emptyCond3 = re.search(emptyExp, locator3) is not None 
	
		if re.search(SFExp, sf) is not None:
			#Checking if the SF Function already exists
			sql = "SELECT SF FROM Locators WHERE SF='%s'" % sf
			try:	
				cursor.execute(sql)
		   		result = cursor.fetchone()
				if result is None:
					if IPCond1 is False:
						self.addFuncFrame.msg.setText("Type a valid IP address for the first locator!")

					elif ((IPCond2 is False) and (emptyCond2 is False)) or ((emptyCond2 is True) and (emptyCond3 is False)): 
						self.addFuncFrame.msg.setText("Type a valid IP address for the second locator!")

					elif IPCond3 is False and emptyCond3 is False:
						self.addFuncFrame.msg.setText("Type a valid IP address for the third locator!")

					else:
						self.addFuncFrame.msg.setText("")
						reply = QtGui.QMessageBox.question(self, 'Confirmation', "Confirm add operation?",
							QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
		

						if reply == QtGui.QMessageBox.Yes:
							try:
								if emptyCond3 is True:
									locator3 =""
									locNum -= 1
								if emptyCond2 is True:
									locator2 ="" 
									locNum -= 1

								sql = "INSERT INTO Locators (SF, Locator1, Locator2, Locator3, LocNum) VALUES ('%s', '%s', '%s', '%s', %d)" % (sf, locator1, locator2, locator3, locNum)
								cursor.execute(sql)
							   	db.commit()
					
								#Updating List of SF Functions and locators
								self.delFuncFrame.combo.addItem(sf)	
								if locNum==3:
									self.updateFuncFrame.combo.addItem(sf + " => " + locator1 + "|" + locator2 + "|" + locator3)
								elif locNum==2:	
									self.updateFuncFrame.combo.addItem(sf + " => " + locator1 + "|" + locator2)
								else:
									self.updateFuncFrame.combo.addItem(sf + " => " + locator1)



								#Updating List of available SF in the "Add Map Frame"
								self.addMapFrame.checkBoxList[0].append(QtGui.QCheckBox(sf)) 
								self.addMapFrame.checkBoxList[1].append(sf) 
								l = len(self.addMapFrame.checkBoxList[0])-1
								self.addMapFrame.checkBoxList[0][l].clicked.connect(self.checkBoxClicked) 
								self.addMapFrame.SFCheckListDisplay()

							except:
						  		db.rollback()
								print "Error inserting New SF-Locator"
				else:
					self.addFuncFrame.msg.setText("SF Function already exists!")
			except:
				print "Error Checking if the new SF Function already exists"
		else:
			self.addFuncFrame.msg.setText("Type a valid SF Function! (At least 2 letters)")
			#QtGui.QMessageBox.critical(self, 'Error', "No SF Function selected!" , QtGui.QMessageBox.Ok)

	def delFunc_buttonClicked(self): #Deleting an existing SF Function
		if self.delFuncFrame.combo.count() != 0:
			curtext = self.delFuncFrame.combo.currentText()
			SF = curtext.split(' ')
			removedSF = SF[0]
			indexesList = []
			print "SF Map to remove: " + removedSF + "\n"


			msg = "Are you sure to delete the selected Entry?"
			reply = QtGui.QMessageBox.question(self, 'Confirmation', msg , QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

			if reply == QtGui.QMessageBox.Yes:
				try:	

					#Updating the list of availble SF functions (SF Map add Frame)
					cb_index = self.addMapFrame.checkBoxList[1].index(removedSF) 
					self.addMapFrame.checkBoxList[0].pop(cb_index)
					self.addMapFrame.checkBoxList[1].pop(cb_index)
					self.addMapFrame.grid.itemAt(cb_index).widget().deleteLater()
					self.addMapFrame.SFCheckListDisplay()

					#Updating the list of availble SF functions to delete and update (SF Function del and update Frame)
					index = self.delFuncFrame.combo.currentIndex()	
					self.delFuncFrame.combo.removeItem(index)
					self.updateFuncFrame.combo.removeItem(index)

					#Removing associeted SFMaps
					sql = "SELECT SF_MAP_INDEX, SFMap FROM SFMaps";
					try:	
						cursor.execute(sql)
						results = cursor.fetchall()

						for result in results:
							index = int(result[0])
							rowMap = result[1]
							SFMap = rowMap.lstrip('{')
							SFMap = SFMap.rstrip('}')
							SF_Map = SFMap.split(', ')

							for SF in SF_Map:
								if SF==removedSF: 
									print "Deleting associated SF Map: %d %s" % (index, rowMap)
									#The SFMap is associated with the removed SF function
									#Deleting the associated SF Map and applying necessary updates

									#Updating DSCP available values
									DSCP.append(index) 

									#Updating List of availble SF Maps
									cb_index = self.delMapFrame.SFMapIndexesList.index(index) #getting index of the current map to remove
									self.delMapFrame.SFMapIndexesList.pop(cb_index)
									self.delMapFrame.combo.removeItem(cb_index)

									#Updating SFMaps database
									sql = "DELETE FROM SFMaps WHERE SF_Map_Index=%d" % index
									try:	
										cursor.execute(sql)
						   				db.commit()
									except:
					  					db.rollback()
										print "Error Deleting SF Map from the local repositry"

									#Updating SFC Routing Tables of the Nodes involved in the deleted SF Map
									Update_Del(index, rowMap)
									break;

					except:
						print "Error removing associeted SFMaps!" 



					#Updating SF Locators Database (Deleting the selected SF Function)
					sql = "DELETE FROM Locators WHERE SF='%s'" % removedSF
					print sql
					cursor.execute(sql)
			   		db.commit()


				except:
	  				db.rollback()
					print "Error Deleting SF Function"

		else:
			QtGui.QMessageBox.critical(self, 'Error', "No Entry remaining!" , QtGui.QMessageBox.Ok)

	def updateFunc_buttonClicked(self): #updating the locator of an existing SF Function
		if self.delFuncFrame.combo.count() != 0:
			#Preparing conditions
			cb_index = self.updateFuncFrame.combo.currentIndex()
			IPExp = "^((25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)$"
			emptyExp = "^( ?){15}$"
			error = None

			#reading SF Function to update
			curtext = self.updateFuncFrame.combo.currentText()
			SF = curtext.split(' ')
			updatedSF = SF[0]

			#Reading the number of locators of the SF Function to update
			try:	
				sql = "SELECT LocNum FROM Locators WHERE SF='%s'" % updatedSF
				cursor.execute(sql)
	   			result = cursor.fetchone()
			except:
	  			Error =  "Error: unable to fecth the number of SF's locators"
				print Error 
			locNum = result[0]

			#Preparing Database updates
			if locNum==1:
				newLoc1 = self.updateFuncFrame.newLoc1_le.text()
				IPCond1= re.search(IPExp, newLoc1) is not None
				emptyCond1 = re.search(emptyExp, newLoc1) is not None 

				print "Only the first locator can be updated"
				#lock other textfields
				if (IPCond1 is True) and (emptyCond1 is False):
					sql = "UPDATE Locators SET Locator1 = '%s' WHERE SF='%s'" % (newLoc1, updatedSF)
					self.updateFuncFrame.loc1[cb_index] = newLoc1
				else:
					error = "Type valid IP address for the first locator"

			elif locNum==2:
				newLoc1 = self.updateFuncFrame.newLoc1_le.text()
				newLoc2 = self.updateFuncFrame.newLoc2_le.text()
				self.updateFuncFrame.newLoc3_le.setDisabled(True)

				IPCond1= re.search(IPExp, newLoc1) is not None
				IPCond2= re.search(IPExp, newLoc2) is not None

				emptyCond1 = re.search(emptyExp, newLoc1) is not None 
				emptyCond2 = re.search(emptyExp, newLoc2) is not None 

				print "Both the first and the second locator can be updated"
				#lock other textfields
				if (IPCond1 is False) and (emptyCond1 is False):
					error = "Type valid IP address for the first locator"
				elif (IPCond2 is False) and (emptyCond2 is False):
					error =  "Type valid IP address for the second locator"
				elif (emptyCond1 is True) and (emptyCond2 is True):
					error = "Type at least one locator to update"
				else:
					if emptyCond1 is True:		
						sql = "UPDATE Locators SET Locator2 = '%s' WHERE SF='%s'" % (newLoc2, updatedSF)
						self.updateFuncFrame.loc2[cb_index] = newLoc2
					elif emptyCond2 is True:		
						sql = "UPDATE Locators SET Locator1 = '%s' WHERE SF='%s'" % (newLoc1, updatedSF)
						self.updateFuncFrame.loc1[cb_index] = newLoc1
					else:
						sql = "UPDATE Locators SET Locator2 = '%s', Locator2 = '%s' WHERE SF='%s'" % (newLoc1, newLoc2, updatedSF)
						self.updateFuncFrame.loc1[cb_index] = newLoc1
						self.updateFuncFrame.loc2[cb_index] = newLoc2
					
			elif locNum==3:
				newLoc1 = self.updateFuncFrame.newLoc1_le.text()
				newLoc2 = self.updateFuncFrame.newLoc2_le.text()
				newLoc3 = self.updateFuncFrame.newLoc3_le.text()

				IPCond1= re.search(IPExp, newLoc1) is not None
				IPCond2= re.search(IPExp, newLoc2) is not None
				IPCond3= re.search(IPExp, newLoc3) is not None

				emptyCond1 = re.search(emptyExp, newLoc1) is not None 
				emptyCond2 = re.search(emptyExp, newLoc2) is not None 
				emptyCond3 = re.search(emptyExp, newLoc3) is not None
 
				print "All locators can be updated"
				if (IPCond1 is False) and (emptyCond1 is False):
					error = "Type valid IP address for the first locator"
				elif (IPCond2 is False) and (emptyCond2 is False):
					error = "Type valid IP address for the second locator"
				elif (IPCond3 is False) and (emptyCond3 is False):
					error = "Type valid IP address for the third locator"
				elif (emptyCond1 is True) and (emptyCond2 is True) and (emptyCond3 is True):
					error = "Type at least one locator to update"
				else:
					if emptyCond1 is True:		
						if emptyCond2 is True:		
							sql = "UPDATE Locators SET Locator3 = '%s' WHERE SF='%s'" % (newLoc3, updatedSF)
							self.updateFuncFrame.loc3[cb_index] = newLoc3
						elif emptyCond3 is True:
							sql = "UPDATE Locators SET Locator2 = '%s' WHERE SF='%s'" % (newLoc2, updatedSF)
							self.updateFuncFrame.loc2[cb_index] = newLoc2
						else:
							sql = "UPDATE Locators SET Locator2 = '%s', Locator3 = '%s' WHERE SF='%s'" % (newLoc2, newLoc3, updatedSF)
							self.updateFuncFrame.loc2[cb_index] = newLoc2
							self.updateFuncFrame.loc3[cb_index] = newLoc3

					elif emptyCond2 is True:
						if emptyCond3 is True:				
							sql = "UPDATE Locators SET Locator1 = '%s' WHERE SF='%s'" % (newLoc1, updatedSF)
							self.updateFuncFrame.loc1[cb_index] = newLoc1
						else: 
							sql = "UPDATE Locators SET Locator1 = '%s', Locator3 = '%s' WHERE SF='%s'" % (newLoc1, newLoc3, updatedSF)
							self.updateFuncFrame.loc1[cb_index] = newLoc1
							self.updateFuncFrame.loc3[cb_index] = newLoc3

					elif emptyCond3 is True:
						sql = "UPDATE Locators SET Locator1 = '%s', Locator2 = '%s' WHERE SF='%s'" % (newLoc1, newLoc2, updatedSF)
						self.updateFuncFrame.loc1[cb_index] = newLoc1
						self.updateFuncFrame.loc2[cb_index] = newLoc2
					else:
						sql = "UPDATE Locators SET Locator1 = '%s', Locator2 = '%s', Locator3 = '%s' WHERE SF='%s'" % (newLoc1, newLoc2, newLoc3, updatedSF)
						self.updateFuncFrame.loc1[cb_index] = newLoc1
						self.updateFuncFrame.loc2[cb_index] = newLoc2
						self.updateFuncFrame.loc3[cb_index] = newLoc3

			if error is None:
				self.updateFuncFrame.msg.setText("")
				msg = "Are you sure to update the selected Entry?"
				reply = QtGui.QMessageBox.question(self, 'Confirmation', msg , QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

				if reply == QtGui.QMessageBox.Yes:
					try:
						cursor.execute(sql)
				   		db.commit()
					except:
		  				db.rollback()
						print "Error Updating SF Locators"

					#Updating List of SF Functions and locators
					if locNum==3:
						self.updateFuncFrame.combo.setItemText(cb_index, updatedSF + " => " + self.updateFuncFrame.loc1[cb_index] + "|" + self.updateFuncFrame.loc2[cb_index] + "|" + self.updateFuncFrame.loc3[cb_index])
					elif locNum==2:	
						self.updateFuncFrame.combo.setItemText(cb_index, updatedSF + " => " + self.updateFuncFrame.loc1[cb_index] + "|" + self.updateFuncFrame.loc2[cb_index])
					else:
						self.updateFuncFrame.combo.setItemText(cb_index, updatedSF + " => " + self.updateFuncFrame.loc1[cb_index])

			else:
				self.updateFuncFrame.msg.setText(error)
		else:
			QtGui.QMessageBox.critical(self, 'Error', "No Entry remaining!" , QtGui.QMessageBox.Ok)

	#****************************#
	#*SF Maps Management FEvents*#
	#****************************#
	def resetMap_buttonClicked(self):
		global count
		count=0
		self.addMapFrame.SFLabel.setText("New SF Map:  ")
		for checkbox in self.addMapFrame.checkBoxList[0]:
			checkbox.setCheckState(0)


	def delMap_buttonClicked(self): #Deleting an existing SF Map
		if self.delMapFrame.combo.count() != 0:
			curtext = str(self.delMapFrame.combo.currentText()) #Converting to str to use lstrip 

			text = curtext.split(" ")
			mapIndex = text[0]

			SFMap = curtext.lstrip(str(mapIndex) + " ") #Strip the Map index 
			SF = curtext.split(' ')

			msg = "Are you sure to delete the selected Entry?"
			reply = QtGui.QMessageBox.question(self, 'Confirmation', msg , QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

			if reply == QtGui.QMessageBox.Yes:
				print "Map to delete: " + curtext
				DSCP.append(mapIndex) #Updating DSCP available values
				sql = "DELETE FROM SFMaps WHERE SF_Map_Index=%d" % int(mapIndex)
				cb_index = self.delMapFrame.combo.currentIndex()	
				self.delMapFrame.combo.removeItem(cb_index)

				try:	
					cursor.execute(sql)
		   			db.commit()
				except:
	  				db.rollback()
					print "Error Deleting SF Map from the local repositry"

				#Updating SFC Routing Tables of the Nodes involved in the deleted SF Map
				Update_Del(int(mapIndex), SFMap)

		else:
			QtGui.QMessageBox.critical(self, 'Error', "No Entry remaining!" , QtGui.QMessageBox.Ok)




	def addMap_buttonClicked(self):
		if(count!=0):
			index_text = self.addMapFrame.index_le.text()
			#DSCPexp = "^([0-4,8]|[1-3][0,2,4,6,8]|4[0,4,6,8]|56)$"
			DSCPexp = "^([1-9]|[1-5][0-9]|6[0-3])$"
			if(index_text==""):
				try:
					#Preparing the new SF Map
					index = DSCP[0]
					DSCP.remove(DSCP[0]) #Updating DSCP available values
					Map = str(self.addMapFrame.SFLabel.text()).split('{') #Cant split using space 
					newSFMap = "{" + Map[1]

					#Adding new SF Map on confirmation
					reply = QtGui.QMessageBox.question(self, 'Message',
					"Do you really want to add this new SF Map?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

					if reply == QtGui.QMessageBox.Yes:
						sql = "INSERT INTO SFMaps (SF_MAP_INDEX, SFMap) VALUES (%d, '%s')" % (index, newSFMap)
						print sql
						try:	
							cursor.execute(sql)
					   		db.commit()
						except:
					  		db.rollback()
							print "Error Adding new SF Map"
	
						self.delMapFrame.combo.addItem(str(index) + " " + newSFMap)

						#Updating SFC Routing Tables of the Nodes involved in the new SF Map
						Update_Add(index, newSFMap)
				except:
					QtGui.QMessageBox.critical(self, 'Error', "No DSCP value remaining!" , QtGui.QMessageBox.Ok)


			elif re.search(DSCPexp, index_text) is None:
				self.addMapFrame.msg.setText("Type a valid\nDSCP value!")

			else:
				self.addMapFrame.msg.setText("")
				index = int(index_text) #Converting the typed number in the LineEdit to Integer
				Map = str(self.addMapFrame.SFLabel.text()).split('{') #Cant split using space 
				newSFMap = "{" + Map[1]

				#Checking if the SF_Map_index already exists
				sql = "SELECT SF_MAP_INDEX FROM SFMaps WHERE SF_MAP_INDEX=%d" % int(index)
				try:	
					cursor.execute(sql)
		   			result = cursor.fetchone()
					if result is None:
						DSCP.remove(index) #Updating DSCP available values
						#Adding new SF Map on confirmation
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
						#Printing Error: Index already exists
						self.addMapFrame.msg.setText("Index already exists!")
						print "SF_Map_Index already exists!! Try again."
				except:
					print "Error While Testing if the typed SF_Map_Index already exists!!"


		else:
			QtGui.QMessageBox.critical(self, 'Error', "No SF Function selected!" , QtGui.QMessageBox.Ok)

		

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