from time import sleep
 
while True:
    import os
    import subprocess
    from subprocess import Popen, PIPE
 
    # The directory to sync:
    syncdir="/home/pi/Desktop/motion-pics"
 
    # Path to the Dropbox-uploaded shell script:
    uploader = "/home/pi/Dropbox-Uploader/dropbox_uploader.sh"
 
    # If set to "1", then files will be uploaded. If "0", files won't be uploaded:
    upload = 1 # Default is 1.
 
    # If set to "1", then upload new files without checking if they already exist. If "0", don't upload files that already exist:
    overwrite = 0 # Default is 0.
 
    # If set to "1", crawl sub folders for files to upload. If set to "0", just upload files in the main folder:
    recursive = 0 # Default is 0.
 
    # If set to "1", delete local file on successfull upload. If set to "0", files will not be deleted on the pi:
    deleteLocal = 1 # Default is 1.
 
    # Prints indented output:
    def print_output(msg, level):
        print((" " * level * 2) + msg)

    # Gets a list of files in a dropbox directory:
    def list_files(path):
 
        p = Popen([uploader, "list", path], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output = p.communicate()[0].decode("utf-8")
 
        fileList = list()

        lines = output.splitlines()      
        for line in lines:
            if line.startswith(" [F]"):
                line = line[5:]
                line = line[line.index(' ')+1:]
                fileList.append(line)
        return fileList

    # Uploads a single file:
    def upload_file(localPath, remotePath):
        p = Popen([uploader, "upload", localPath, remotePath], stdin=PIPE, stdout=PIPE, stderr=PIPE)

        output = p.communicate()[0].decode("utf-8").strip()

        if output.startswith("> Uploading") and output.endswith("DONE"):
            return 1
        else:
            return 0
 
    # Uploads files in a directory:
    def upload_files(path, level):
        fullpath = os.path.join(syncdir,path)

        print_output("Syncing " + fullpath,level)
 
        if not os.path.exists(fullpath):
 
            print_output("Path not found: " + path, level)
 
        else:
            # Get a list of file/dir in the path:
            filesAndDirs = os.listdir(fullpath)
 
            # Group files and directories:
            files = list()
 
            dirs = list()
 
            for file in filesAndDirs:
                filepath = os.path.join(fullpath,file)
 
                if os.path.isfile(filepath):
                    files.append(file)       
 
                if os.path.isdir(filepath):
                    dirs.append(file)

            print_output(str(len(files)) + " Files, " + str(len(dirs)) + " Directories",level)
  
            # If the path contains files and we don't want to override get a list of files in dropbox:
            if len(files) > 0 and overwrite == 0:
                dfiles = list_files(path)
 
            # Loop through the files to check to upload:
            for f in files:                                 
                print_output("Found File: " + f,level)   

                if upload == 1 and (overwrite == 1 or not f in dfiles): 
                    fullFilePath = os.path.join(fullpath,f)
 
                    relativeFilePath = os.path.join(path,f)  
 
                    print_output("Uploading File: " + f,level+1)   
 
                    if upload_file(fullFilePath, relativeFilePath) == 1:
                        print_output("Uploaded File: " + f,level + 1)
 
                        if deleteLocal == 1 and f != "DropboxFileUploader.py" and f != "motionPic.py":
 
                            print_output("Deleting File: " + f,level + 1)
 
                            os.remove(fullFilePath)                        
 
                    else:
                        print_output("Error Uploading File: " + f,level + 1)
 
            # If recursive loop through the directories:
            if recursive == 1:
                for d in dirs:
                    print_output("Found Directory: " + d, level)
 
                    relativePath = os.path.join(path,d)
 
                    upload_files(relativePath, level + 1)

    # Start upload:
    upload_files("",1)

    sleep(1)