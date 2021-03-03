from telnetlib import Telnet

class TelnetCon:
    def __init__(self, host, pw, db):
        self.tn = Telnet(host, 23)
        self.tn.set_debuglevel(db)
        #password = b'Elena9596'

        print(self.tn.read_until(b":"))
        self.tn.write(str.encode(pw))
        self.tn.write(b'\r')

        n, match, previous_text = self.tn.expect([br'Invalid', br'success'])
        if n == 0:
            print(previous_text)
        else:
            print(previous_text)



    def setTemp(self,temp):
        self.send(f'M104 S{temp}')

    def waitForMovesToFinish(self):
        self.send('M400')

    def dwell(self, seconds):
        self.send(f'G4 S{seconds}')

    def waitForHeater(self):
        self.send('M116')

    def send(self, msg):
        self.tn.write(str.encode(msg))
        self.tn.write(b'\r')


    def close(self):
        self.tn.close()
