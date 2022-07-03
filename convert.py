import os
import subprocess

needed_patients = []
def checkFolder(location):
    os.chdir(location)
    os.system("pwd")
    try:
        layout_file = subprocess.check_output("ls -l | grep _layout", shell=True).decode().split("\n")
    except subprocess.CalledProcessError as grepexc:
        print("error code", grepexc.returncode, grepexc.output)
        return False
    if len(layout_file) > 1:
        for i in range(len(layout_file) - 1):
            temp_file = layout_file[i].split(" ")
            file_name = temp_file[len(temp_file) - 1]
            #print(file_name)
            types = subprocess.check_output("cat " + file_name, shell=True).decode()
            #print(types)
            return "PLETH" in types and "ABP" in types
    else:
        return False

def findABPAndPLETH():
    os.chdir("../mimic/physionet.org/files/mimic3wdb-matched/1.0/p00")
    for i in range(0, 10):
        patients_temp = subprocess.check_output("ls -l", shell=True).decode().split("\n")
        patients = []
        for j in range(len(patients_temp) - 1):
            temp = patients_temp[j]
            start = temp.find("p0")
            patients.append(temp[start:])
        os.chdir("../")
        #os.system("ls -l")
        for j in range(2, 5): #len(patients)):
            correct = checkFolder("p0" + str(i) + "/" + patients[j] + "/")
            if correct:
                needed_patients.append(patients[j])
            os.chdir("../../")
        if(i < 9):
            os.chdir("p0" + str(i + 1))
    os.chdir("../../../../../../Scripts")
    write_File = os.open("needed_patients", os.O_RDWR)
    for s in needed_patients:
        os.write(write_File, str.encode(s + "\n"))
    os.close(write_File)

def convertToMAT():
    needed_patients = subprocess.check_output("cat needed_patients", shell=True).decode().split("\r\n")
    print(needed_patients)
    os.chdir("../mimic/physionet.org/files/mimic3wdb-matched/1.0/")
    for i in range(len(needed_patients)):
        os.chdir(needed_patients[i][0:3] + "/" + needed_patients[i])
        os.system("pwd")
        file_names = subprocess.check_output("ls -l | grep " + needed_patients[i], shell=True).decode().split("\n")
        print(file_names)
        for j in range(len(file_names)):
            file_name = file_names[j]
            file_name = file_name[file_name.find(needed_patients[i]):]
            os.system("wfdb2mat -r " + file_name)
        move_files = subprocess.check_output("ls -l | grep m.mat", shell=True).decode().split("\n")
        header_files = subprocess.check_output("ls -l | grep m.hea", shell=True).decode().split("\n")
        move_file = []
        header_file = []
        for j in range(len(move_files)):
            move_file.append(move_files[j][move_files[j].find("p0"):])
            header_file.append(header_files[j][header_files[j].find("p0"):])
        os.system("mkdir " + needed_patients[i])
        os.system("mv " + needed_patients[i] + " ../../../../../../../Scripts/MAT_Files/" + needed_patients[i])
        for j in range(len(move_files) - 1):
            os.system("mv " + move_file[j] + " ../../../../../../../Scripts/MAT_Files/" + needed_patients[i] + "/" + move_file[j])
            os.system("mv " + header_file[j] + " ../../../../../../../Scripts/MAT_Files/" + needed_patients[i] + "/" + header_file[j])
        os.chdir("../../")

def second_check():
    os.chdir("MAT_Files")
    folders = subprocess.check_output("ls -l", shell=True).decode().split("\n")
    folder = []
    for i in range(len(folders)):
        folder.append(folders[i][folders[i].find("p0"):])
    for i in range(1, len(folder) - 1):
        os.system("pwd")
        os.chdir(folder[i])
        try:
            headers = subprocess.check_output("ls -l | grep .hea", shell=True).decode().split("\n")
            header = []
            for j in range(len(headers) - 1):
                header.append(headers[j][headers[j].find("p0"):])
                check = subprocess.check_output("cat " + header[j]).decode()
                if(not("ABP" in check and "PLETH" in check)):
                    os.system("rm -f " + header[j])
                    print(header[j][:len(header[j]) - 4])
                    os.system("rm -f " + header[j][:len(header[j]) - 4] + ".mat")
            os.chdir("../")
        except subprocess.CalledProcessError as grepexc:
            print("error code", grepexc.returncode, grepexc.output)
            os.chdir("../")

def debug_test():
    os.chdir('../MIMIC-III_DATA/physionet.org/files/mimic3wdb-matched/1.0/p00/p000030/')

#debug_test()
findABPAndPLETH()
convertToMAT()
second_check()
