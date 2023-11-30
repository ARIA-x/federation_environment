import os, errno
from configparser import ConfigParser, ExtendedInterpolation


# TODO: 相対パスのサポート

class SimulationConfig:

    name = "sim"
    path = None
    cmd  = None
    args = None
    baseImage = None
    update = False
    workdir = None
    indir = None
    outdir = None
    retrieve = None

    def __init__(self, filename=None):
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        if filename is None:
            pass
        else:
            self.config.read(filename)

    def read(self, filename):
        if not os.path.exists(filename):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filename)
        self.config.read(filename)

        ## Mandatory
        ## BASIC section
        self.name     = self.config['BASIC']['NAME']
        self.path     = self.config['BASIC']['PATH']
        self.retrieve = self.config['BASIC']['RETRIEVE']

        ## SIMULATOR section
        self.cmd     = self.config['SIMULATOR']['CMD']
        self.args    = self.config['SIMULATOR']['ARGS'].split(', ')
        self.workdir = self.config['SIMULATOR']['WORKDIR']
        self.outdir  = self.config['SIMULATOR']['OUTDIR']
        
        ## REQUIREMENT section
        self.baseImage  = self.config['REQUIREMENT']['FROM']
        self.update     = self.config['REQUIREMENT'].getboolean('UPDATE')

        ## Arbitrary
        try:
            self.indir   = self.config['SIMULATOR']['INDIR']
        except KeyError as e:
            print("configuration skip: " + str(e))

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def setIndir(self, dir):
        self.indir = dir

    def getIndir(self):
        return self.indir

    def setOutdir(self, dir):
        self.outdir = dir

    def getOutdir(self):
        return self.outdir

    def setRetrieve(self, dir):
        self.retrieve = dir

    def getRetrieve(self):
        return self.retrieve

    def setWorkDir(self, dir):
        self.workdir = dir

    def getWorkDir(self):
        return self.workdir

    def setUpdate(self, update):
        self.update = update

    def getUpdate(self):
        return self.update

    def setBaseImage(self, name):
        self.baseImage = name

    def getBaseImage(self):
        return self.baseImage

    def setPath(self, path):
        self.path = path

    def getPath(self):
        return self.path

    def setCmd(self, cmd):
        self.cmd = cmd

    def setArgs(self, args):
        self.args = args

    def getCmdline(self):
        if (self.args):
            return self.cmd + ' ' + ' '.join(self.args)
        else:
            return self.cmd
    
    def ready(self):
        if (self.cmd != None) and (self.path != None):
            return True
        else:
            return False


### For test
if __name__ == "__main__":
    path = r"C:\Users\kohig\Works\phasezero\examples\devtest\SimA\\"
    file = r"C:\Users\kohig\Works\phasezero\examples\devtest\SimA\config.ini"
    conf = SimulationConfig()
    conf.read(file)
    print(conf.getPath())
    print(conf.getCmdline())
    print(conf.getBaseImage())
    print(conf.getWorkDir())
    print(conf.getUpdate())