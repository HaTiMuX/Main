from PyQt4 import QtGui
from Functions import delMap_Update

#Deleting an existing SF Map
def delMap(self, db, cursor, DSCP): 
	if self.delMapFrame.combo.count() != 0:
		curtext = str(self.delMapFrame.combo.currentText()) #Converting to str to use lstrip 

		text = curtext.split(" ")
		mapIndex = int(text[0])

		SFMap = curtext.lstrip(str(mapIndex) + " ") #Strip the Map index 
		SF = curtext.split(' ')

		msg = "Are you sure to delete the selected Entry?"
		reply = QtGui.QMessageBox.question(self, 'Confirmation', msg , QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

		if reply == QtGui.QMessageBox.Yes:
			error=0
			print "Map to delete: " + curtext

			#Deleting SF Map from the local repositry
			try:	
				sql = "DELETE FROM SFMaps WHERE SF_Map_Index=%d" % mapIndex
				cursor.execute(sql)
				print "* Deleting SF Map from the local repositry: Success!"
			except:
				error=1
				print "Error: Deleting SF Map from the local repositry Failed!"

			#Updating SFC Routing Tables of the Nodes involved in the deleted SF Map
			error = delMap_Update(mapIndex, SFMap)

			if error==0:
				cb_index = self.delMapFrame.combo.currentIndex()	
				self.delMapFrame.combo.removeItem(cb_index)

				DSCP.append(mapIndex) #Updating DSCP available values

				db.commit()

				print "Deleting SF Map: Success!"

			else:
				db.rollback()
				print "Deleting SF Map: Failed!"

	else:
		QtGui.QMessageBox.critical(self, 'Error', "No Entry remaining!" , QtGui.QMessageBox.Ok)
