# this module defines the class for the storage of test parameters

class GeneralLimits:
    """
    defines the limitting values for the given test script parameter
    """
    def __init__(self, Upper=None, Lower=None, AllowedList=None):
        
        self.setLimits(Upper, Lower, AllowedList)
        #self.AllowedList = AllowedList
        #self.Upper = Upper
        #self.Lower = Lower
        self.fitsIn = []
        return
    def _isWithinLimits(self, value):
        """
        recursive test if the given value is in the limits
        for often cases of iterrable values
        """
        try:
            for segment in value:
                self.fitsIn.append( self._isWithinLimits(segment))
                fitsIn = True
        except:
            fitsIn = True # init the return answer for unlimited parameters
            if self.AllowedList:
                if not (value in self.AllowedList):
                    fitsIn = False
            else:
                if self.Lower:
                    if value < self.Lower:
                        fitsIn = False
                if self.Upper:
                    if value > self.Upper:
                        fitsIn = False
        return fitsIn
    def _isCorrectString(self,value):
        """ returns an YES/NO answer if the given string is in the ALlowed List """
        correctString = True # init the return answer for unlimited parameters
        if self.AllowedList:
            if not (value in self.AllowedList):
                correctString = False
        return correctString
    def isWithinLimits(self, value):
        if isinstance(value,type('string')):
            answer = self._isCorrectString(value)
        else:
            answer = self._isWithinLimits(value)
        # test if the value was iterable:
        length = len(self.fitsIn)
        if length > 0:
            for segment in self.fitsIn:
                answer = answer * segment
        else:
            pass
        self.fitsIn = []          
        return answer
    def getLimits(self):
        Upper = self.Upper
        Lower = self.Lower
        AllowedList = self.AllowedList
        return [Upper, Lower, AllowedList]
    def setLimits(self,Upper=None, Lower=None, AllowedList=None):
        if AllowedList == None:
            self.AllowedList = None
            self.Upper = Upper
            self.Lower = Lower
        else:
            self.AllowedList = AllowedList
            self.Upper = None
            self.Lower = None
    
class GeneralParameter:
    def __init__(self, Name, Unit, Type, Iterable,  Limits, Description):
        # initialize the parameters
        self.AllovedTypes = ['float', 'count', 'boolean', 'name']
        #self.values = {}
        self.setName(Name)
        self.setUnit(Unit)
        self.Limits = GeneralLimits(Upper=Limits[0], Lower=Limits[1], AllowedList=Limits[2])
        self.setType(Type,Iterable)
        self.setDescription(Description)
        self.Value = None
        #self.values['Limits'] = GeneralLimits(Upper=Limits[0], Lower=Limits[1], AllowedList=Limits[2])
        #self.values['Limits'].Upper=Limits[0]
        #self.values['Limits'].Lower=Limits[1]
        #self.values['Limits'].AllowedList=Limits[2]
        #if Limits == [ None, None, None]:
        #    self.values['Limits'] = GeneralLimits()
        #else:
        #    self.values['Limits'] = GeneralLimits()
        #    self.values['Limits'].Upper=Limits[0]
        #    self.values['Limits'].Upper=Limits[0]
        return
    def setValue(self, Value):
        if self.Limits.isWithinLimits(Value):
            self.Value = Value
        else:
            answer = "Parameter out of limits"
        answer = 0
        # test if the parameter is iterable:
        try:
            length = len(Value)
            iterable = True
        except:
            iterable = False
        self.iterableParam = iterable
        return answer
    def getValue(self):
        value = self.Value
        return value
    def getType(self):
        typeOfParam = self.Type
        iterableParam = self.iterableParam
        return (typeOfParam, iterableParam)
    def setType(self,Type,iterableParam):
        answer = None
        if Type in self.AllovedTypes:
            self.Type = Type
            if iterableParam:
                self.iterableParam = iterableParam
            else:
                self.iterableParam = False
        else:
            answer = 'bad parameter type'
        return answer
    def setDescription(self, Description):
        self.Description = Description
        answer = 0
        return answer
    def getDescription(self):
        Description = self.Description
        return Description
    def setLimits(self, Limits):
        self.Limits.setLimits(Limits)
        answer = 0
        return answer
    def getLimits(self):
        Limits = self.Limits.getLimits()
        return Limits
    def setName(self, Name):
        self.Name = Name
        answer = 0
        return answer
    def getName(self):
        Name = self.Name
        return Name
    def setUnit(self, Unit):
        self.Unit = Unit
        answer = 0
        return answer
    def getUnit(self):
        Unit = self.Unit
        return Unit
