import json

class Parser:
    def __init__(self, name, filename, default_wave="triangle", default_envelope=None):
        self.filename = filename
        self.default_wave = default_wave
        self.default_envelope = default_envelope
        self.data = {"metadata": {},
                     "instruments": {},
                     "order":       [],
                     "patterns":    {}}
        self.data["metadata"]["name"] = name
    
    def fromFile(self, name=None):
        if name==None: name = self.filename
        self.data = json.load(open(name, "r", encoding='utf-8'))
    
    def saveFile(self):
        json.dump(self.data, open(self.filename, "w", encoding="utf-8"))

    def editInstrument(self, pattern, wavetype=None, amplitude=None, downgrade=None, envelope=False):
        if type(pattern) is str: pattern = [pattern]
        for pat in pattern:
            if pat not in self.data["instruments"]:
                self.data["instruments"][pat] = {}
            self.data["instruments"][pat] = {"wavetype": self.default_wave}
            if wavetype!=None: self.data["instruments"][pat]["wavetype"] = wavetype
            if amplitude!=None: self.data["instruments"][pat]["amplitude"] = amplitude
            if downgrade!=None: self.data["instruments"][pat]["downgrade"] = downgrade
            if envelope==False: envelope = self.default_envelope
            self.data["instruments"][pat]["envelope"] = envelope

    def editOrder(self, line, offset=None):
        offset = self.__getOffset(offset, len(self.data["order"]))
        if type(line) is str: line=[line]
        for pattern in line:
            if pattern not in self.data["instruments"]:
                self.data["instruments"][pattern] = {"wavetype": self.default_wave, "envelope": self.default_envelope}
        while len(self.data["order"])-1<offset:
            self.data["order"].append([])
        self.data["order"][offset] = line

    def editPattern(self, pattern, note=None, length=None, offset=None, **kwargs):
        if pattern not in self.data["patterns"]:
            self.data["patterns"][pattern] = []
        offset = self.__getOffset(offset, len(self.data["patterns"][pattern]))
        while True:
            if len(self.data["patterns"][pattern])>offset: break
            self.data["patterns"][pattern].append(None)
        self.data["patterns"][pattern][offset] = {"note": note}|kwargs
        if length!=None: self.data["patterns"][pattern][offset]["length"] = length
    
    def __getOffset(self, offset, lendata):
        if offset==None:
            return lendata
        elif str(offset)[0]=="-":
            return lendata+offset
        else:
            return offset

    def getData(self): return self.data
