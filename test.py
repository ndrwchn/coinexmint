import keyboard #Using module keyboard
from threading import Timer

def t_over():
    
    print('time over')
    #keyboard.press_and_release('enter')

def key_option(_type):
    s = ''
    timeout0 = 15 # seconds to wait input
    t = Timer(timeout0,t_over)
    t.start()
    prompt = "You have %d seconds to choose the correct answer...\n" % timeout0
    print(prompt)

    
    try: #used try so that if user pressed other than the given key error will not be shown
        if keyboard.is_pressed('s'):#if key 'q' is pressed 
            print('You Pressed s Key!')
            s = 'timeout'
             #finishing the loop
        elif keyboard.is_pressed('c'):
            print('you press c key')
            s = 'done'
            
        elif keyboard.is_pressed('f'):
            print('you press c key')
            s = 'flipping ' + _type
        else:
            s = ''
        
    except:
        print('error')#if user pressed a key other than the given key the loop will break

    # keyboard.press_and_release('enter')
    t.cancel()
    t.join()
    if t.isAlive():
        print('timer is alive')
    else:
        print('timer is no more alive')
    
    if t.finished:
        print('timer is finished')

    return s


FF = key_option('by')

print(FF)