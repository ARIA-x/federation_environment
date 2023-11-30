import datetime, time, os

print ("simulation start ...")
time.sleep(1)

out_filename = './result/result.txt'
in_filename = './input/result.txt'

file_path = os.path.dirname(out_filename)

if not os.path.exists(file_path):
    os.makedirs(file_path)
else:
    print("directory: " + file_path + " exists")


with open(out_filename, "a+") as f:
    now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
    f.write("Hehehe...I'm sim-c ")
    f.write(now + '\n')
print ("simulation finished")
