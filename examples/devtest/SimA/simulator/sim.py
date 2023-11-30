import datetime, time, os

print ("simulation start ...")
time.sleep(1)

filename = './result/result.txt'

file_path = os.path.dirname(filename)

if not os.path.exists(file_path):
    os.makedirs(file_path)
else:
    print("directory: " + file_path + " exists")

with open("./result/result.txt", "a+") as f:
    now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
    f.write("Hehehe...")
    f.write(now + '\n')
print ("simulation finished")
