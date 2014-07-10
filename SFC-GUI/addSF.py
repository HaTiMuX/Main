import re
from Functions import LocalLocators_Update
from PyQt4 import QtGui


#Adding a new SF Function
def addFunc(self, db, cursor): 
	error = 0
	locNum = 3
	SF = self.addFuncFrame.func_le.text()
	locator1 = self.addFuncFrame.loc1_le.text()
	locator2 = self.addFuncFrame.loc2_le.text()
	locator3 = self.addFuncFrame.loc3_le.text()
	description = self.addFuncFrame.desc_te.toPlainText()

	SFExp = "^[a-z,A-Z]{2}[a-z,A-Z,0-9]?([a-z,A-Z,0-9,_]?){27}$"
	IPExp = "^((25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)$"
	emptyExp = "^( ?){15}$"

	IPCond1= re.search(IPExp, locator1) is not None
	IPCond2= re.search(IPExp, locator2) is not None
	IPCond3= re.search(IPExp, locator3) is not None
	emptyCond1 = re.search(emptyExp, locator1) is not None 
	emptyCond2 = re.search(emptyExp, locator2) is not None 
	emptyCond3 = re.search(emptyExp, locator3) is not None 

	if re.search(SFExp, SF) is not None:
		#Checking if the SF Function already exists
		sql = "SELECT SF FROM Locators WHERE SF='%s'" % SF
		try:	
			cursor.execute(sql)
	   		result = cursor.fetchone()
		except:
			error = 1
			print "Error: Checking if the new SF Function already exists failed!"

		if (result is None) and (error==0):
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
					print "**** Adding New SF Function ****"

					#Adding New SF Function to the Locators Database
					try:
						if emptyCond3 is True:
							locator3 =""
							locNum -= 1
						if emptyCond2 is True:
							locator2 ="" 
							locNum -= 1
						sql = "INSERT INTO Locators (SF, Locator1, Locator2, Locator3, Description, LocNum) VALUES ('%s', '%s', '%s', '%s', '%s', %d)" % (SF, locator1, locator2, locator3, description, locNum)
						cursor.execute(sql)
					except:
						error = 1
						print "Adding New SF Function to local repository: Failed!"

					#Updating LocalLocators Databases of the SF Nodes + the Ingress Node
					error = LocalLocators_Update(SF, locator1, 1)
					if error==0:
						print "Updating LocalLocators: Success!"
					else:
						print "Error: Updating LocalLocators Failed!"
						
					if error==0:
						#Updating List of "delFuncFrame"
						self.delFuncFrame.combo.addItem(SF)	

						#Updating List of "addLocFrame" + "delLocFrame" + "updateLocFrame"
						self.addLocFrame.locators[0].append(SF)
						self.delLocFrame.locators[0].append(SF)
						self.updateLocFrame.locators[0].append(SF)

						self.addLocFrame.locators[1].append(locator1)
						self.delLocFrame.locators[1].append(locator1)
						self.updateLocFrame.locators[1].append(locator1)

						self.addLocFrame.locators[2].append(locator2)
						self.delLocFrame.locators[2].append(locator2)
						self.updateLocFrame.locators[2].append(locator2)

						self.addLocFrame.locators[3].append(locator3)
						self.delLocFrame.locators[3].append(locator3)
						self.updateLocFrame.locators[3].append(locator3)

						if locNum==3:
							self.addLocFrame.combo.addItem(SF + " => " + locator1 + "|" + locator2 + "|" + locator3)
							self.delLocFrame.combo.addItem(SF + " => " + locator1 + "|" + locator2 + "|" + locator3)
							self.updateLocFrame.combo.addItem(SF + " => " + locator1 + "|" + locator2 + "|" + locator3)
						if locNum==2:	
							self.addLocFrame.combo.addItem(SF + " => " + locator1 + "|" + locator2)
							self.delLocFrame.combo.addItem(SF + " => " + locator1 + "|" + locator2)
							self.updateLocFrame.combo.addItem(SF + " => " + locator1 + "|" + locator2)
						elif locNum==1:
							self.addLocFrame.combo.addItem(SF + " => " + locator1)
							self.delLocFrame.combo.addItem(SF + " => " + locator1)
							self.updateLocFrame.combo.addItem(SF + " => " + locator1)
		

						#Updating List of available SF in the "Add Map Frame"
						self.addMapFrame.checkBoxList[0].append(QtGui.QCheckBox(SF)) 
						self.addMapFrame.checkBoxList[1].append(SF) 
						l = len(self.addMapFrame.checkBoxList[0])-1
						self.addMapFrame.checkBoxList[0][l].clicked.connect(self.checkBoxClicked) 
						self.addMapFrame.SFCheckListDisplay()

						db.commit()
						print "Adding new SF Function done!"
						print "****"
					else:
						db.rollback()
						print "Error: Adding new SF Function failed"
						print "****"
		else:
			self.addFuncFrame.msg.setText("SF Function already exists!")

	else:
		self.addFuncFrame.msg.setText("Type a valid SF Function! (At least 2 letters)")