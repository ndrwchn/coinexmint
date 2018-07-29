import sys, select

print ("You have 5 seconds to answer!")

i, o, e = select.select( [sys.stdin], [], [], 5 )

if (i):
  option = sys.stdin.readline().strip()
  print ("You said", option)
  if option == "s":
    print ('option: timeout')

else:
  print ("You said nothing!")