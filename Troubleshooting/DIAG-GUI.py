from PyQt4 import QtGui, QtCore
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *
import sys, MySQLdb

classifierIP = "10.1.0.99"

db = MySQLdb.connect("localhost","sfcuser","sfc123","SFC")
cursor = db.cursor()


class DIAG_RES(Packet):
    name = "DIAG_RESPONSE"
    fields_desc=[ ByteField("REQ_ID", 0),
           	  IntEnumField("STATUS", None, {0:"FAIL", 1:"SUCCESS"}),
                  IntEnumField("ERROR" , 0, {0:"NO_ERROR", 1:"NOT_FOUND", 2:"BAD_INDEX", 3:"NextSF_NOT_FOUND", 4:"NextSFLocator_NOT_FOUND", 5:"SEQUENCE_END_ERROR", 6:"OUT_OF_RESSOURCES", 7:"UNKNOWN"})]

class DIAG_REQ(Packet):
    name = "DIAG_REQUEST"
    fields_desc=[ ByteField("REQ_ID", 0),
                  ShortField("SF_Map_Index", None),
                  FieldLenField("SF_ID_Len", None, length_of="SF_ID"), 
                  StrLenField("SF_ID", "", length_from=lambda pkt:pkt.SF_ID_Len),
                  FieldLenField("ES_SF_ID_Len", None, length_of="ES_SF_ID"), 
                  StrLenField("ES_SF_ID", "", length_from=lambda pkt:pkt.ES_SF_ID_Len),
                  ByteField("TestPacket", 0)]


bind_layers(IP, DIAG_REQ, proto=253)
bind_layers(DIAG_REQ, IP, TestPacket=1)
bind_layers(DIAG_REQ, DIAG_RES)
bind_layers(DIAG_RES, IP)

def display(p):
	if DIAG_REQ in p:
		d = p[DIAG_REQ]

		if d.ES_SF_ID=="":
			if d.SF_Map_Index==0:
				print "\tSF Map Index = %d" % d.SF_Map_Index
				print "\tSF Function  = %s" % d.SF_ID
			else:
				print "\tSF Map Index       = %d" % d.SF_Map_Index
				print "\tFirst SF Function  = %s" % d.SF_ID

		if d.ES_SF_ID!="":
			print "\tSF Map Index   = %d" % d.SF_Map_Index
			print "\tSequence Start = %s" % d.SF_ID
			print "\tSequence End   = %s" % d.ES_SF_ID

def cb(p, payload):
	data = payload.get_data()
	p = IP(data)
	if DIAG_REQ in p:
		print "Answer received"
		res = p[DIAG_REQ]
		text = res.show()
		print text
		payload.set_verdict(nfqueue.NF_DROP)
	else:
		print "No answer"
		payload.set_verdict(nfqueue.NF_DROP)


class MainFrame(QtGui.QFrame):
	def __init__(self, parent):
        	super(MainFrame, self).__init__(parent)

        	groupBox = QtGui.QGroupBox("Choose the DIAG operation")

       		self.sf = QtGui.QPushButton("SF Function")
       		self.map = QtGui.QPushButton("SF Map")
       		self.sequence = QtGui.QPushButton("Sequence")
       		self.classRules = QtGui.QPushButton("Classification rules")
       		self.allSF = QtGui.QPushButton("All SF Maps of a SF Function")
       		self.allMaps = QtGui.QPushButton("All SF Maps")

	    	self.vbox = QtGui.QVBoxLayout(self)
		self.vbox.addWidget(self.sf)
		self.vbox.addWidget(self.map)
		self.vbox.addWidget(self.sequence)
		self.vbox.addWidget(self.classRules)
		self.vbox.addWidget(self.allSF)
		self.vbox.addWidget(self.allMaps)
		groupBox.setLayout(self.vbox)

	    	self.vmainBox = QtGui.QVBoxLayout(self)
		self.vmainBox.addWidget(groupBox)
		self.setLayout(self.vmainBox)


class SF_Frame(QtGui.QFrame):
	def __init__(self, parent):
        	super(SF_Frame, self).__init__(parent)

		#Combo Box
		self.combo = QtGui.QComboBox(self)
		sql = "SELECT SF FROM Locators"			
		try:	
			cursor.execute(sql)
   			results = cursor.fetchall()
		except:
   			print "Error: unable to fecth data"

		for result in results:
			self.combo.addItem(str(result[0]))

		#Box1
	    	vbox1 = QtGui.QVBoxLayout()
		self.label = QtGui.QLabel("Choose the SF Function to troubleshoot")
		vbox1.addWidget(self.label)
		vbox1.addWidget(self.combo)
        	vbox1.addStretch()

		#Box2
	    	hbox2 = QtGui.QHBoxLayout()
       		self.back = QtGui.QPushButton("Back")
       		self.start = QtGui.QPushButton("Start")
		hbox2.addWidget(self.back)
		hbox2.addWidget(self.start)

		#Main Box
	    	self.vbox = QtGui.QVBoxLayout()
		self.vbox.addLayout(vbox1)
		self.vbox.addLayout(hbox2)
		self.setLayout(self.vbox)

class ClassRules_Frame(QtGui.QFrame):
	def __init__(self, parent):
        	super(ClassRules_Frame, self).__init__(parent)

		#Combo Box
		self.combo = QtGui.QComboBox(self)
		classifierDB = MySQLdb.connect(classifierIP,"sfcuser","sfc123","SFC")
		classifierCursor = classifierDB.cursor()
		sql = "SELECT id, SF_MAP_INDEX, SIP, DIP, Protocol, SPort, DPort FROM ClassRules ORDER BY ParNum DESC"			
		try:	
			classifierCursor.execute(sql)
   			results = classifierCursor.fetchall()
		except:
   			print "Error: unable to fecth data (Reading Rules from Classifier)"

		rules = ""
		self.rulesList = []
		self.RIDs = []
		for result in results:
			self.RIDs.append(result[0])
			num = "Rule %d" % len(self.RIDs)	
			mark  = "  Map_Index\t=  " + str(result[1]) + "\n"			                 
			SIP   = "  IP Source\t=  " + str(result[2]) + "\n"
			DIP   = "  IP Dest\t=  " + str(result[3]) + "\n"
			proto = "  Protocol\t=  " + str(result[4]) + "\n"
			sport = "  Port Source\t=  " + str(result[5]) + "\n"
			dport = "  Port Dest\t=  " + str(result[6]) + "\n"

			rule = mark + SIP + DIP + proto + sport + dport + "\n"
			self.rulesList.append(rule)
			self.combo.addItem(num)
			rules = rules + num + ":\n" + rule

       		self.rulesTE = QtGui.QTextEdit()
		self.rulesTE.setText(rules)

		#Box
	    	hbox = QtGui.QHBoxLayout()
       		self.back = QtGui.QPushButton("Back")
       		self.start = QtGui.QPushButton("Start")
		hbox.addWidget(self.back)
		hbox.addWidget(self.start)

		#Main Box
	    	self.vbox = QtGui.QVBoxLayout()
		self.label = QtGui.QLabel("Choose the Rule to delete:", self)
		self.vbox.addWidget(self.label)
		self.vbox.addWidget(self.combo)
		self.vbox.addWidget(self.rulesTE)
		self.vbox.addStretch()
		self.vbox.addLayout(hbox)
		self.setLayout(self.vbox)


class SFMap_Frame(QtGui.QFrame):
	def __init__(self, parent):
        	super(SFMap_Frame, self).__init__(parent)

		#Combo Box
		self.combo = QtGui.QComboBox(self)
		sql = "SELECT SF_MAP_INDEX, SFMap FROM SFMaps"			
		try:	
			cursor.execute(sql)
   			results = cursor.fetchall()
		except:
   			print "Error: unable to fecth data"

		for result in results:
			self.combo.addItem(str(result[0]) + " " + str(result[1]))

		#Box1
	    	vbox1 = QtGui.QVBoxLayout()
		self.label = QtGui.QLabel("Choose the SF Map to troubleshoot")
		vbox1.addWidget(self.label)
		vbox1.addWidget(self.combo)
        	vbox1.addStretch()

		#Box2
	    	hbox2 = QtGui.QHBoxLayout()
       		self.back = QtGui.QPushButton("Back")
       		self.start = QtGui.QPushButton("Start")
		hbox2.addWidget(self.back)
		hbox2.addWidget(self.start)

		#Main Box
	    	self.vbox = QtGui.QVBoxLayout()
		self.vbox.addLayout(vbox1)
		self.vbox.addLayout(hbox2)
		self.setLayout(self.vbox)

class Sequence_Frame(QtGui.QFrame):
	def __init__(self, parent):
        	super(Sequence_Frame, self).__init__(parent)

		#Combo Box1
		self.combo1 = QtGui.QComboBox(self)
		sql = "SELECT SF_MAP_INDEX, SFMap FROM SFMaps"			
		try:	
			cursor.execute(sql)
   			results = cursor.fetchall()
		except:
   			print "Error: unable to fecth data"

		for result in results:
			self.combo1.addItem(str(result[0]) + " " + str(result[1]))

		#Combo Box 2 & 3
		self.combo2 = QtGui.QComboBox(self)
		self.combo3 = QtGui.QComboBox(self)
		text = str(self.combo1.currentText())
		SFMap = (text.split("{")[1]).rstrip("}").split(", ")
		i=1
		for SF in SFMap:
			if i==1:
				self.combo2.addItem(SF)

			elif i==len(SFMap):
				self.combo3.addItem(SF)
			else:
				self.combo2.addItem(SF)
				self.combo3.addItem(SF)
			i += 1

		#Box1
	    	vbox1 = QtGui.QVBoxLayout()
		self.label1 = QtGui.QLabel("Select the SF Map to create the sequence")
		self.label2 = QtGui.QLabel("Select the start of the sequence")
		self.label3 = QtGui.QLabel("Select the end of the sequence")
		vbox1.addWidget(self.label1)
		vbox1.addWidget(self.combo1)
		vbox1.addWidget(self.label2)
		vbox1.addWidget(self.combo2)
		vbox1.addWidget(self.label3)
		vbox1.addWidget(self.combo3)
        	vbox1.addStretch()

		#Box2
	    	hbox2 = QtGui.QHBoxLayout()
       		self.back = QtGui.QPushButton("Back")
       		self.start = QtGui.QPushButton("Start")
		hbox2.addWidget(self.back)
		hbox2.addWidget(self.start)

		#Main Box
	    	self.vbox = QtGui.QVBoxLayout()
		self.vbox.addLayout(vbox1)
		self.vbox.addLayout(hbox2)
		self.setLayout(self.vbox)


class AllSF_Frame(QtGui.QFrame):
	def __init__(self, parent):
        	super(AllSF_Frame, self).__init__(parent)


		#Box1
	    	vbox1 = QtGui.QVBoxLayout()
		label1 = QtGui.QLabel("Select the SF Function")
		label2 = QtGui.QLabel("Troubleshooting of thsese SF Maps:")
		self.label3 = QtGui.QLabel("")
		vbox1.addWidget(label1)

		#Combo Box
		self.combo = QtGui.QComboBox(self)
		sql = "SELECT SF FROM Locators"			
		try:	
			cursor.execute(sql)
   			results = cursor.fetchall()
		except:
   			print "Error: unable to fecth data"

		for result in results:
			self.combo.addItem(str(result[0]))

		sql = "SELECT SF_MAP_INDEX, SFMap FROM SFMaps"			
		try:	
			cursor.execute(sql)
   			self.results = cursor.fetchall()
		except:
   			print "Error: unable to fecth data"

		self.indexes = []
		self.firstSFs = []
		self.SFMaps= []
		currentSF = self.combo.currentText()

		for result in self.results:
			SFMap = (result[1].split("{")[1]).rstrip("}").split(", ")
			firstSF = SFMap[0]
			for SF in SFMap:
				if SF == currentSF:
					self.indexes.append(result[0])
					self.SFMaps.append(result[1])
					self.firstSFs.append(firstSF)
					text = self.label3.text()
					self.label3.setText(str(text) + result[1] + "\n")
					break

		vbox1.addWidget(self.combo)
		vbox1.addWidget(label2)
		vbox1.addWidget(self.label3)
        	vbox1.addStretch()

		#Box2
	    	hbox2 = QtGui.QHBoxLayout()
       		self.back = QtGui.QPushButton("Back")
       		self.start = QtGui.QPushButton("Start")
		hbox2.addWidget(self.back)
		hbox2.addWidget(self.start)

		#Main Box
	    	self.vbox = QtGui.QVBoxLayout()
		self.vbox.addLayout(vbox1)
		self.vbox.addLayout(hbox2)
		self.setLayout(self.vbox)


class AllMaps_Frame(QtGui.QFrame):
	def __init__(self, parent):
        	super(AllMaps_Frame, self).__init__(parent)
		
		self.indexes = []
		self.firstSFs = []
		self.SFMaps= []

		#Reading all SF Maps
		text = ""
		sql = "SELECT SF_MAP_INDEX, SFMap FROM SFMaps"			
		try:	
			cursor.execute(sql)
   			results = cursor.fetchall()
		except:
   			print "Error: unable to fecth data"

		for result in results:
			text = text + str(result[0]) + "\t" + result[1] + "\n"
			firstSF = (result[1].split("{")[1]).rstrip("}").split(", ")[0]
			self.indexes.append(result[0]) 
			self.firstSFs.append(firstSF)
			self.SFMaps.append(result[1])



		#HBox
	    	hbox = QtGui.QHBoxLayout()
       		self.back = QtGui.QPushButton("Back")
       		self.start = QtGui.QPushButton("Start")
		hbox.addWidget(self.back)
		hbox.addWidget(self.start)

		#Main Box
	    	self.vbox = QtGui.QVBoxLayout()
		label1 = QtGui.QLabel("Troubleshooting of all SFMaps:")
		label2 = QtGui.QLabel("Index\tSFMap")
		label3 = QtGui.QLabel(text)
		self.vbox.addWidget(label1)
		self.vbox.addWidget(label2)
		self.vbox.addWidget(label3)
        	self.vbox.addStretch()
		self.vbox.addLayout(hbox)
		self.setLayout(self.vbox)


class MainWindow(QtGui.QMainWindow):

    	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)

		self.mainFrame = MainFrame(QtGui.QFrame(self))
		self.SFFrame = SF_Frame(QtGui.QFrame(self))
		self.classRulesFrame =	ClassRules_Frame(QtGui.QFrame(self))
		self.SFMapFrame = SFMap_Frame(QtGui.QFrame(self))
		self.seqFrame =	Sequence_Frame(QtGui.QFrame(self))
		self.allSFFrame = AllSF_Frame(QtGui.QFrame(self))
		self.allMapsFrame = AllMaps_Frame(QtGui.QFrame(self))


		self.central_widget = QtGui.QStackedWidget()		#Creation
       		self.central_widget.addWidget(self.mainFrame)		#Fill
       		self.central_widget.addWidget(self.SFFrame)
       		self.central_widget.addWidget(self.classRulesFrame)
       		self.central_widget.addWidget(self.SFMapFrame)
       		self.central_widget.addWidget(self.seqFrame)
       		self.central_widget.addWidget(self.allSFFrame)
       		self.central_widget.addWidget(self.allMapsFrame)
		self.central_widget.setCurrentWidget(self.mainFrame)	#Set Currrent Frame
		self.setCentralWidget(self.central_widget)		#Add to main Window


		####################
		#Events connections#
		####################
		#Main Frame
		self.mainFrame.sf.clicked.connect(self.SF_buttonClicked)
		self.mainFrame.map.clicked.connect(self.SFMap_buttonClicked)  
		self.mainFrame.sequence.clicked.connect(self.seq_buttonClicked) 
		self.mainFrame.classRules.clicked.connect(self.classRules_buttonClicked)  
		self.mainFrame.allSF.clicked.connect(self.allSF_buttonClicked)  
		self.mainFrame.allMaps.clicked.connect(self.allMaps_buttonClicked) 

		#Classification Rules Frame
		self.classRulesFrame.back.clicked.connect(self.back_buttonClicked)
		self.classRulesFrame.start.clicked.connect(self.classRulesStart_buttonClicked) 

		#SF Frame
		self.SFFrame.back.clicked.connect(self.back_buttonClicked)
		self.SFFrame.start.clicked.connect(self.SFStart_buttonClicked)

		#SFMap Frame
		self.SFMapFrame.back.clicked.connect(self.back_buttonClicked)
		self.SFMapFrame.start.clicked.connect(self.SFMapStart_buttonClicked)

		#Sequence Frame
		self.seqFrame.back.clicked.connect(self.back_buttonClicked)
		self.seqFrame.start.clicked.connect(self.seqStart_buttonClicked)
		self.seqFrame.combo1.currentIndexChanged.connect(self.seq_combo1EventHandler)
		self.seqFrame.combo2.currentIndexChanged.connect(self.seq_combo2EventHandler)

		#AllSF Frame
		self.allSFFrame.back.clicked.connect(self.back_buttonClicked)
		self.allSFFrame.start.clicked.connect(self.allSFStart_buttonClicked)
		self.allSFFrame.combo.currentIndexChanged.connect(self.allSF_comboEventHandler)

		#All Maps Frame
		self.allMapsFrame.back.clicked.connect(self.back_buttonClicked)
		self.allMapsFrame.start.clicked.connect(self.allMapsStart_buttonClicked)


		###################
		#Window Parameters#
		###################
		QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10)) 
		self.setWindowIcon(QtGui.QIcon('tool.png')) 
		self.setGeometry(300, 300, 200, 150)
		self.setWindowTitle('Troubleshooting')
		self.statusBar()


	def SF_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.SFFrame)

	def SFMap_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.SFMapFrame)

	def seq_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.seqFrame)

	def classRules_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.classRulesFrame)

	def allSF_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.allSFFrame)

	def allMaps_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.allMapsFrame)

	def back_buttonClicked(self): 
		self.central_widget.setCurrentWidget(self.mainFrame)


	#Sending DIAG_REQ Events
	def SFStart_buttonClicked(self):
		sf = self.SFFrame.combo.currentText()
		sql = "SELECT Locator1 FROM Locators WHERE SF='%s'" % sf			
		try:	
			cursor.execute(sql)
   			result = cursor.fetchone()
		except:
   			print "Error: unable to fecth data"

		p = IP(proto=253, dst=result[0])/DIAG_REQ(SF_Map_Index=0, SF_ID=sf, ES_SF_ID="", TestPacket=0)
		print "Troubleshooting SF Function %s" % sf
		display(p)
		#send(p)
		print ""

	def classRulesStart_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.classRulesFrame)
		print "Troubleshooting classification rules"

	def SFMapStart_buttonClicked(self):
		text = str(self.SFMapFrame.combo.currentText()).split(" {")
		index = int(text[0])
		firstSF = text[1].rstrip("}").split(", ")[0]

		sql = "SELECT Locator1 FROM Locators WHERE SF='%s'" % firstSF			
		try:	
			cursor.execute(sql)
   			result = cursor.fetchone()
		except:
   			print "Error: unable to fecth data"

		p = IP(proto=253, dst=result[0])/DIAG_REQ(SF_Map_Index=index, SF_ID=firstSF, ES_SF_ID="", TestPacket=0)
		print "Troubleshooting SF Map %s" % str(self.SFMapFrame.combo.currentText())[2:]
		display(p)
		#send(p)
		print ""

	def seqStart_buttonClicked(self):
		text = str(self.seqFrame.combo1.currentText()).split(" {")
		index = int(text[0])

		startSF = str(self.seqFrame.combo2.currentText())
		EndSF = str(self.seqFrame.combo3.currentText())

		sql = "SELECT Locator1 FROM Locators WHERE SF='%s'" % startSF			
		try:	
			cursor.execute(sql)
   			result = cursor.fetchone()
		except:
   			print "Error: unable to fecth data"

		print "Troubleshooting a sequence in SF Map %s" % str(self.SFMapFrame.combo.currentText())[2:]
		p = IP(proto=253, dst=result[0])/DIAG_REQ(SF_Map_Index=index, SF_ID=startSF, ES_SF_ID=EndSF, TestPacket=0)
		display(p)
		#send(p)
		print ""


	def allSFStart_buttonClicked(self):
		print "Troubleshooting all SF Maps where %s is involved" % self.allSFFrame.combo.currentText()
		i=0
		while(i<len(self.allSFFrame.indexes)):
			index = self.allSFFrame.indexes[i]
			firstSF = self.allSFFrame.firstSFs[i]
			SFMap = self.allSFFrame.SFMaps[i]

			sql = "SELECT Locator1 FROM Locators WHERE SF='%s'" % firstSF			
			try:	
				cursor.execute(sql)
	   			result = cursor.fetchone()
			except:
	   			print "Error: unable to fecth data"

			print "DIAG_REQ() N %d for SF Map %s:" % ((i+1), SFMap)
			p = IP(proto=253, dst=result[0])/DIAG_REQ(SF_Map_Index=index, SF_ID=firstSF, ES_SF_ID="", TestPacket=0)
			display(p)
			#send(p)
			i += 1

		print ""


	def allMapsStart_buttonClicked(self):
		print "Troubleshooting all SF Maps"
		i=0
		while(i<len(self.allMapsFrame.indexes)):
			index = self.allMapsFrame.indexes[i]
			firstSF = self.allMapsFrame.firstSFs[i]
			SFMap = self.allMapsFrame.SFMaps[i]

			sql = "SELECT Locator1 FROM Locators WHERE SF='%s'" % firstSF			
			try:	
				cursor.execute(sql)
	   			result = cursor.fetchone()
			except:
	   			print "Error: unable to fecth data"

			print "DIAG_REQ() N %d for SF Map %s:" % ((i+1), SFMap)
			p = IP(proto=253, dst=result[0])/DIAG_REQ(SF_Map_Index=index, SF_ID=firstSF, ES_SF_ID="", TestPacket=0)
			display(p)
			#send(p)
			i += 1

		print ""

	def seq_combo1EventHandler(self):
		self.seqFrame.combo2.clear()
		self.seqFrame.combo3.clear()
		text = str(self.seqFrame.combo1.currentText())
		SFMap = (text.split("{")[1]).rstrip("}").split(", ")
		i=0
		while(i<len(SFMap)-1):
			self.seqFrame.combo2.addItem(SFMap[i])
			i += 1

	def seq_combo2EventHandler(self):
		self.seqFrame.combo3.clear()
		index = self.seqFrame.combo2.currentIndex() + 1
		text = str(self.seqFrame.combo1.currentText())
		SFs = (text.split("{")[1]).rstrip("}").split(", ")

		while(index<len(SFs)):
			self.seqFrame.combo3.addItem(SFs[index])
			index += 1

	def allSF_comboEventHandler(self):
		self.allSFFrame.indexes = []
		self.allSFFrame.firstSFs = []
		self.allSFFrame.label3.setText("")
		currentSF = self.allSFFrame.combo.currentText()

		for result in self.allSFFrame.results:
			SFMap = (result[1].split("{")[1]).rstrip("}").split(", ")
			firstSF = SFMap[0]
			for SF in SFMap:
				if SF == currentSF:
					self.allSFFrame.indexes.append(result[0])
					self.allSFFrame.firstSFs.append(firstSF)
					text = self.allSFFrame.label3.text()
					self.allSFFrame.label3.setText(str(text) + result[1] + "\n")
					break


def main():
	app = QtGui.QApplication(sys.argv)
   	mainw = MainWindow()
   	mainw.show()
	sys.exit(app.exec_())
	db.close()


if __name__ == '__main__':
    	main()