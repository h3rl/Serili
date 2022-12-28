from gui import ConsoleWindow

import threading
import time
import serial
import serial.tools

import util

# globals
app = None
should_exit = False
ser = None
recieve_thread = None
 
def RxThread():
    """Thread to read from serial port"""
    while not should_exit:
        if ser and ser.readable():
            try:
                data = ser.readall()
            except util.SerialTimeoutException:
                app.console_log("Read Timeout","error")
            
            if data:
                try:
                    app.console_log(data.decode())
                except:
                    app.console_log(data)
        time.sleep(0.1)

def on_user_command(command):
    # parse local commands first
    if command == "help":
        app.console_log("Commands: ping, exit")
        return
    elif command == "exit":
        if ser:
            ser.close()
            if ser.closed:
                app.console_log("Serial port closed successfully!")
            else:
                app.console_log("Failed to close serial port")
        should_exit = True
        app.quit()
    elif command == "ping":
        send_arduino_command("ping")
    else:
        app.console_log("Invalid command, help for list of commands")
        return

def send_arduino_command(command):
    if not ser:
        app.console_log("No serial port open")
        return

    tick = 0
    while not ser.writable():
        time.sleep(0.1)
        tick += 1
        if tick > 50:# 5 seconds
            app.console_log("Timed out, serial port not writable","error")
            return

    b = str(command + app.get_line_ending()).encode()
    ser.write_timeout = 1
    try:
        ser.write(b)
    except util.SerialTimeoutException:
        app.console_log("Write Timeout","error")
    return

if __name__ == "__main__":
    app = ConsoleWindow()
    app.on_command(on_user_command)
    # create threads
    recieve_thread = threading.Thread(target=RxThread)
    recieve_thread.start()
    app.mainloop()
    
    # clean up
    should_exit = True
    recieve_thread.join()
    
