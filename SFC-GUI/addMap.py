import re
from PyQt4 import QtGui
from Functions import addMap_Update



def addMap_Updates(self, index, newSFMap, DSCP, db, cursor):
	try:
		sql = "INSERT INTO SFMaps (SF_MAP_INDEX, SFMap) VALUES (%d, '%s')" % (index, newSFMap)	
		cursor.execute(sql)
		print "Adding new SF Map to the local repository: Success"
	except:
		print "Error Adding new SF Map to the local repository"


	#Updating SFC Routing Tables of the Nodes involved in the new SF Map
	error = addMap_Update(index, newSFMap)

	if error==0:
		self.delMapFrame.combo.addItem(str(index) + " " + newSFMap)
		DSCP.remove(index) #Updating DSCP available values
		#Update of SFMapIndexesList
		self.delMapFrame.SFMapIndexesList.append(index)
		db.commit()
		print "Adding SF Map: Success!"
	else:
		db.rollback()
		print "Error: Adding SF Map Failed!"


def addMap(self, db, cursor, DSCP, count):
	if(count!=0):
		index_text = self.addMapFrame.index_le.text()
		DSCPexp = "^([1-9]|[1-5][0-9]|6[0-3])$"
		if(index_text==""):
			if len(DSCP)!= 0:
				reply = QtGui.QMessageBox.question(self, 'Message',
				"Do you really want to add this new SF Map?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

				if reply == QtGui.QMessageBox.Yes:
					#Preparing the new SF Map
					index = DSCP[0]
					Map = str(self.addMapFrame.SFLabel.text()).split('{') #Can't split using space 
					newSFMap = "{" + Map[1]
					#Applying Updates
					addMap_Updates(self, index, newSFMap, DSCP, db, cursor)
			else:
				QtGui.QMessageBox.critical(self, 'Error', "No DSCP value remaining!" , QtGui.QMessageBox.Ok)


		elif re.search(DSCPexp, index_text) is None:
			self.addMapFrame.msg.setText("Type a valid\nDSCP value!")

		else:
			self.addMapFrame.msg.setText("")
			index = int(index_text) #Converting the typed number in the LineEdit to Integer

			#Checking if the SF_Map_index already exists
			sql = "SELECT SF_MAP_INDEX FROM SFMaps WHERE SF_MAP_INDEX=%d" % int(index)
			try:	
				cursor.execute(sql)
	   			result = cursor.fetchone()
				if result is None:
					reply = QtGui.QMessageBox.question(self, 'Message',
					"Do you really want to add this new SF Map?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

					if reply == QtGui.QMessageBox.Yes:
						#Preparing the new SF Map
						Map = str(self.addMapFrame.SFLabel.text()).split('{') #Can't split using space 
						newSFMap = "{" + Map[1]
						#Applying Updates
						addMap_Updates(self, index, newSFMap, DSCP, db, cursor)
				else:
					self.addMapFrame.msg.setText("Index already exists!")
					print "SF_Map_Index already exists!! Try again."
			except:
				print "Error While Testing if the typed SF_Map_Index already exists!!"
	else:
		QtGui.QMessageBox.critical(self, 'Error', "No SF Function selected!" , QtGui.QMessageBox.Ok)