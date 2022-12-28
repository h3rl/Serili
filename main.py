
import threading
from gui import ConsoleWindow


def main():
    #while True:
    print("Port is open on ",port)

    # send AT command
    b = str("AT\r\n").encode()
    print("Writing bytes:")
    print(b)
    ser.write_timeout = 1
    try:
        ser.write(b)
    except serial.SerialTimeoutException:
        print("Write timeout")
        ser.close()
        #continue
    data = ser.readall()
    print(data)
    ser.close()

def TxThread(ser):
    """Thread to write to serial port"""
    while True:
        command = input("Enter command: ")
        # parse local commands first
        if command == "help":
            print("Commands: ping, exit")
            continue

        while not ser.writeable():
            time.sleep(1)
        if command == "ping":
            ser.write(b"ping\r\n")
        elif command == "exit":
            print("Exiting")
            ser.close()
            if ser.closed:
                print("Serial port closed successfully!")
            else:
                print("Failed to close serial port")
            sys.exit(0)
        else:
            print("Invalid command, help for list of commands")
        

def RxThread(ser):
    """Thread to read from serial port"""
    while True:
        if ser.readable():
            data = ser.readall()
            print(data)

# globals
app = None
should_exit = False
ser = None
recieve_thread = None
send_thread = None
app_thread = None

def on_user_command(command):
    # parse local commands first
    if command == "help":
        print("Commands: ping, exit")
        return
    elif command == "exit":
        if ser:
            ser.close()
            if ser.closed:
                print("Serial port closed successfully!")
            else:
                print("Failed to close serial port")
        should_exit = True

    if command == "ping":
        send_arduino_command("ping")
        
    # parse and send to arduino
    # send to arduino
    pass

def send_arduino_command(command):
    pass

if __name__ == "__main__":
    app = ConsoleWindow()
    app.on_command(on_user_command, ending=True)
    # create threads
    app_thread = threading.Thread(target=app.mainloop)
    app_thread.start()
    main()
    app_thread.join()
    
