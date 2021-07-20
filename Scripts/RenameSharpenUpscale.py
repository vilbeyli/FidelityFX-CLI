#=================================================================================================#
# Python script to mass-handle image files.
#
# Features:
# - Rename
# - Reverse, if named FileName_####.png
# - AMD FidelityFX Contrast Adaptive Sharpening (CAS) Filter
# - AMD FidelityFX Super Resolution 1.0 (FSR 1.0) 
#   - Edge-Adaptive Spatial Upsampling (EASU)
#   - Robust Contrast Adaptive Sharpening (RCAS) 
#
#=================================================================================================
import os
import sys, getopt
from os.path import isfile, join
import re

# ------------------------------------------------------
# DATA
# ------------------------------------------------------
DEFAULT_DIR='./'
DETAULT_STRING_TO_RENAME='Frame'
FFX_CLI_FILE=os.path.join(os.getcwd(), 'FidelityFX_CLI.exe')

# ------------------------------------------------------
# FUNCTIONS
# ------------------------------------------------------
def PrintHelp():
    print("Example Usages:")
    print("    RenameSharpenUpscale.py -i 'OldName' -o 'NewName'")
    print("    RenameSharpenUpscale.py -d C:/FileDirectory -i 'OldName' -o 'NewName'")
    print("    RenameSharpenUpscale.py -d C:/FileDirectory -i 'OldName' -o 'NewName' -r")
    print("    RenameSharpenUpscale.py -d C:/FileDirectory -s 0.8")
    print("    RenameSharpenUpscale.py -d C:/FileDirectory -u 3840x2160")
    print("")
    print("-d : directory to search & replace")
    print("-i : input search string")
    print("-o : string to be replaced with")
    print("-r : invert the file order, assuming FileName_FrameNumber.png, e.g. Frame_0001.png")
    print("-s : run FidelityFX Contrast Adaptive Sharpening (CAS) with the specified Sharpness value on each image in the given directory")
    print("-u : run FidelityFX Super Resolution 1.0 to upscale to given resolution, e.g. -u 2560x1440")
    print("")

def GetRenamedFilesFromArgList(ArgList):
    RenamedFileList=[]
    for arg in ArgList:
        RenamedFileList.append(arg[1])
    return RenamedFileList

def UpscaleFiles(FileList, UpscaledResolutionStr, SharpenAmount = 0.0):
    # perform checks
    if not os.path.exists(FFX_CLI_FILE):
        print("FidelityFX Command Line program doesn't exist: " + FFX_CLI_FILE)
        return
    OutResolutionX=0
    OutResolutionY=0
    Tokens=UpscaledResolutionStr.split("x")
    if len(Tokens) != 2:
        print("FidelityFX Super Resolution: Invalid image dimensions are provided: " + UpscaledResolutionStr)
        return
    OutResolutionX = int(Tokens[0])
    OutResolutionY = int(Tokens[1])
    if OutResolutionX <= 0 or OutResolutionY <= 0:
        print("FidelityFX Super Resolution: Invalid image dimensions are provided: " + UpscaledResolutionStr)
        return

    # TODO:
    bSharpen=SharpenAmount != 0.0
    InResolutionX=0
    InResolutionY=0
    RCASSharpen=0.0


    # print status
    print("")
    print("Running AMD FidelityFX Super Resolution...")
    print("    " + str(InResolutionX) + "x" + str(InResolutionY) + " -> " + UpscaledResolutionStr)
    if bSharpen:
        print("    Sharpness=" + str(SharpenAmount) + " | RCAS Sharpness=" + str(RCASSharpen))

    # EASU()
    #build cmd args
    cmd_args = " -Scale " + str(OutResolutionX) + " " + str(OutResolutionY) + " -Mode EASU "
    print(FFX_CLI_FILE + cmd_args)
    IOFileList=[]
    for FilePath in FileList:
        Find=os.path.basename(FilePath)
        Replace="_" + Find
        OutFilePath=str(FilePath).replace(Find, Replace)
        cmd_args += str(FilePath) + " " + str(OutFilePath) + " "
        IOFileList.append([FilePath, OutFilePath])

    # print I/O files
    for IOFilePair in IOFileList:
        print("    " + IOFilePair[0] + " " + IOFilePair[1])
    print("")

    # Run FidelityFX EASU
    FFX_CMD=FFX_CLI_FILE + " " + cmd_args
    os.system(FFX_CMD)

    # RCAS()
    if SharpenAmount != 0.0:
        # TODO:


    return

def SharpenFiles(FileList, Sharpness):
    if not os.path.exists(FFX_CLI_FILE):
        print("FidelityFX Command Line program doesn't exist: " + FFX_CLI_FILE)
        return
    
    print("")
    print("Running AMD FidelityFX Contrast Adaptive Sharpening...")
    print(FFX_CLI_FILE + " -Sharpness " + str(Sharpness))

    #build cmd args
    cmd_args_sharpness = "-Sharpness " + str(Sharpness) + " "
    cmd_args = cmd_args_sharpness
    CasIOFileList=[]
    for FilePath in FileList:
        Find=os.path.basename(FilePath)
        Replace="_" + Find
        OutFilePath=str(FilePath).replace(Find, Replace)
        cmd_args += str(FilePath) + " " + str(OutFilePath) + " "
        CasIOFileList.append([FilePath, OutFilePath])

    # build OS call string
    FFX_CMD=FFX_CLI_FILE + " " + cmd_args
    for IOFilePair in CasIOFileList:
        print("    " + IOFilePair[0] + " " + IOFilePair[1])
    print("")
    os.system(FFX_CMD)

# ------------------------------------------------------
# MAIN
# ------------------------------------------------------
def main(argv):

    # program parameters
    InputDirectory=os.getcwd() # current path of the py file
    StringToSearch=DETAULT_STRING_TO_RENAME
    StringToReplace=''
    InvertOrder=False
    FindAndReplace=False
    Sharpen=False
    SharpenAmount=0.0
    Upscale=False
    UpscaledResolutionStr=""

    # https://www.tutorialspoint.com/python/python_command_line_arguments.htm
    # read command line arguments:
    # -d for which directory to search for files
    # -i for which string to search in file names
    # -o to replace the string specified with -i
    try:
        opts, args = getopt.getopt(argv, "hd:i:o:rs:u:", [""])
    except getopt.GetoptError:
        PrintHelp()
        sys.exit(-1)
    
    for opt, arg in opts:
        if opt == '-h':
            PrintHelp()
            sys.exit()
        elif opt in ("-d"):
            InputDirectory=arg
        elif opt in ("-i"):
            StringToSearch=arg
            FindAndReplace = True
        elif opt in ("-o"):
            StringToReplace=arg
        elif opt in ("-r"):
            InvertOrder=True
        elif opt in ("-s"):
            Sharpen=True
            SharpenAmount=arg
        elif opt in ("-u"):
            Upscale=True
            UpscaledResolutionStr=arg
        else:
            print("Invalid Arg: ") + arg
    
    # do some checks before running the code
    if(not FindAndReplace and not InvertOrder and not Sharpen and not Upscale):
        print("Invalid  input: specify name to replace using -i or specify inverting order with -r")
        PrintHelp()
        exit(-1)
    if not os.path.exists(InputDirectory):
        print("Specified input directory '" + str(InputDirectory) + "' doesn't exist. Exiting...")
        exit(-1)

    # print params and start executing
    print('PARAMETERS')
    print('    InputDirectory  = ' + str(InputDirectory))
    if FindAndReplace:
        print('    StringToSearch  = ' + str(StringToSearch))
        print('    StringToReplace = ' + str(StringToReplace))
    if InvertOrder:
        print('    Reverse Order   = ' + str(InvertOrder))
    if Sharpen:
        print('    FFX_CAS Sharpen = ' + str(SharpenAmount))
    if Upscale:
        print('    FSR Upscale = ' + str(UpscaledResolutionStr))
    print('')


    # list files in the target directory
    # https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
    Files = [f for f in os.listdir(InputDirectory) if isfile(join(InputDirectory, f))]
    print('Files in Directory : ' + str(len(Files)))

    FilesToRename=[]
    if FindAndReplace:
        # search for ReplaceTarget in the file names
        # and get the list of files to be renamed
        FilesToRename=[f for f in Files if (StringToSearch in f)]
        print('Files to Rename    : ' + str(len(FilesToRename)))
        print('')

    # rename the files
    # https://stackoverflow.com/questions/2491222/how-to-rename-a-file-using-python
    if len(FilesToRename) == 0:
        if FindAndReplace:
            print("No matching files found to rename, skipping renaming.")

        # if we're not renaming anything, then collect all the image files in the given directory
        Files=[join(InputDirectory, FileName) for FileName in Files if (".png" in FileName.lower())]

        # TODO: invert frame order?
        

        if Upscale:
            UpscaleFiles(Files, UpscaledResolutionStr, SharpenAmount)

        if Sharpen and not Upscale:
            SharpenFiles(Files, SharpenAmount)
        
    else:
        OSRenameParams=[]
        print('Renaming...')

        # record parameters to os.rename() call: [OldDir, NewDir]
        for OldFileName in FilesToRename:
            NewName=OldFileName.replace(StringToSearch, StringToReplace) # find & replace
            NewFileDir=join(InputDirectory, NewName)     # get full path
            OldFileDir=join(InputDirectory, OldFileName) # get full path
            OSRenameParams.append([OldFileDir, NewFileDir])
        
        # invert frame ordering if specified
        if InvertOrder:            
            RenamedFileList=GetRenamedFilesFromArgList(OSRenameParams) # extract the 2nd parameters which are the resulting file names from renaming
            RenamedFileList.reverse() # reverse the list and the ordering

            for i in range(0, len(RenamedFileList)): # then write back to the parameters the reverted order
                OSRenameParams[i][1] = RenamedFileList[i]

        # finally, actually do the renaming
        for params in OSRenameParams:
            os.rename(params[0], params[1]) 
            print(str(params[0]).replace('\\', '/') + " -> " + str(params[1]).replace('\\', '/'))
        
        # run FFX-CAS if specified
        if Sharpen:
            RenamedFileList=GetRenamedFilesFromArgList(OSRenameParams)
            SharpenFiles(RenamedFileList, SharpenAmount)
            

if __name__ == "__main__":
   main(sys.argv[1:])