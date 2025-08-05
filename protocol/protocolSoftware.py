import subprocess as sp
import webbrowser as Linkexecuter

class ProtocolExecuteLink:
    def loadLink(link):
        Linkexecuter.open(link)

    def loadLinkNSFW():
        Linkexecuter.open("https://huggingface.co/spaces/Heartsync/NSFW-image?not-for-all-audiences=true")
        

class ProtocolExecuteFile:
    def __init__(self, FilePath):
        self.FilePath = FilePath
    
    def ExecuteFileC(self, exeFilePath):
        sp.call(["gcc", self.FilePath, "-o", exeFilePath])
        sp.call([exeFilePath])

    def ExecuteFilepy(self):
        sp.call(["python", self.FilePath])

    def WriteFile(self, content):
        file = open(self.FilePath, "w")
        file.write(content)
        file.close()
    
    def Removelines(self):
        with open(self.FilePath, 'r+') as fp:
            lines = fp.readlines()
            fp.seek(0)
            fp.truncate()
            fp.writelines(lines[1:-1])
        
            