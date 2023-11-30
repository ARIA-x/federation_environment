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

with open(in_filename, "r") as f:
    prev_results = f.readlines()

with open(out_filename, "a+") as f:
    now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
    for line in prev_results:
        f.write(line)
    f.write("Fufufu...I'm sim-b ")
    f.write(now + '\n')
print ("simulation finished")
