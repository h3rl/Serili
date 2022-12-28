from gui import ConsoleWindow

import threading
import time
import serial
import serial.tools
from serial.tools.list_ports import comports

from util import *
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
    global ser
    # parse local commands first
    command, *args = command.split(" ")
    if command == "help":
        app.console_log("SERIAL commands")
        app.console_log(" open <port> <baudrate>", "hint")
        app.console_log(" close", "hint")
        app.console_log(" listport", "hint")
        
        app.console_log("CLIENT commands")
        app.console_log(" exit", "hint")

        return
    elif command == "exit":
        if ser and ser.is_open:
            ser.close()
        should_exit = True
        app.quit()
    elif command == "ping":
        send_arduino_command("ping")
    elif command == "close":
        if ser and ser.is_open:
            ser.close()
            if ser.closed:
                app.console_log("Serial port closed successfully!")
            else:
                app.console_log("Failed to close serial port")
        else:
            app.console_log("No serial port open")
    elif command in ["open", "connect"]:
        if len(args) == 0:
            app.console_log("Invalid arguments","warning")
            app.console_log("Usage: open <port> <baudrate>", "hint")
            app.console_log("hint: use listport to list available ports", "hint")
            return
        
        port, baudrate = None, None        
        try:
            port = args[0]
            if len(args) > 1:
                baudrate = int(args[1])
            else:
                app.console_log("Using default baudrate: 9600","hint")
                baudrate = 9600
        except ValueError:
            app.console_log("Invalid arguments","warning")
            app.console_log("Usage: open <port> <baudrate>", "hint")
            app.console_log("hint: use listport to list available ports", "hint")
            return
        if ser and ser.is_open:
            app.console_log("Some serial port is already open","warning")
            return
        try:
            ser = serial.Serial(port, baudrate, timeout=1)
        except serial.SerialException as e:
            app.console_log(f"Failed to open serial port: {port}","error")
            return
        if ser.is_open:
            app.console_log(f"{port} opened", "success")
        else:
            app.console_log(f"Failed to open serial port: {port}","error")
            return
    elif command in ["listport", "list", "ports"]:
        ports = comports()
        for port in ports:
            app.console_log(port.device)
        else:
            app.console_log("No ports found","warning")
        return
    elif command == "cls":
        app.clear_console()
    else:
        app.console_log("Invalid command, help for list of commands","warning")
        return

def send_arduino_command(command):
    if not ser:
        app.console_log("No serial port open","error")
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
    except serial.SerialTimeoutException:
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
    
