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
DSCP = [1,2,3,4,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,44,46,48,56]
sql = "SELECT SF_MAP_INDEX FROM SFMaps"

try:	
	cursor.execute(sql)
	results = cursor.fetchall()
	for val in results:
		DSCP.remove(val[0]/4)
except:
	print "Error updating DSCP available values!!"


###########
#Functions#
###########
def Update_Add(Index, rowMap):
	SFMap = rowMap.lstrip('{')
	SFMap = SFMap.rstrip('}')
	SF_Map = SFMap.split(', ')
	print "New SF Map to add: " + str(SF_Map)
	for SF in SF_Map:
		#Adding configuration to the Ingress Node
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
				sql = "INSERT INTO SFCRoutingTable (SF_MAP_INDEX, NextSFHop, Encap) VALUES ('%d','%s', NULL)" % ((Index*4),IPx)
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
				sql1 = "SELECT ip FROM SFIP WHERE sf = '%s'" % (SF)
				sql2 = "SELECT ip FROM SFIP WHERE sf = '%s'" % SF_Map[SF_Map.index(SF) + 1] 
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

	#Deleting row from table 'SFCRoutingTable' of the Ingress Node
	sql = "DELETE FROM SFCRoutingTable WHERE SF_Map_Index=%d" % Index*4
	try:
		cursor.execute(sql)
		db.commit()
	except:
		db.rollback()
		print "Error: unable to remove data from local server"
	

	#Deleting row from the remote table 'SFCRoutingTable' for each SF Node 
	for SF in SF_Map:
		try:
			sql = "SELECT ip FROM SFIP WHERE sf = '%s'" % (SF)
			cursor.execute(sql)
			result = cursor.fetchone()
			IP = result[0] #SF node IP
		except:
			print "Error: unable to fecth data (IP addresses for remove)"

		try:
			sql = "DELETE FROM SFCRoutingTable WHERE SF_Map_Index=%d" % Index*4
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
		self.msg = QtGui.QLabel("")
	    	self.vbox = QtGui.QVBoxLayout()
		self.vbox.addLayout(hbox1)
		self.vbox.addLayout(hbox2)
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
		sql = "SELECT SF, Locator FROM Locators"			
		try:	
			cursor.execute(sql)
   			results = cursor.fetchall()
		except:
   			print "Error: unable to fecth data"

		for result in results:
			self.combo.addItem(str(result[0]) + " => " + str(result[1]))

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

		#Box1
	    	hbox1 = QtGui.QHBoxLayout()
		self.loc_l = QtGui.QLabel("New Locator")
       		self.loc_le = QtGui.QLineEdit()
		self.loc_le.setMaxLength(20)
		self.loc_le.sizeHint()
		hbox1.addWidget(self.loc_l)
		hbox1.addWidget(self.loc_le)
        	hbox1.addStretch()

		#HBox
	    	hbox = QtGui.QHBoxLayout()
       		self.back = QtGui.QPushButton("Back")
       		self.updateFunc = QtGui.QPushButton("Update")
		hbox.addWidget(self.back)
		hbox.addWidget(self.updateFunc)

		#Combo Box
		self.combo = QtGui.QComboBox(self)
		sql = "SELECT SF, Locator FROM Locators"			
		try:	
			cursor.execute(sql)
   			results = cursor.fetchall()
		except:
   			print "Error: unable to fecth data"

		for result in results:
			self.combo.addItem(str(result[0]) + " => " + str(result[1]))

		#Main Box
	    	self.vbox = QtGui.QVBoxLayout()
		self.msg = QtGui.QLabel("")
		self.label = QtGui.QLabel("Choose the Entry to update:", self)
		self.vbox.addWidget(self.label)
		self.vbox.addWidget(self.combo)
		self.vbox.addLayout(hbox1)
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
			self.combo.addItem(str(results[i][0]) + " " + str(results[i][1]))
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
		sf = self.addFuncFrame.func_le.text()
		locator = self.addFuncFrame.loc_le.text()
		IPexp = "^((25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)$"
	
		if(sf==""):
			self.addFuncFrame.msg.setText("Type a valid SF Function!")
			self.addFuncFrame.msg.setStyleSheet('color: red')
			#QtGui.QMessageBox.critical(self, 'Error', "No SF Function selected!" , QtGui.QMessageBox.Ok)

		elif re.search(IPexp, locator) is None:
			self.addFuncFrame.msg.setText("Type a valid IP address!")
			self.addFuncFrame.msg.setStyleSheet('color: red')

		else:
			self.addFuncFrame.msg.setText("")
			reply = QtGui.QMessageBox.question(self, 'Confirmation', "Confirm add operation?",
				QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

			if reply == QtGui.QMessageBox.Yes:

				try:
					sql = "INSERT INTO Locators (SF, Locator) VALUES ('%s', '%s')" % (sf, locator)
					cursor.execute(sql)
			   		db.commit()
					self.updateFuncFrame.combo.addItem(sf + " => " + locator)	
					self.delFuncFrame.combo.addItem(sf + " => " + locator)	

					self.addMapFrame.checkBoxList[0].append(QtGui.QCheckBox(sf)) 
					l = len(self.addMapFrame.checkBoxList[0])-1
					self.addMapFrame.checkBoxList[0][l].clicked.connect(self.checkBoxClicked) 
					self.addMapFrame.checkBoxList[1].append(sf) 

					self.addMapFrame.SFCheckListDisplay()

				except:
		  			db.rollback()
					print "Error inserting New SF"

	def delFunc_buttonClicked(self): #Deleting an existing SF Function
		if self.delFuncFrame.combo.count() != 0:
			curtext = self.delFuncFrame.combo.currentText()
			SF = curtext.split(' ')
			print str(SF[0])
			msg = "Are you sure to delete the selected Entry?"
			reply = QtGui.QMessageBox.question(self, 'Confirmation', msg , QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

			if reply == QtGui.QMessageBox.Yes:
				sql = "DELETE FROM Locators WHERE SF='%s'" % SF[0]

				cb_index = self.addMapFrame.checkBoxList[1].index(SF[0]) 
				print cb_index
				self.addMapFrame.checkBoxList[0].pop(cb_index)
				self.addMapFrame.checkBoxList[1].pop(cb_index)
				self.addMapFrame.grid.itemAt(cb_index).widget().deleteLater()
				self.addMapFrame.SFCheckListDisplay()

				try:	
					cursor.execute(sql)
			   		db.commit()
					index = self.delFuncFrame.combo.currentIndex()	
					self.delFuncFrame.combo.removeItem(index)
					self.updateFuncFrame.combo.removeItem(index)

	
				except:
	  				db.rollback()
					print "Error Deleting"
		else:
			QtGui.QMessageBox.critical(self, 'Error', "No Entry remaining!" , QtGui.QMessageBox.Ok)

	def updateFunc_buttonClicked(self): #updating the locator of an existing SF Function
		if self.delFuncFrame.combo.count() != 0:
			curtext = self.updateFuncFrame.combo.currentText()
			SF = curtext.split(' ')
			locator = self.updateFuncFrame.loc_le.text()

			IPexp = "^((25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)$"

			if re.search(IPexp, locator) is None:
				self.updateFuncFrame.msg.setText("Type a valid IP address!")
				self.updateFuncFrame.msg.setStyleSheet('color: red')

			else:
				self.updateFuncFrame.msg.setText("")
				msg = "Are you sure to update the selected Entry: '%s'?" % curtext
				reply = QtGui.QMessageBox.question(self, 'Confirmation', msg , QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

				if reply == QtGui.QMessageBox.Yes:
					sql = "UPDATE Locators SET Locator = '%s' WHERE SF='%s'" % (locator, SF[0])
					try:	
						cursor.execute(sql)
			   			db.commit()
						index = self.delFuncFrame.combo.currentIndex()	
						self.updateFuncFrame.combo.removeItem(index)
						self.updateFuncFrame.combo.addItem(SF[0]+ " => " + locator)
						self.delFuncFrame.combo.removeItem(index)
						self.delFuncFrame.combo.addItem(SF[0] + " => " + locator)

					except:
		  				db.rollback()
						print "Error Updating"
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
			index = text[0]
			print index

			SFMap = curtext.lstrip(str(index) + " ") #Strip the index 
			print SFMap
			SF = curtext.split(' ')

			msg = "Are you sure to delete the selected Entry: '%s'?" % curtext
			reply = QtGui.QMessageBox.question(self, 'Confirmation', msg , QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

			if reply == QtGui.QMessageBox.Yes:
				DSCP.append(index) #Appdating DSCP available values
				sql = "DELETE FROM SFMaps WHERE SF_Map_Index=%d" % int(index)
				index = self.delMapFrame.combo.currentIndex()	
				self.delMapFrame.combo.removeItem(index)

				try:	
					cursor.execute(sql)
		   			db.commit()
				except:
	  				db.rollback()
					print "Error Deleting SF Map"

				#Updating SFC Routing Tables of the Nodes involved in the deleted SF Map
				Update_Del(int(index), SFMap)

		else:
			QtGui.QMessageBox.critical(self, 'Error', "No Entry remaining!" , QtGui.QMessageBox.Ok)




	def addMap_buttonClicked(self):
		if(count!=0):
			index_text = self.addMapFrame.index_le.text()
			DSCPexp = "^([0-4,8]|[1-3][0,2,4,6,8]|4[0,4,6,8]|56)$"
			if(index_text==""):
				try:
					#Preparing the new SF Map
					index = DSCP[0]
					DSCP.remove(DSCP[0]) #Appdating DSCP available values
					Map = str(self.addMapFrame.SFLabel.text()).split('{') #Cant split using space 
					newSFMap = "{" + Map[1]

					#Adding new SF Map on confirmation
					reply = QtGui.QMessageBox.question(self, 'Message',
					"Do you really want to add this new SF Map?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

					if reply == QtGui.QMessageBox.Yes:
						sql = "INSERT INTO SFMaps (SF_MAP_INDEX, SFMap) VALUES (%d, '%s')" % ((index*4), newSFMap)
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
				self.addMapFrame.msg.setStyleSheet('color: red')

			else:
				self.addMapFrame.msg.setText("")
				index = int(index_text) #Converting the typed number in the LineEdit to Integer
				Map = str(self.addMapFrame.SFLabel.text()).split('{') #Cant split using space 
				newSFMap = "{" + Map[1]

				#Checking if the SF_Map_index already exists
				sql = "SELECT SF_MAP_INDEX FROM SFMaps WHERE SF_MAP_INDEX=%d" % (int(index)*4)
				try:	
					cursor.execute(sql)
		   			result = cursor.fetchone()
				except:
					print "Error While Testing if the typed SF_Map_Index already exists!!"

				if result is None:
					DSCP.remove(index) #Appdating DSCP available values
					#Adding new SF Map on confirmation
					reply = QtGui.QMessageBox.question(self, 'Message',
					"Do you really want to add this new SF Map?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

					if reply == QtGui.QMessageBox.Yes:
						sql = "INSERT INTO SFMaps (SF_MAP_INDEX, SFMap) VALUES (%d, '%s')" % (index*4, newSFMap)
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
					self.addMapFrame.msg.setStyleSheet('color: red')
					print "SF_Map_Index already exists!! Try again."
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




