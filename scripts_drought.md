f=open("D:/enviournmental programming/P_June2019.asc", "r")
for line in f:
    print (line)
    lines = f.readlines()
data_lines = lines[6:]
data=[]
ncols= int(f.readlines().split()[1])
nrows= int(f.readlines().split()[1])
for i in range (3):
    f.readlines()
  ###what is this
