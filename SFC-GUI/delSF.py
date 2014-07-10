from PyQt4 import QtGui
from Functions import delMap_Update, LocalLocators_Update

#Deleting an existing SF Function
def delFunc(self, db, cursor, DSCP): 
	if self.delFuncFrame.combo.count() != 0:
		curtext = self.delFuncFrame.combo.currentText()
		SF = curtext.split(' ')
		removedSF = SF[0]
		indexesList = []

		msg = "Are you sure to delete the selected Entry?"
		reply = QtGui.QMessageBox.question(self, 'Confirmation', msg , QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

		if reply == QtGui.QMessageBox.Yes:
			error = 0
			print "***** SF Function to remove: " + removedSF + " *****"

			#Reading Locator of the removed SF
			try:	
				sql = "SELECT Locator1 FROM Locators WHERE SF='%s'" % removedSF
				cursor.execute(sql)
				result = cursor.fetchone()
			except:
				error = 1

			#Updating SF LocalLocators Database 
			error = LocalLocators_Update(removedSF, result[0], 3)

			#Updating SF Locators Database (Deleting the selected SF Function)
			try:
				sql = "DELETE FROM Locators WHERE SF='%s'" % removedSF
				cursor.execute(sql)
				print "* Deleting SF from Locators database: Success!"
			except:
				error = 1
				print "* Deleting SF from Locators database: Failed!"


			#Removing associeted SFMaps (SFMaps Database + List of delMapFrame)
			try:	
				sql = "SELECT SF_MAP_INDEX, SFMap FROM SFMaps"
				cursor.execute(sql)
				results = cursor.fetchall()
				print "* Reading SFMaps: Success!" 
			except:
				error = 1
				print "* Reading SFMaps: Failed!" 

			if error==0:
				for result in results:
					index = int(result[0])
					rowMap = result[1]
					SFMap = rowMap.lstrip('{')
					SFMap = SFMap.rstrip('}')
					SF_Map = SFMap.split(', ')

					for SF in SF_Map:
						if error==1:
							break

						if SF==removedSF: 
							#The SFMap is associated with the removed SF function
							#Deleting the associated SF Map and applying necessary updates
							print "* Deleting associated SF Map: %d %s" % (index, rowMap)

							#Updating DSCP available values
							try:
								DSCP.append(index) 
								print "\tUpdating DSCP values: Success!"
							except:
								error = 1
								print "\tUpdating DSCP values: Failed!"

							#Updating SFMaps database
							try:	
								sql = "DELETE FROM SFMaps WHERE SF_Map_Index=%d" % index
								cursor.execute(sql)
								print "\tUpdating SFMaps database: Success!"
							except:
								error = 1
								print "\tUpdating SFMaps database: Failed!"

							#Updating List of availble SF Maps
							cb_index = self.delMapFrame.SFMapIndexesList.index(index) #getting index of the current map to remove
							self.delMapFrame.SFMapIndexesList.pop(cb_index)
							self.delMapFrame.combo.removeItem(cb_index)

							#Updating SFC Routing Tables of the Nodes involved in the deleted SF Map
							error = delMap_Update(index, rowMap)
							if error==0:	
								print "\tUpdating SFC Routing Tables of the current SF Map: Success!"
							else:
								error = 1
								print "\tUpdating SFC Routing Tables of the current SF Map: Failed!"

							if error==0:
								print "\tDeleting associated SF Map: %d %s : Success!" % (index, rowMap)
							else:
								print "\tDeleting associated SF Map: %d %s : Failed!" % (index, rowMap)
								#Restoring DSCP values in case of error
								DSCP.remove(index)

							break
				if error==0:
					print "* Deleting associeted SFMaps: Success!" 
				else:
					print "* Deleting associeted SFMaps: Failed!" 


			if error==0:
				#getting index of the current SF to remove
				index = self.delFuncFrame.combo.currentIndex() 

				#Updating the list of availble SF functions to delete "delFuncFrame"
				self.delFuncFrame.combo.removeItem(index)

				#Updating Lists of "addLocFrame" + "delLocFrame" + "updateLocFrame"
				self.addLocFrame.locators[0].pop(index)
				self.delLocFrame.locators[0].pop(index)
				self.updateLocFrame.locators[0].pop(index)

				self.addLocFrame.locators[1].pop(index)
				self.delLocFrame.locators[1].pop(index)
				self.updateLocFrame.locators[1].pop(index)

				self.addLocFrame.locators[2].pop(index)
				self.delLocFrame.locators[2].pop(index)
				self.updateLocFrame.locators[2].pop(index)

				self.addLocFrame.locators[3].pop(index)
				self.delLocFrame.locators[3].pop(index)
				self.updateLocFrame.locators[3].pop(index)

				self.addLocFrame.combo.removeItem(index)
				self.delLocFrame.combo.removeItem(index)
				self.updateLocFrame.combo.removeItem(index)

				#Updating the list of availble SF Functions (addMapFrame)
				cb_index = self.addMapFrame.checkBoxList[1].index(removedSF) 
				self.addMapFrame.checkBoxList[0].pop(cb_index)
				self.addMapFrame.checkBoxList[1].pop(cb_index)
				self.addMapFrame.grid.itemAt(cb_index).widget().deleteLater()
				self.addMapFrame.SFCheckListDisplay()

				db.commit()
				print "Deleting SF Function " + removedSF + ": Success!"
				print "*****"
			else:
				db.rollback()
				print "Deleting SF Function " + removedSF + ": Failed!"
				print "*****"
	else:
		QtGui.QMessageBox.critical(self, 'Error', "No Entry remaining!" , QtGui.QMessageBox.Ok)
