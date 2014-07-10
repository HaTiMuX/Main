import re
from PyQt4 import QtGui
import MySQLdb
import sys

classifierIP = "10.1.0.99"

#Adding a new rule
def addRule(self):
	self.addRuleFrame.error.setText("")
	SIP = self.addRuleFrame.rules_SIP_le.text()
	DIP = self.addRuleFrame.rules_DIP_le.text()
	proto = self.addRuleFrame.protoCombo.currentText()
	sport = self.addRuleFrame.rules_sport_le.text()
	dport = self.addRuleFrame.rules_dport_le.text()
	prio  = self.addRuleFrame.rules_prio_le.text()
	mark  = int(self.addRuleFrame.markCombo.currentText().split(" ")[0])
	param_num = 0
	IPExp = "^((25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)$"
	portExp = "^(([0-9]?){4}|[0-5]([0-9]?){4}|6[0-4]?([0-9]?){3}|65[0-4]?([0-9]?){2}|655[0-2]?[0-9]?|6553[0-5]?)$"
	prioExp = "^[1-9][0-9]?$"


	
	if(self.addRuleFrame.markCombo.count()!=0):
		if((re.search(prioExp, prio) is not None) or prio==""):
			if(SIP=="" and  DIP=="" and sport=="" and dport=="" and proto=="None"):
				self.addRuleFrame.error.setText("Fill at least one criterian for the rule!")

			elif ((re.search(IPExp, DIP) is None) and DIP!="") or ((re.search(IPExp, SIP) is None) and SIP!=""):
				self.addRuleFrame.error.setText("Type a valid IP address!")
		
			elif ((re.search(portExp, dport) is None) and dport!="") or ((re.search(portExp, sport) is None) and sport!=""):
				self.addRuleFrame.error.setText("Type a valid Port Number!")
				#print dport

			elif ((sport!="" or dport!="") and (proto!="TCP" and proto!="UDP")):
				self.addRuleFrame.error.setText("Select TCP or UDP to specify port numbers!")

			else:
				reply = QtGui.QMessageBox.question(self, 'Confirmation', "Confirm add rule operation?",
					QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

				if reply == QtGui.QMessageBox.Yes:
					if SIP!="":
						param_num += 1
					if DIP!="":
						param_num += 1
					if proto != "None":
						param_num += 1

					if sport!="":
						sport_num = int(sport)
						param_num += 1
					else:
						sport_num = 0 

					if dport!="":
						dport_num = int(dport) 
						param_num += 1
					else:
						dport_num = 0 

					if prio!="":
						prio_num = int(prio) 
					else:
						prio_num = 99


					try:
						sql =  ('INSERT INTO ClassRules (SF_MAP_INDEX, SIP, DIP, Protocol, SPort, DPort, Prio, ParNum) '\
							"VALUES ('%d','%s', '%s', '%s', '%d', '%d', '%d', '%d')") % (mark, SIP, DIP, proto, sport_num, dport_num, prio_num, param_num)
						classifierDB = MySQLdb.connect(classifierIP,"sfcuser","sfc123","SFC")
						classifierCursor = classifierDB.cursor()

						try:
							classifierCursor.execute(sql)
					   		classifierDB.commit()
						except:
					  		classifierDB.rollback()
							print "Error inserting New Rule"

						classifierDB.close()
					except:
						print "Problem connecting to the classifier DB"

					#Updates
					if len(self.delRuleFrame.RIDs)!=0:
						new_id = self.delRuleFrame.RIDs[len(self.delRuleFrame.RIDs) - 1] + 1
					else:
						new_id = 1
					self.delRuleFrame.RIDs.append(new_id)
					num = "Rule %d" % len(self.delRuleFrame.RIDs)	
					mark  = "  Map_Index\t=  " + str(mark) + "\n"			                 
					SIP   = "  IP Source\t=  " + str(SIP) + "\n"
					DIP   = "  IP Dest\t=  " + str(DIP) + "\n"
					proto = "  Protocol\t=  " + str(proto) + "\n"
					sport = "  Port Source\t=  " + str(sport) + "\n"
					dport = "  Port Dest\t=  " + str(dport) + "\n"

					newRule = mark + SIP + DIP + proto + sport + dport + "\n"
					rules = self.delRuleFrame.rulesTE.toPlainText() + num + ":\n" + newRule
					self.delRuleFrame.rulesTE.setText(rules)
					self.delRuleFrame.rulesList.append(newRule)
					self.delRuleFrame.combo.addItem(num)

		else:
			self.addRuleFrame.error.setText("Type a valid Priority for the rule!")
	else:
		self.addRuleFrame.error.setText("No mark available!")

#Deleting an existing Rule
def delRule(self): 
	if self.delRuleFrame.combo.count() != 0:
		index = self.delRuleFrame.combo.currentIndex()
		msg = "Are you sure to delete the selected Entry?"
		reply = QtGui.QMessageBox.question(self, 'Confirmation', msg , QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

		if reply == QtGui.QMessageBox.Yes:
			self.delRuleFrame.combo.clear()
			try:
				sql = "DELETE FROM ClassRules WHERE id='%d'" % self.delRuleFrame.RIDs[index]
				classifierDB = MySQLdb.connect(classifierIP,"sfcuser","sfc123","SFC")
				classifierCursor = classifierDB.cursor()
				try:	
					classifierCursor.execute(sql)
			   		classifierDB.commit()

				except:
	  				classifierDB.rollback()
					print "Error Deleting (Rule)"

				classifierDB.close()
			except:
				print "Problem connecting to the classifier DB"

			self.delRuleFrame.combo.removeItem(index)
			self.delRuleFrame.RIDs.pop(index)
			self.delRuleFrame.rulesList.pop(index)

			newRules = ""
			i=1
			for rule in self.delRuleFrame.rulesList:
				num = "Rule %d" % i 	
				newRules = newRules + num + ":\n" + rule
				self.delRuleFrame.combo.addItem(num)
				i += 1
			self.delRuleFrame.rulesTE.setText(newRules)

	
	else:
		QtGui.QMessageBox.critical(self, 'Error', "No Entry remaining!" , QtGui.QMessageBox.Ok)