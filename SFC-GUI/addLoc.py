import re
from PyQt4 import QtGui, QtCore


def addLocUpdate(self, db, cursor):
	#Reading current SF functions
	curtext = self.addLocFrame.combo.currentText()
	SF = curtext.split(' ')

	#Reading LocNum of the current SF Function 
	try:	
		sql = "SELECT LocNum FROM Locators WHERE SF='%s'" % SF[0]
		cursor.execute(sql)
   		result = cursor.fetchone()

	except:
		print "Error: unable to fecth the number of SF's locators (addLocUpdate)"

	try:
		locNum = result[0]
		if locNum==3:
			self.addLocFrame.newLoc3_le.setDisabled(True)
			self.addLocFrame.newLoc2_le.setDisabled(True)

		elif locNum==2:
			self.addLocFrame.newLoc2_le.setDisabled(True)
			self.addLocFrame.newLoc3_le.setDisabled(False)

		elif locNum==1:
			self.addLocFrame.newLoc2_le.setDisabled(False)
			self.addLocFrame.newLoc3_le.setDisabled(False)
		else:
			print "Unexpected error: combo event LocNum"
	except:
		print "No entry remaining (add loc)"


#Add locator to an existing SF Function
def addLoc(self, db, cursor): 
	if self.addLocFrame.combo.count() != 0:
		#Preparing conditions
		cb_index = self.addLocFrame.combo.currentIndex()
		IPExp = "^((25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)$"
		emptyExp = "^( ?){15}$"
		self.addLocFrame.success_msg.setText("")
		error = None

		#reading SF Function to update (Add Locator)
		curtext = self.addLocFrame.combo.currentText()
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
			newLoc2 = self.addLocFrame.newLoc2_le.text()
			newLoc3 = self.addLocFrame.newLoc3_le.text()

			IPCond2= re.search(IPExp, newLoc2) is not None
			IPCond3= re.search(IPExp, newLoc3) is not None
			emptyCond2 = re.search(emptyExp, newLoc2) is not None 
			emptyCond3 = re.search(emptyExp, newLoc3) is not None 

			if (IPCond2 is False) and (emptyCond2 is False):
				error = "Type valid IP address for the second locator"
			elif (IPCond3 is False) and (emptyCond3 is False):
				error =  "Type valid IP address for the third locator"
			elif (emptyCond2 is True) and (emptyCond3 is True):
				error = "Type at least one locator to add"
			else:
				if emptyCond2 is True:		
					error = "Respect the order of locators"
				elif emptyCond3 is True:	
					locNum = 2	
					sql = "UPDATE Locators SET Locator2 = '%s', LocNum = %d WHERE SF='%s'" % (newLoc2, locNum, updatedSF)
				else:
					locNum = 3 							
					sql = "UPDATE Locators SET Locator2 = '%s', Locator3 = '%s', LocNum = %d WHERE SF='%s'" % (newLoc2, newLoc3, locNum, updatedSF)

		elif locNum==2:
			newLoc2 = self.addLocFrame.locators[2][cb_index] #Needed in display (locNum==3 has to cases from 1 or from 2)
			newLoc3 = self.addLocFrame.newLoc3_le.text()
			
			IPCond3= re.search(IPExp, newLoc3) is not None
			if (IPCond3 is False):
				error = "Type valid IP address for the third locator"
			else:
				locNum = 3	
				sql = "UPDATE Locators SET Locator3 = '%s', LocNum = %d WHERE SF='%s'" % (newLoc3, locNum, updatedSF)

		else:
			error = "Unknown error (Loc Add)"

		if error is None:
			self.addLocFrame.error_msg.setText("")
			msg = "Are you sure to update the selected Entry?"
			reply = QtGui.QMessageBox.question(self, 'Confirmation', msg , QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

			if reply == QtGui.QMessageBox.Yes:
				try:
					cursor.execute(sql)
			   		db.commit()
				except:
	  				db.rollback()
					print "Error Updating SF Locators"

				#Updating List of SF Functions and locators "addLocFrame" + "delLocFrame" + "updateLocFrame"
				if locNum==3:
					self.addLocFrame.combo.setItemText(cb_index, updatedSF + " => " + self.addLocFrame.locators[1][cb_index] + "|" + newLoc2  + "|" + newLoc3)
					self.delLocFrame.combo.setItemText(cb_index, updatedSF + " => " + self.addLocFrame.locators[1][cb_index] + "|" + newLoc2  + "|" + newLoc3)
					self.updateLocFrame.combo.setItemText(cb_index, updatedSF + " => " + self.addLocFrame.locators[1][cb_index] + "|" + newLoc2  + "|" + newLoc3)

					if self.addLocFrame.locators[2][cb_index]=="":
						self.addLocFrame.success_msg.setText("Locators successfully added!")
						self.addLocFrame.locators[2][cb_index] = newLoc2
						self.delLocFrame.locators[2][cb_index] = newLoc2
						self.updateLocFrame.locators[2][cb_index] = newLoc2
					else:
						self.addLocFrame.success_msg.setText("Locator successfully added!")

					self.addLocFrame.locators[3][cb_index] = newLoc3
					self.delLocFrame.locators[3][cb_index] = newLoc3
					self.updateLocFrame.locators[3][cb_index] = newLoc3

				elif locNum==2:	
					self.addLocFrame.combo.setItemText(cb_index, updatedSF + " => " + self.addLocFrame.locators[1][cb_index] + "|" + newLoc2)
					self.delLocFrame.combo.setItemText(cb_index, updatedSF + " => " + self.addLocFrame.locators[1][cb_index] + "|" + newLoc2)
					self.updateLocFrame.combo.setItemText(cb_index, updatedSF + " => " + self.addLocFrame.locators[1][cb_index] + "|" + newLoc2)

					self.addLocFrame.locators[2][cb_index] = newLoc2
					self.delLocFrame.locators[2][cb_index] = newLoc2
					self.updateLocFrame.locators[2][cb_index] = newLoc2
					self.addLocFrame.success_msg.setText("Locator successfully added!")
				else:
					QtGui.QMessageBox.critical(self, 'Error', "Unknown error (locNum, Loc Add)!" , QtGui.QMessageBox.Ok)

		else:
			self.addLocFrame.error_msg.setText(error)
	else:
		QtGui.QMessageBox.critical(self, 'Error', "No Entry remaining!" , QtGui.QMessageBox.Ok)
