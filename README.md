# Serili

Com serial commandlinetool in python using pyserial

This is a project that provides a GUI-based console for interacting with a serial port. The GUI is created using the ConsoleWindow module from the gui package. The project also includes a util module for handling exceptions and a threading module to run a separate thread for reading data from the serial port. The user can enter commands in the console to open and close a serial port, list available serial ports, send commands to the serial port, and exit the program. The serial and serial.tools modules are used to communicate with the serial port, and the comports function from serial.tools.list_ports is used to list available serial ports. The program continuously reads data from the serial port in a separate thread and displays it in the console. The user can also input commands to send to the serial port.

Going to further develop this alongside my Balancer project
