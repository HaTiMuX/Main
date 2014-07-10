from PyQt4 import QtGui
from Functions import LocalLocators_Update

def delLocUpdate(self, db, cursor):
	#Reading current SF functions
	curtext = self.delLocFrame.combo.currentText()
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
		count = self.delLocFrame.posCombo.count()
		if locNum==3:
			if count==0:
				self.delLocFrame.posCombo.addItem("1")
				self.delLocFrame.posCombo.addItem("2")
				self.delLocFrame.posCombo.addItem("3")
			elif count==2:
				self.delLocFrame.posCombo.addItem("3")
		elif locNum==2:
			if count==0:
				self.delLocFrame.posCombo.addItem("1")
				self.delLocFrame.posCombo.addItem("2")
			self.delLocFrame.posCombo.removeItem(2) #3rd item
		elif locNum==1:
			#The order of removing is important due to indexes update
			self.delLocFrame.posCombo.removeItem(2) #3rd item
			self.delLocFrame.posCombo.removeItem(1) #2nd item
			self.delLocFrame.posCombo.removeItem(0) #1st item
	except:
		print "No entry remaining (delete)"



def delLoc(self, db, cursor):
	if self.addLocFrame.combo.count() != 0:
		error = 0
		cb_index = self.delLocFrame.combo.currentIndex()
		SF = self.delLocFrame.locators[0][cb_index]
		pos = int(self.delLocFrame.posCombo.currentIndex()) + 1

		msg = "Are you sure to remove the specified locator?"
		reply = QtGui.QMessageBox.question(self, 'Confirmation', msg , QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

		if reply == QtGui.QMessageBox.Yes:
			self.delLocFrame.error_msg.setText("")

			
			#Updating Locators Database
			#Reading all locators of the current SF Function 
			try:	
				sql = "SELECT LocNum, Locator1, Locator2, Locator3 FROM Locators WHERE SF='%s'" % SF
				cursor.execute(sql)
		   		result = cursor.fetchone()
			except:
				print "Error: unable to fecth locators (loc deletion)"

			#Preparing Updates for the current SF Function 
			locNum = result[0]
			if locNum==2:
				if pos==1:
					loc1 = result[2]
					loc2 = ""
					sql = "UPDATE Locators SET Locator1 = '%s', Locator2 = '%s', LocNum = 1 WHERE SF='%s'" % (loc1, loc2, SF)
					#Updating local locators Databases
					error = LocalLocators_Update(SF, loc1, 2)

				elif pos==2:
					loc2 = ""
					sql = "UPDATE Locators SET Locator2 = '%s', LocNum = 1 WHERE SF='%s'" % (loc2, SF)

			elif locNum==3:
				if pos==3:
					loc3 = ""
					loc2 = result[2]
					loc1 = result[1]
					sql = "UPDATE Locators SET Locator3 = '%s', LocNum = 2 WHERE SF='%s'" % (loc2, loc3, SF)

				elif pos==2:
					loc3 = ""
					loc2 = result[3]
					loc1 = result[1] 
					sql = "UPDATE Locators SET Locator2 = '%s', Locator3 = '%s', LocNum = 2 WHERE SF='%s'" % (loc2, loc3, SF)

				elif pos==1:
					loc3 = ""
					loc2 = result[3]
					loc1 = result[2]
					sql = "UPDATE Locators SET Locator1 = '%s', Locator2 = '%s', Locator3 = '%s', LocNum = 2 WHERE SF='%s'" % (loc1, loc2, loc3, SF)
					#Updating local locators Databases
					error = LocalLocators_Update(SF, loc1, 2)
			else:
				error=1


			#Updating List of SF Functions and locators "delLocFrame" + "addLocFrame" + "updateLocFrame" 
			if locNum==3:
				self.updateLocFrame.locators[1][cb_index] = loc1
				self.addLocFrame.locators[1][cb_index] = loc1
				self.delLocFrame.locators[1][cb_index] = loc1

				self.updateLocFrame.locators[2][cb_index] = loc2
				self.addLocFrame.locators[2][cb_index] = loc2
				self.delLocFrame.locators[2][cb_index] = loc2

				self.updateLocFrame.locators[3][cb_index] = loc3	
				self.addLocFrame.locators[3][cb_index] = loc3
				self.delLocFrame.locators[3][cb_index] = loc3

				self.updateLocFrame.combo.setItemText(cb_index, SF + " => " + loc1 + "|" + loc2)
				self.addLocFrame.combo.setItemText(cb_index, SF + " => " + loc1 + "|" + loc2)
				self.delLocFrame.combo.setItemText(cb_index, SF + " => " + loc1 + "|" + loc2)
			elif locNum==2:	
				self.updateLocFrame.locators[1][cb_index] = loc1
				self.addLocFrame.locators[1][cb_index] = loc1
				self.delLocFrame.locators[1][cb_index] = loc1

				self.updateLocFrame.locators[2][cb_index] = loc2
				self.addLocFrame.locators[2][cb_index] = loc2
				self.delLocFrame.locators[2][cb_index] = loc2

				self.updateLocFrame.combo.setItemText(cb_index, SF + " => " + loc1)
				self.addLocFrame.combo.setItemText(cb_index, SF + " => " + loc1)
				self.delLocFrame.combo.setItemText(cb_index, SF + " => " + loc1)

			#Applying updates
			if error==0:
				try:
					cursor.execute(sql)
			   		db.commit()
					self.delLocFrame.success_msg.setText("Locator deleted Successfully")
					self.delLocFrame.error_msg.setText("")
				except:
	  				db.rollback()
					self.delLocFrame.error_msg.setText("Locator deletion failed!")
					self.delLocFrame.success_msg.setText("")

	else:
		QtGui.QMessageBox.critical(self, 'Error', "No Entry remaining!" , QtGui.QMessageBox.Ok)


