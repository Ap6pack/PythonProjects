import win32con
import win32api
import win32gui



# get the handle of the calculator window

calculator_window = win32gui.FindWindow("CalcFrame", "Calculator")

# if the calculator window is found

if calculator_window != 0:

  # get the process ID of the calculator window

  process_id = win32process.GetWindowThreadProcessId(calculator_window)[1]


  # open the process with PROCESS_ALL_ACCESS privileges

  handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, process_id)


  # allocate memory for the message to be written to the calculator

  message = "This is a fun message!"

  message_size = len(message) + 1

  address = win32api.VirtualAllocEx(handle, 0, message_size, win32con.MEM_COMMIT, win32con.PAGE_READWRITE)


  # write the message to the allocated memory

  win32api.WriteProcessMemory(handle, address, message.encode(), message_size, None)


  # get the address of the SetWindowTextW function

  set_window_text_address = win32api.GetProcAddress(win32api.GetModuleHandle("User32.dll"), "SetWindowTextW")

  # create a remote thread to call the SetWindowTextW function with the address of the allocated memory as the argument

  win32api.CreateRemoteThread(handle, None, 0, set_window_text_address, address, 0, None)

  # close the handle to the process

  win32api.CloseHandle(handle)

