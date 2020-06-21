from rejestr_class import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
class procesor:
    def __init__(self,app):
        M = 50
        self.SP = M-1
        self.STOS = [None] * M
        self.VERIFY = "off"
        self.app = app
        self.AX = rejestr()
        self.BX = rejestr()
        self.CX = rejestr()
        self.DX = rejestr()
        self.DOS_version = 2.1
        self.rejestry = [self.AX,self.BX,self.CX,self.DX]

        self.rej_dict = {
            "AX"  : [self.AX, '-1'],
            "AXH" : [self.AX, 'H'],
            "AXL" : [self.AX,'L'],
            "BX"  : [self.BX, '-1'],
            "BXH" : [self.BX, 'H'],
            "BXL" : [self.BX,'L'],
            "CX"  : [self.CX, '-1'],
            "CXH" : [self.CX, 'H'],
            "CXL" : [self.CX, 'L'],
            "DX"  : [self.DX, '-1'],
            "DXH" : [self.DX, 'H'],
            "DXL" : [self.DX, 'L']
        }
    def clear_rej(self):
        M = 10
        self.SP = M-1
        self.STOS = [None] * M
        for i in range(len(self.rejestry)):
            self.rejestry[i].clear_cont()
        self.update_rej()

    def update_rej(self):
        for rej in self.rejestry:
                rej.update_preview()

    def execute(self, *args):
        getattr(self, args[0])(args[1], args[2])
        self.update_rej()

    def MOV(self, a, b,):
        val_a = getattr(self.rej_dict[a][0], self.rej_dict[a][1])

        try:
            val_b = getattr(self.rej_dict[b][0],self.rej_dict[b][1])
        except:
            val_b = b

        if (self.rej_dict[a][1] == 'L'):
            if (val_b > 255):
                diff = val_b - 255
                setattr(self.rej_dict[a][0],self.rej_dict[a][1], 255)
                diff = clip(diff,0,255)
                setattr(self.rej_dict[a][0],self.rej_dict[a[:2] + "H"][1], diff)
            else:
                setattr(self.rej_dict[a][0],self.rej_dict[a][1], val_b)
        else:
            val_b = clip(val_b,0,255)
            setattr(self.rej_dict[a][0],self.rej_dict[a][1], val_b)

    def ADD(self, a,b):
        val_a = getattr(self.rej_dict[a][0], self.rej_dict[a][1])
        try:
            val_b = getattr(self.rej_dict[b][0],self.rej_dict[b][1])
        except:
            val_b = b
        if (self.rej_dict[a][1] == 'L'):
            if (val_b + val_a > 255):
                diff = val_b - 255 + val_a
                diff = clip(diff,0,255)
                setattr(self.rej_dict[a][0],self.rej_dict[a][1], 255)
                self.ADD(a[:2] + "H",diff)
            else:
                val = clip(val_a + val_b,0,255)
                setattr(self.rej_dict[a][0],self.rej_dict[a][1], val)   
        else:
            val = clip(val_a + val_b,0,255)
            setattr(self.rej_dict[a][0],self.rej_dict[a][1], val)   
        
    def SUB(self, a,b):
        val_a = getattr(self.rej_dict[a][0], self.rej_dict[a][1])
        try:
            val_b = getattr(self.rej_dict[b][0],self.rej_dict[b][1])
        except:
            val_b = b

        val = clip(val_a - val_b,0,255)
        setattr(self.rej_dict[a][0],self.rej_dict[a][1], val)

    def INT01(self, a ,b):
        self.app.quit()
    def INT02(self, a ,b):
        val_h = getattr(self.rej_dict["AX"][0], "H")
        print(date.today())
    def INT21(self,a,b):    
        val_h = getattr(self.rej_dict["AX"][0], "H")
        # 2A [hex] = 42 - pobierz date
        if val_h == 42:
            setattr(self.rej_dict['DX'][0], 'L', date.today().day)
            setattr(self.rej_dict['DX'][0], 'H', date.today().month)
            setattr(self.rej_dict['CX'][0], 'H', int(str(date.today().year)[:2]))
            setattr(self.rej_dict['CX'][0], 'L', int(str(date.today().year)[:-2]))
        #  0 [hex] = 0 - koniec programu
        if val_h == 0:
            self.app.quit()

        if val_h == 44:
            setattr(self.rej_dict['CX'][0], 'H', datetime.now().time().hour)
            setattr(self.rej_dict['CX'][0], 'L', datetime.now().time().minute)
            setattr(self.rej_dict['DX'][0], 'H', datetime.now().time().second)
            setattr(self.rej_dict['DX'][0], 'L', 0)

        if val_h == 57:
            x =  getattr(self.rej_dict["DX"][0], "H")
            dirpath = os.getcwd()
            try:
                os.mkdir(dirpath + "/" + "folder_{}".format(x))
            except:
                pass

        if val_h == 1:
            ex.press_now = True
            ex.lose_focus()
        if val_h == 48:
            setattr(self.rej_dict['AX'][0], 'L', 2)
            setattr(self.rej_dict['AX'][0], 'H', 1)
            setattr(self.rej_dict['BX'][0], 'H', 255)
            setattr(self.rej_dict['BX'][0], 'L', 32)
            setattr(self.rej_dict['CX'][0], 'H', 12)
            setattr(self.rej_dict['CX'][0], 'L', 67)
        if val_h == 46:
            o = getattr(self.rej_dict["AX"][0], "L")
            if(o == 0):
                self.VERIFY = "off"
            if(o==1):
                self.VERIFY = "on"
            ex.console_print(self.VERIFY)


    def INT16(self,a,b):    
        val_h = getattr(self.rej_dict["AX"][0], "H")
        # odczytanie pozycji kursora
        if val_h == 3:
            x,y = win32api.GetCursorPos()
            setattr(self.rej_dict['CX'][0], 'H', clip(int(x),0,255))
            setattr(self.rej_dict['CX'][0], 'L', clip(int(y),0,255))


    def INT15(self,a,b):
        val_h = getattr(self.rej_dict["AX"][0], "H")
        if(val_h == 134):
            t = getattr(self.rej_dict["CX"][0], "H")+getattr(self.rej_dict["CX"][0], "L")
            print(t)
            time.sleep(t/100)
    def INT10(self,a,b):
        val_h = getattr(self.rej_dict["AX"][0], "H")
        if(val_h == 2):
            x = getattr(self.rej_dict["DX"][0], "H")
            y = getattr(self.rej_dict["DX"][0], "L")
            win32api.SetCursorPos((x,y))


    def PUSH(self, a,b):
        val_h = getattr(self.rej_dict[a][0], "H")
        val_l = getattr(self.rej_dict[a][0], "L")
        self.STOS[self.SP] = (val_h,val_l)
        self.SP -= 1
        print(self.STOS)
    def POP(self, a,b):
        self.SP += 1
        vals = self.STOS[self.SP]
        setattr(self.rej_dict[a][0],'H', vals[0])
        setattr(self.rej_dict[a][0],'L', vals[1])
        self.STOS[self.SP] = None
        print(self.STOS)
