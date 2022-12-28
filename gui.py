import tkinter as tk
from typing import Callable

class Config():
    def __init__(self,filename="config.ini"):
        self._filename = filename
        self.console_history_size = 100
        self._line_endings = ["NONE", "CR", "LF", "CRLF"]
        self.line_ending = "CRLF"
        self._err_log = []

    def on_error(self, error_callback):
        self.error_callback = error_callback

    def create_config(self):
        file = None
        try:
            file = open(self._filename, "w")
        except PermissionError:
            return "Permission denied"
            
        
        file.write("# Config file for the console window\n")
        for key, value in self.__dict__.items():
            if key.startswith("_"): # ignore private variables
                continue
            file.write(f"{key}={value}\n")
        file.close()
        return "Config file created"

    def validate_config_keyval(self, key, value):
        # check that given kets have a valid value
        #print(value)
        if key == "console_history_size":
            if type(value) != int:
                return False
        elif key == "line_ending":
            #print(value)
            if value not in self._line_endings:
                return False

        return True

    def read_config(self):
        file = None
        try:
            file = open(self._filename, "r")
        except FileNotFoundError:
            return self.create_config()

        try:
            for line in file.readlines():
                line = line.strip().replace(" ","")
                if line.startswith("#"):
                    continue
                key, value = line.split("=")


                # try convert value to int, float, bool or str
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        if value.lower() == "true":
                            value = True
                        elif value.lower() == "false":
                            value = False

                
                # check that key is valid
                if not self.validate_config_keyval(key, value):
                    self._err_log.append(f"Skipping invalid setting: {key}={value}")

                self.__dict__[key] = value
        except ValueError:
            return "Invalid config file"
        
        return "Config file loaded"

class ConsoleWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.VARS = Config()
        self.VARS.read_config()
        self.command_history = []
        self.history_index = -1

        # set callbacks to none
        self.command_callback = None

        # Window properties
        self.title("Console Window")
        self.geometry("640x480")
        # Main elements
        self.output_frame = tk.Frame(self)
        self.scrollbar = tk.Scrollbar(self.output_frame)
        self.console_output = tk.Text(self.output_frame, yscrollcommand=self.scrollbar.set)
        # Configuration
        self.scrollbar.config(command=self.console_output.yview)
        self.console_output.config(state="disabled", cursor="arrow")
        
        # Pack the elements
        self.console_output.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.output_frame.pack(side="top", fill="both", expand=True)

        self.input_frame = tk.Frame(self)
        self.input_prompt_label = tk.Label(self.input_frame, text="> ")
        self.console_input = tk.Entry(self.input_frame)
        self.VARS.lineending = tk.StringVar(self.input_frame)
        self.VARS.lineending.set(self.VARS.line_ending)
        self.lineending_selector = tk.OptionMenu(self.input_frame, self.VARS.lineending, "NONE","CR", "LF", "CRLF")
        #self.console_input.option_add("height", 5)

        # handle input function binding
        self.console_input.bind("<Return>", self.handle_input)
        self.console_input.bind("<Up>", self.handle_history)
        self.console_input.bind("<Down>", self.handle_history)
        
        self.input_prompt_label.pack(side="left")
        
        self.lineending_selector.pack(side="right")
        self.console_input.pack(side="right", fill="x", expand=True)
        self.input_frame.pack(side="bottom", fill="x")

        # add config error commands to console
        if len(self.VARS._err_log) > 0:
            for error in self.VARS._err_log:
                self.console_log(error,"warning")
    def handle_history(self, event):
        # if no input reset history index
        if len(self.console_input.get()) <= 0:
            self.history_index = -1

        if event.keysym == "Up":
            self.history_index += 1
        elif event.keysym == "Down":
            self.history_index -= 1
        self.history_index = max(0, min(self.history_index, len(self.command_history)-1))
        #print(self.history_index, self.command_history)
        if len(self.command_history) > 0:
            self.console_input.delete(0, "end")
            self.console_input.insert(0, self.command_history[self.history_index])

    def handle_input(self, event):
        # get input
        input_text = self.console_input.get()
        # clear input
        self.console_input.delete(0, "end")
        self.console_log(f"> {input_text}")
        self.console_output.config(state="disabled")

        # call command callback
        if self.command_callback:
            self.command_callback(input_text)
        
        # add unique to history
        if len(self.command_history) > 0 and self.command_history[0] == input_text:
            return

        self.command_history.insert(0, input_text)
        if len(self.command_history) > self.VARS.console_history_size:
            self.command_history.pop(0)

    def get_line_ending(self):
        ending_setting = self.VARS.lineending.get()
        ending = ""
        if ending_setting == "CR":
            ending = "\r"
        elif ending_setting == "LF":
            ending = "\n"
        elif ending_setting == "CRLF":
            ending = "\r\n"
        return ending

    def console_log(self, text, type="normal"):
        colors = {
            "normal": "black",
            "error": "red",
            "warning": "orange",
            "success": "green"
        }
        #text = text.replace("\r", "¶").replace("\n", "¶¶").replace("\t", "→")
        text = text.strip() + "\n"

        # enable editing
        self.console_output.config(state="normal")

        # get current position in output
        end_index = self.console_output.index("end-1c")
        self.console_output.insert("end", text)
        start_index = f"{end_index}+{len(text)}c"
        # create tag
        self.console_output.tag_add(type, end_index, start_index)
        self.console_output.tag_config(type, foreground=(colors[type] if type in colors else "black"))
        
        # disable editing
        self.console_output.config(state="disabled")

    def on_command(self, command_callback: Callable[[str], None]):
        self.command_callback = command_callback