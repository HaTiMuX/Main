import re
from PyQt4 import QtGui
from Functions import LocalLocators_Update

def updateLocUpdate(self, db, cursor):
	#Reading current SF functions
	curtext = self.updateLocFrame.combo.currentText()
	SF = curtext.split(' ')

	#Reading LocNum of the current SF Function 
	try:	
		sql = "SELECT LocNum FROM Locators WHERE SF='%s'" % SF[0]
		cursor.execute(sql)
   		result = cursor.fetchone()
	except:
		print "Error: unable to fecth the number of SF's locators"


	try:
		locNum = result[0]

		if locNum==3:
			self.updateLocFrame.newLoc1_le.setDisabled(False)
			self.updateLocFrame.newLoc2_le.setDisabled(False)
			self.updateLocFrame.newLoc3_le.setDisabled(False)
		elif locNum==2:
			self.updateLocFrame.newLoc1_le.setDisabled(False)
			self.updateLocFrame.newLoc2_le.setDisabled(False)
			self.updateLocFrame.newLoc3_le.setDisabled(True)
		elif locNum==1:
			self.updateLocFrame.newLoc1_le.setDisabled(False)
			self.updateLocFrame.newLoc2_le.setDisabled(True)
			self.updateLocFrame.newLoc3_le.setDisabled(True)
		else:
			print "Unexpected error: combo event LocNum"

	except:
		print "No entry remaining (update)"


def updateLoc(self, db, cursor): #updating locators of an existing SF Function
	if self.updateLocFrame.combo.count() != 0:
		#Preparing conditions
		cb_index = self.updateLocFrame.combo.currentIndex()
		IPExp = "^((25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)$"
		emptyExp = "^( ?){15}$"
		Error = None
		error = 0

		#reading SF Function to update
		curtext = self.updateLocFrame.combo.currentText()
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
			newLoc1 = self.updateLocFrame.newLoc1_le.text()
			IPCond1= re.search(IPExp, newLoc1) is not None
			emptyCond1 = re.search(emptyExp, newLoc1) is not None 

			print "Only the first locator can be updated"
			#lock other textfields
			if (IPCond1 is True) and (emptyCond1 is False):
				sql = "UPDATE Locators SET Locator1 = '%s' WHERE SF='%s'" % (newLoc1, updatedSF)
			else:
				Error = "Type valid IP address for the first locator"

		elif locNum==2:
			newLoc1 = self.updateLocFrame.newLoc1_le.text()
			newLoc2 = self.updateLocFrame.newLoc2_le.text()

			IPCond1= re.search(IPExp, newLoc1) is not None
			IPCond2= re.search(IPExp, newLoc2) is not None

			emptyCond1 = re.search(emptyExp, newLoc1) is not None 
			emptyCond2 = re.search(emptyExp, newLoc2) is not None 

			print "Both the first and the second locator can be updated"
			#lock other textfields
			if (IPCond1 is False) and (emptyCond1 is False):
				Error = "Type valid IP address for the first locator"
			elif (IPCond2 is False) and (emptyCond2 is False):
				Error =  "Type valid IP address for the second locator"
			elif (emptyCond1 is True) and (emptyCond2 is True):
				Error = "Type at least one locator to update"
			else:
				if emptyCond1 is True:		
					sql = "UPDATE Locators SET Locator2 = '%s' WHERE SF='%s'" % (newLoc2, updatedSF)
				elif emptyCond2 is True:		
					sql = "UPDATE Locators SET Locator1 = '%s' WHERE SF='%s'" % (newLoc1, updatedSF)
				else:
					sql = "UPDATE Locators SET Locator1 = '%s', Locator2 = '%s' WHERE SF='%s'" % (newLoc1, newLoc2, updatedSF)
				
		elif locNum==3:
			newLoc1 = self.updateLocFrame.newLoc1_le.text()
			newLoc2 = self.updateLocFrame.newLoc2_le.text()
			newLoc3 = self.updateLocFrame.newLoc3_le.text()

			IPCond1= re.search(IPExp, newLoc1) is not None
			IPCond2= re.search(IPExp, newLoc2) is not None
			IPCond3= re.search(IPExp, newLoc3) is not None

			emptyCond1 = re.search(emptyExp, newLoc1) is not None 
			emptyCond2 = re.search(emptyExp, newLoc2) is not None 
			emptyCond3 = re.search(emptyExp, newLoc3) is not None

			print "All locators can be updated"
			if (IPCond1 is False) and (emptyCond1 is False):
				Error = "Type valid IP address for the first locator"
			elif (IPCond2 is False) and (emptyCond2 is False):
				Error = "Type valid IP address for the second locator"
			elif (IPCond3 is False) and (emptyCond3 is False):
				Error = "Type valid IP address for the third locator"
			elif (emptyCond1 is True) and (emptyCond2 is True) and (emptyCond3 is True):
				Error = "Type at least one locator to update"
			else:
				if emptyCond1 is True:		
					if emptyCond2 is True:		
						sql = "UPDATE Locators SET Locator3 = '%s' WHERE SF='%s'" % (newLoc3, updatedSF)
					elif emptyCond3 is True:
						sql = "UPDATE Locators SET Locator2 = '%s' WHERE SF='%s'" % (newLoc2, updatedSF)
					else:
						sql = "UPDATE Locators SET Locator2 = '%s', Locator3 = '%s' WHERE SF='%s'" % (newLoc2, newLoc3, updatedSF)

				elif emptyCond2 is True:
					if emptyCond3 is True:				
						sql = "UPDATE Locators SET Locator1 = '%s' WHERE SF='%s'" % (newLoc1, updatedSF)
					else: 
						sql = "UPDATE Locators SET Locator1 = '%s', Locator3 = '%s' WHERE SF='%s'" % (newLoc1, newLoc3, updatedSF)

				elif emptyCond3 is True:
					sql = "UPDATE Locators SET Locator1 = '%s', Locator2 = '%s' WHERE SF='%s'" % (newLoc1, newLoc2, updatedSF)
				else:
					sql = "UPDATE Locators SET Locator1 = '%s', Locator2 = '%s', Locator3 = '%s' WHERE SF='%s'" % (newLoc1, newLoc2, newLoc3, updatedSF)


		if Error is None:
			self.updateLocFrame.error_msg.setText("")
			msg = "Are you sure to update the selected Entry?"
			reply = QtGui.QMessageBox.question(self, 'Confirmation', msg , QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

			if reply == QtGui.QMessageBox.Yes:
				try:
					cursor.execute(sql)
			   		db.commit()
				except:
	  				db.rollback()
					print "Error Updating SF Locators"


				#Updating Local Locators
				error = LocalLocators_Update(updatedSF, newLoc1, 2)

				#Updating List of SF Functions and locators "updateLocFrame" + "addLocFrame" + "delLocFrame"
				if locNum==3:
					if emptyCond1 is False:	
						self.updateLocFrame.locators[1][cb_index] = newLoc1
						self.addLocFrame.locators[1][cb_index] = newLoc1
						self.delLocFrame.locators[1][cb_index] = newLoc1
					if emptyCond2 is False:	
						self.updateLocFrame.locators[2][cb_index] = newLoc2
						self.addLocFrame.locators[2][cb_index] = newLoc2
						self.delLocFrame.locators[2][cb_index] = newLoc2
					if emptyCond3 is False:
						self.updateLocFrame.locators[3][cb_index] = newLoc3	
						self.addLocFrame.locators[3][cb_index] = newLoc3
						self.delLocFrame.locators[3][cb_index] = newLoc3
		
					loc1 = self.addLocFrame.locators[1][cb_index]
					loc2 = self.addLocFrame.locators[2][cb_index]
					loc3 = self.addLocFrame.locators[3][cb_index]
					self.updateLocFrame.combo.setItemText(cb_index, updatedSF + " => " + loc1 + "|" + loc2 + "|" + loc3)
					self.addLocFrame.combo.setItemText(cb_index, updatedSF + " => " + loc1 + "|" + loc2 + "|" + loc3)
					self.delLocFrame.combo.setItemText(cb_index, updatedSF + " => " + loc1 + "|" + loc2 + "|" + loc3)
				elif locNum==2:	
					if emptyCond1 is False:	
						self.updateLocFrame.locators[1][cb_index] = newLoc1
						self.addLocFrame.locators[1][cb_index] = newLoc1
						self.delLocFrame.locators[1][cb_index] = newLoc1
					if emptyCond2 is False:	
						self.updateLocFrame.locators[2][cb_index] = newLoc2
						self.addLocFrame.locators[2][cb_index] = newLoc2
						self.delLocFrame.locators[2][cb_index] = newLoc2

					loc1 = self.addLocFrame.locators[1][cb_index]
					loc2 = self.addLocFrame.locators[2][cb_index]
					self.updateLocFrame.combo.setItemText(cb_index, updatedSF + " => " + loc1 + "|" + loc2)
					self.addLocFrame.combo.setItemText(cb_index, updatedSF + " => " + loc1 + "|" + loc2)
					self.delLocFrame.combo.setItemText(cb_index, updatedSF + " => " + loc1 + "|" + loc2)
				elif locNum==1:
					self.updateLocFrame.locators[1][cb_index] = newLoc1
					self.addLocFrame.locators[1][cb_index] = newLoc1
					self.updateLocFrame.combo.setItemText(cb_index, updatedSF + " => " + newLoc1)
					self.addLocFrame.combo.setItemText(cb_index, updatedSF + " => " + newLoc1)
					self.delLocFrame.combo.setItemText(cb_index, updatedSF + " => " + newLoc1)
				else:
					print "Error updating Lists (Loc Update)"

				self.updateLocFrame.success_msg.setText("Locators successfully updated!")
		else:
			self.updateLocFrame.error_msg.setText(error)
	else:
		QtGui.QMessageBox.critical(self, 'Error', "No Entry remaining!" , QtGui.QMessageBox.Ok)
