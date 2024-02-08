import time
# Enable pyserial extensions
import serial 
class Ssc32:
    def __init__(self, portName="/dev/ttyUSB0", baudRate=115200,timeOutSecond=0.1):
    # Open a serial port from /dev/ttyUSB0
    #Cette méthode initialise la connexion série avec le SSC32 en utilisant le port série spécifié (portName),
    #le débit binaire (baudRate), et le délai d'attente (timeOutSecond).
    #Elle envoie également la commande VER\r au SSC32 pour récupérer 
    #et afficher la version du logiciel du SSC32.
        self.ser = serial.Serial()
        self.ser.baudrate=baudRate
        self.ser.port=portName
        self.ser.timeout=timeOutSecond
        self.ser.open()
        # Send bytes
        self.ser.write(b'VER\r')
        self.VERSION=self.ser.read(100)

        self.servoFirstUsage=[1]*32
        self.verbose=True
        if self.verbose:
            print(str(self.VERSION)) 
    def close(self):
        self.ser.close()
    #def write(self):
    
    #Cette méthode attend que la réponse à la commande 'Q\r' soit égale au caractère '.'. 
    #Elle est utilisée pour synchroniser l'envoi de nouvelles commandes au SSC32.
    def waitForNextCommand(self):
    # wait until response to 'Q\r' command is equal to '.' character    
        rep="+"
        while rep.find(".")<0:
            self.ser.write(b"Q\r")
            rep=self.ser.read(1)
            rep=str(rep)
    
    #Cette méthode envoie une commande au SSC32 pour déplacer les servos spécifiés (numServos)
    #vers les positions en microsecondes spécifiées (valuesUS).
    #Le paramètre optionnel timeTravelms permet de spécifier la durée du déplacement.
    def gotoUs( self,numServos=[0,1], valuesUS=[1500,1500] , timeTravelms=1000):
        k=0
        msg=''
        timeOk=True
        for num in numServos:
            us=valuesUS[k]
            msg=msg+'#'+str(num)+' P'+str(us)+' '
            if ( self.servoFirstUsage[k]==1 ):
                self.servoFirstUsage[k]=0
                timeOk=False
            k=k+1
        if (timeTravelms>0)and(timeOk):    
            msg=msg + 'T'+str(timeTravelms)
        msg=msg+'\r'
        msg=msg.encode("ASCII")
        if self.verbose:
            print(msg)    
        self.ser.write(msg)
    
    #Cette méthode envoie une commande au SSC32 pour contrôler les sorties numériques spécifiées (numServos). 
    #Les valeurs True ou False spécifient si la sortie doit être activée ou désactivée.
    def digitalOutput( self,numServos=[8,9], values=[False,False] ):
            k=0
            msg=''
            for num in numServos:
                logicVal=values[k]
                if logicVal:
                    msg=msg+'#'+str(num)+'H '
                else:
                    msg=msg+'#'+str(num)+'L '
                k=k+1
            msg=msg+'\r'
            msg=msg.encode("ASCII")
            if self.verbose:
                print(msg)    
            self.ser.write(msg)

testeSSC32=False
if testeSSC32:
    # Receive bytes
    ssc32=Ssc32(portName="/dev/ttyUSB0",baudRate=115200,timeOutSecond=0.05)
    reponse=ssc32.ser.read(100)
    print(str(reponse))
    testeServo=False
    if (testeServo):
        ssc32.gotoUs([0,1],[1000,1000])
        time.sleep(1)
        ssc32.waitForNextCommand()
        ssc32.gotoUs([0,1],[1600,1600],timeTravelms=5000)
        ssc32.waitForNextCommand()
    testeDigitalOut=False
    if (testeDigitalOut):
        ssc32.digitalOutput(numServos=[8],values=[False])
        for i in range(0,20):
            ssc32.digitalOutput(numServos=[8],values=[True])
            time.sleep(1)
            ssc32.digitalOutput(numServos=[8],values=[False])
            time.sleep(1)
        ssc32.digitalOutput(numServos=[8],values=[False])
    testeValues=True
    if (testeValues):
        lastUs=1500
        numServo=0
        allServos=[0,1,3,5,6,7,8,9]
        for k in allServos:
            ssc32.gotoUs([k],[1500]) # par prudence on commence au point milieu
        ssc32.digitalOutput([2],[True]) # on allume le laser0
        fin =False
        while (not(fin)):
            inputStr = input("Enter servo number between 0 and 31, us between 500 and 2500, logical T or F, -1 to finish: ")
            logicalMode=False
            if inputStr=='T':
                logicalVal=True
                logicalMode=True
            if inputStr=='F':
                logicalVal=False
                logicalMode=True
            if logicalMode:
                ssc32.digitalOutput([numServo],[logicalVal])
            else:             
                val=int(inputStr)
                if (val>=0)and(val<32):
                    numServo=val
                    print ('current Servo is:'+str(numServo))
                if (val>=500)and(val<=2500):
                    micros=val
                    ssc32.gotoUs([numServo],[micros],timeTravelms=0)
                    lastUs=micros
                fin= val<0
    for k in allServos:
        ssc32.gotoUs([k],[1500]) # par prudence on commence au point milieu
    ssc32.digitalOutput([2],[False]) # shutDown laser
        
    ssc32.close()
