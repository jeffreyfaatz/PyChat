import socket
import customtkinter
import threading

# TCP connection
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = "127.0.0.1"
PORT = 5005
client.connect((HOST, PORT))

# exit button class
class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("500x350")
        self.title("PyChat")
        
        self.label = customtkinter.CTkLabel(self, text="Do you want to exit?")
        self.label.pack(padx=20, pady=20)
        self.label.grid(row=0, column=0, columnspan=2, padx=20, pady=10)

        self.yes_button = customtkinter.CTkButton(self, text="Yes", command=self.exit_f)
        self.yes_button.grid(row=1, column=0, padx=20, pady=10)

        self.no_button = customtkinter.CTkButton(self, text="No", command=self.destroy)
        self.no_button.grid(row=1, column=1, padx=20, pady=10)

    def exit_f(self):
        self.destroy()
        exit()

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        # main configs
        self.users = None
        self.sent_message = None
        self.received_message = None
        self.name = None
        self.message_counter = 1
        self.chat_counter = 2
        self.resizable(width=False, height=False)
        self.title("PyChat Messaging App")
        self.geometry(f"{900}x{580}")
        
        # grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        
        # sidebar
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=1)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(0, weight=1)
        
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 0))

        self.clear_button = customtkinter.CTkButton(self.sidebar_frame, text="Clear Chat", command=self.clear_chat)
        self.clear_button.grid(row=1, column=0, padx=20, pady=(10, 20))
        
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Theme", anchor="n")
        self.appearance_mode_label.grid(row=2, column=0, padx=20, pady=(10, 0))
        
        self.current_appearance_mode = customtkinter.get_appearance_mode()
        self.appearance_mode_optionmenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionmenu.grid(row=3, column=0, padx=20, pady=(10, 20))
        self.appearance_mode_optionmenu.set(self.current_appearance_mode)

        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling", anchor="w")
        self.scaling_label.grid(row=4, column=0, padx=20, pady=(10, 0))
        
        self.current_scaling = "100%"
        self.scaling_optionmenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"], command=self.change_scaling_event)
        self.scaling_optionmenu.grid(row=5, column=0, padx=20, pady=(10, 20))
        self.scaling_optionmenu.set(self.current_scaling)
        
        self.exit_button = customtkinter.CTkButton(self.sidebar_frame, text="Exit", hover_color="Red", command=self.exit_app)
        self.exit_button.grid(row=6, column=0, padx=20, pady=(10, 20))
        
        # main entry
        # message tabs
        self.tabview = customtkinter.CTkTabview(self, width=600)
        self.tabview.grid(row=0, rowspan=3, column=1, columnspan=2, padx=20, pady=(10, 20), sticky="nsew")

        self.tabview.add("All")
        self.tabview.set("All")
        
        # message entry box
        self.entry = customtkinter.CTkEntry(self, placeholder_text="Enter message")
        self.entry.grid(row=3, column=1, padx=(20, 0), pady=(20, 20), sticky="nsew")
        
        # SEND button
        self.main_button = customtkinter.CTkButton(master=self, text="Send", command=self.send_message)
        self.main_button.grid(row=3, column=2, padx=(20, 20), pady=(20, 20))
        
        # set default values
        self.appearance_mode_optionmenu.set("Dark")
        self.scaling_optionmenu.set("100%")

        # name input box
        name_dialog = customtkinter.CTkInputDialog(text="What is your name:", title="PyChat")
        name = name_dialog.get_input()
        if name == "":
            exit()
        self.set_name(name=name)

        # threading
        recv_thread = threading.Thread(target=self.recv_message)
        recv_thread.daemon = True
        recv_thread.start()
        self.toplevel_window = None

    # exit button/window function
    def exit_app(self):
       if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
           self.toplevel_window = ToplevelWindow(self)
           self.toplevel_window.focus()
       else:
           self.toplevel_window.focus()

    # clear chat function
    def clear_chat(self):
        current_tab = self.tabview.get()
        for widget in self.tabview.tab(current_tab).grid_slaves():
            widget.grid_forget() 

    # set user name form pop up window function       
    def set_name(self, name):
        client.send(name.encode('utf-8'))
        self.name = name
        self.logo_label.configure(text=name)

    # send message to server function
    def send_message(self):
        message = self.entry.get()
        if len(message) > 0:
            self.entry.delete(0, len(message))
            self.sent_message = customtkinter.CTkLabel(self.tabview.tab(self.tabview.get()), text=message + "\n", width=840, font=customtkinter.CTkFont(size=14), text_color=("gray10", "#DCE4EE"), anchor="e")
            self.sent_message.grid(row=self.message_counter, column=1, columnspan=2, padx=(10, 10), sticky="nsew")
            self.message_counter = self.message_counter + 1
            detailed_message = self.tabview.get() + "--" + message
            client.send(detailed_message.encode('utf8'))

    # receive message from server function
    def recv_message(self):
        while True:
            server_message = client.recv(1024).decode('utf8')
            print(server_message)
            message_array = server_message.split("--")
            if len(message_array) > 2:
                if message_array[1] == "All":
                    self.received_message = customtkinter.CTkLabel(self.tabview.tab("All"),
                                                                   text=message_array[0] + ": " + message_array[2],
                                                                   width=840,
                                                                   font=customtkinter.CTkFont(size=14),
                                                                   text_color=("gray10", "#DCE4EE"),
                                                                   anchor="w")
                    self.received_message.grid(row=self.message_counter, column=1, columnspan=2, padx=(10, 10),
                                               sticky="nsew")
                    self.message_counter = self.message_counter + 1
                elif message_array[1] == self.name:
                    self.received_message = customtkinter.CTkLabel(self.tabview.tab(message_array[0]),
                                                                   text=message_array[2], width=840,
                                                                   font=customtkinter.CTkFont(size=14),
                                                                   text_color="red",
                                                                   anchor="w")
                    self.received_message.grid(row=self.message_counter, column=1, columnspan=2, padx=(10, 10),
                                               sticky="nsew")
                    self.message_counter = self.message_counter + 1
            if server_message.startswith("new_client-"):
                self.tabview.add(server_message.split("-")[1])
            elif server_message.startswith("exit_client-"):
                self.tabview.delete(server_message.split("-")[1])
            elif server_message.startswith("Other users:"):
                self.users = server_message.split(":")[1]
                for us in self.users.split(","):
                    if us != self.name:
                        self.tabview.add(us)
    
    # theme drop down menu
    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    # scaling drop down menu
    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)
        
if __name__ == "__main__":
    app = App()
    app.mainloop()