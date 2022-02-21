import win32clipboard
import win32con
import ctypes
import win32api
import win32gui
from ctypes import wintypes

byref = ctypes.byref
user32 = ctypes.windll.user32
INPUT_KEYBOARD = 1
KEYEVENTF_UNICODE  = 0x0004
KEYEVENTF_KEYUP       = 0x0002
def getClipBoardContent():
    # get clipboard data
    win32clipboard.OpenClipboard()
    data = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()
    return data


HOTKEYS = {
  1 : (win32con.VK_INSERT, win32con.MOD_WIN),
  2 : (ord("V"), win32con.MOD_ALT),
  2 : (ord("V"), win32con.MOD_ALT|win32con.MOD_CONTROL),
}
ULONG_PTR = ctypes.c_ulong if ctypes.sizeof(ctypes.c_void_p) == 4 else ctypes.c_ulonglong


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [('dx' ,wintypes.LONG),
                ('dy',wintypes.LONG),
                ('mouseData',wintypes.DWORD),
                ('dwFlags',wintypes.DWORD),
                ('time',wintypes.DWORD),
                ('dwExtraInfo',ULONG_PTR)]

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [('wVk' ,wintypes.WORD),
                ('wScan',wintypes.WORD),
                ('dwFlags',wintypes.DWORD),
                ('time',wintypes.DWORD),
                ('dwExtraInfo',ULONG_PTR)]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [('uMsg' ,wintypes.DWORD),
                ('wParamL',wintypes.WORD),
                ('wParamH',wintypes.WORD)]

class DUMMYUNIONNAME(ctypes.Union):
    _fields_ = [('mi',MOUSEINPUT),
                ('ki',KEYBDINPUT),
                ('hi',HARDWAREINPUT)] 

class INPUT(ctypes.Structure):
    _anonymous_ = ['u']
    _fields_ = [('type',wintypes.DWORD),
                ('u',DUMMYUNIONNAME)]



def send_unicode(s):
    i = INPUT()
    i.type = INPUT_KEYBOARD
    for c in s:
        i.ki = KEYBDINPUT(0,ord(c),KEYEVENTF_UNICODE,0,0)
        user32.SendInput(1,byref(i),ctypes.sizeof(INPUT))
        i.ki.dwFlags |= KEYEVENTF_KEYUP
        user32.SendInput(1,byref(i),ctypes.sizeof(INPUT))


for id, (vk, modifiers) in HOTKEYS.items ():
  print ("Registering id", id, "for key", vk)
  if not user32.RegisterHotKey (None, id, modifiers, vk):
    print( "Unable to register id", id)

try:
  msg = wintypes.MSG ()
  while user32.GetMessageA (byref (msg), None, 0, 0) != 0:
    if msg.message == win32con.WM_HOTKEY:
        print("got message",msg.wParam)        
        win_name = win32gui.GetWindowText (win32gui.GetForegroundWindow())
        print(win_name)
        if -1!=win_name.find("远程桌面连接"):
          print("当前为远程，发送剪切板")
          clipContent = getClipBoardContent()
          print(clipContent)
          win32api.keybd_event(0x35,0,0,0)
          send_unicode(clipContent)
        

    user32.TranslateMessage (byref (msg))
    user32.DispatchMessageA (byref (msg))

finally:
  for id in HOTKEYS.keys ():
    user32.UnregisterHotKey (None, id)
