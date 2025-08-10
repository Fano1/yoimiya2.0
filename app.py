import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import asyncio
import threading
import psutil
import platform
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import os

# Dummy async AI backend functions
from protocol.models.geminiOllama import run_gemini_async
from protocol.models.cai import run_cai_async

async def dummy_image_gen(model_name: str, prompt: str) -> str:
    await asyncio.sleep(1)
    return f"[ImageGen-Dummy]: Generated image using '{model_name}' with prompt: '{prompt}'"

async def dummy_audio_gen(model_name: str, prompt: str) -> str:
    await asyncio.sleep(1)
    return f"[AudioGen-Dummy]: Generated audio using '{model_name}' with prompt: '{prompt}'"

async def dummy_video_gen(model_name: str, prompt: str) -> str:
    await asyncio.sleep(1)
    return f"[VideoGen-Dummy]: Generated video using '{model_name}' with prompt: '{prompt}'"

async def dummy_file_process(file_content: str) -> str:
    await asyncio.sleep(1)
    length = len(file_content)
    return f"[FileProc-Dummy]: Processed file content of length {length} successfully."

class AdminPanel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Admin Panel - Pro Edition")
        self.configure(bg="#121212")

        # Fullscreen & responsive layout
        self.state('zoomed')
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Async loop in background thread
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever, daemon=True).start()

        self.cpu_data, self.ram_data, self.gpu_data = [], [], []
        self.graph_visible = False
        self.uploaded_file_content = None
        self.modeltube_on = False

        self.create_styles()
        self.create_widgets()

        self.after(1000, self.update_system_stats)
        threading.Thread(target=self.terminal_input_listener, daemon=True).start()

    def create_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TLabel", foreground="white", background="#121212", font=("Segoe UI", 16))
        style.configure("TButton", font=("Segoe UI", 16), padding=10)
        
        # Regular combobox style (medium size)
        style.configure("TCombobox",
                        fieldbackground="#2c2c2c",
                        background="#2c2c2c",
                        foreground="white",
                        font=("Segoe UI", 16, "bold"))
        style.map('TCombobox', fieldbackground=[('readonly', '#2c2c2c')])

        # BIG combobox style for extra tall/wide dropdowns
        style.configure("Big.TCombobox",
                        fieldbackground="#2c2c2c",
                        background="#2c2c2c",
                        foreground="white",
                        font=("Segoe UI", 24, "bold"),
                        padding=10)
        style.map('Big.TCombobox', fieldbackground=[('readonly', '#2c2c2c')])

        style.configure("On.TButton", foreground="lime", font=("Segoe UI", 16, "bold"))

    def create_widgets(self):
        ttk.Label(self, text="AI Admin Panel", font=("Segoe UI", 28, "bold"), background="#121212").grid(row=0, column=0, pady=20)

        control_frame = tk.Frame(self, bg="#121212")
        control_frame.grid(row=1, column=0, sticky="nsew", padx=30)
        control_frame.grid_columnconfigure(3, weight=1)

        # Model Dropdown - BIG and WIDE
        ttk.Label(control_frame, text="Select AI Model:").grid(row=0, column=0, sticky="w", pady=10)
        self.model_var = tk.StringVar()
        self.model_dropdown = ttk.Combobox(control_frame, 
                                           textvariable=self.model_var, 
                                           state="readonly", 
                                           width=40,     # approx 40 characters wide
                                           style="Big.TCombobox")  # Use big style
        self.model_dropdown['values'] = ["Gemini Model", "Character.AI Model"]
        self.model_dropdown.current(0)
        self.model_dropdown.grid(row=1, column=0, padx=(0, 30), sticky="w")
        self.model_dropdown.config(height=10)  # Show 10 items in dropdown list

        # Generation Type Dropdown - Also BIG and WIDE
        ttk.Label(control_frame, text="Generation Type:").grid(row=0, column=1, sticky="w", pady=10)
        self.gen_type_var = tk.StringVar()
        self.gen_type_dropdown = ttk.Combobox(control_frame,
                                              textvariable=self.gen_type_var,
                                              state="readonly",
                                              width=40,   # same wide width
                                              style="Big.TCombobox")  # Use big style
        self.gen_type_dropdown['values'] = [
            "None", "Image Generation (Dummy)", "Audio Generation (Dummy)",
            "Video Generation (Dummy)", "File Upload (Dummy)"
        ]
        self.gen_type_dropdown.current(0)
        self.gen_type_dropdown.grid(row=1, column=1, sticky="w")
        self.gen_type_dropdown.config(height=10)  # Show 10 items in dropdown list
        self.gen_type_dropdown.bind("<<ComboboxSelected>>", self.on_gen_type_change)

        # File upload button (hidden by default)
        self.file_upload_btn = ttk.Button(control_frame, text="Upload File", command=self.upload_file)
        self.file_upload_btn.grid(row=1, column=2, padx=15)
        self.file_upload_btn.grid_remove()

        # ModelTube toggle button
        self.modeltube_btn = ttk.Button(control_frame, text="ModelTube OFF", command=self.toggle_modeltube, width=15)
        self.modeltube_btn.grid(row=1, column=3, sticky="e")

        # Input field for commands/prompts - your actual input, not the console widget!
        self.input_field = tk.Entry(self, font=("Segoe UI", 18), bg="#282828", fg="white", insertbackground='white')
        self.input_field.grid(row=2, column=0, padx=30, pady=20, sticky="ew")
        self.input_field.bind("<Return>", lambda e: self.execute_command())

        btn_frame = tk.Frame(self, bg="#121212")
        btn_frame.grid(row=3, column=0, pady=10, padx=30, sticky="ew")
        btn_frame.grid_columnconfigure(2, weight=1)

        send_btn = ttk.Button(btn_frame, text="Send Command", command=self.execute_command)
        send_btn.grid(row=0, column=0, padx=10)

        status_btn = ttk.Button(btn_frame, text="Show Laptop Status", command=self.show_system_status)
        status_btn.grid(row=0, column=1, padx=10)

        graph_btn = ttk.Button(btn_frame, text="Toggle System Graph", command=self.toggle_graph)
        graph_btn.grid(row=0, column=2, padx=10, sticky="e")

        # Console output area (read-only)
        self.console = tk.Text(self, height=20, bg="#181818", fg="#7CFC00", insertbackground='white', font=("Consolas", 14))
        self.console.grid(row=4, column=0, padx=30, pady=20, sticky="nsew")
        self.console.configure(state=tk.DISABLED)

        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.graph_frame = tk.Frame(self, bg="#121212")
        self.graph_frame.grid(row=5, column=0, sticky="nsew", padx=30, pady=10)
        self.graph_frame.grid_remove()

        self.fig, self.ax = plt.subplots(figsize=(14, 4), dpi=100)
        self.ax.set_facecolor("#121212")
        self.ax.tick_params(colors="white")
        for spine in self.ax.spines.values():
            spine.set_color('white')
        self.ax.set_ylim(0, 100)
        self.ax.set_title("System Usage (%)", color="white", fontsize=18)
        self.ax.set_xlabel("Time (seconds ago)", color="white", fontsize=14)
        self.ax.set_ylabel("Usage %", color="white", fontsize=14)

        self.cpu_line, = self.ax.plot([], [], color="cyan", linewidth=3, label="CPU")
        self.ram_line, = self.ax.plot([], [], color="magenta", linewidth=3, label="RAM")
        self.gpu_line, = self.ax.plot([], [], color="yellow", linewidth=3, label="GPU")

        self.ax.legend(loc="upper right", facecolor="#121212", labelcolor="white")

        self.fig.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.generation_handlers = {
            "None": self.handle_none_generation,
            "Image Generation (Dummy)": self.handle_image_generation,
            "Audio Generation (Dummy)": self.handle_audio_generation,
            "Video Generation (Dummy)": self.handle_video_generation,
            "File Upload (Dummy)": self.handle_file_upload_generation,
        }

        self.ai_models = {
            "Gemini Model": run_gemini_async,
            "Character.AI Model": run_cai_async,
        }

    def on_gen_type_change(self, event=None):
        if self.gen_type_var.get() == "File Upload (Dummy)":
            self.file_upload_btn.grid()
        else:
            self.file_upload_btn.grid_remove()
            self.uploaded_file_content = None

    def upload_file(self):
        file_path = filedialog.askopenfilename(title="Select a file")
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.uploaded_file_content = f.read()
                self.log(f"File uploaded and read: {os.path.basename(file_path)} (size: {len(self.uploaded_file_content)} chars)")
            except Exception as e:
                self.log(f"Error reading file: {str(e)}")
                self.uploaded_file_content = None

    def execute_command(self):
        user_input = self.input_field.get().strip()
        model_choice = self.model_var.get()
        gen_type = self.gen_type_var.get()

        if not user_input and gen_type != "File Upload (Dummy)":
            self.log("Type something before sending.")
            return

        if user_input.startswith("/"):
            self.handle_simple_command(user_input)
            self.input_field.delete(0, tk.END)
            return

        self.log(f"[{model_choice} | {gen_type}] Input: {user_input}")

        handler = self.generation_handlers.get(gen_type, self.handle_none_generation)
        asyncio.run_coroutine_threadsafe(handler(model_choice, user_input), self.loop)
        self.input_field.delete(0, tk.END)

    async def handle_none_generation(self, model_name, prompt):
        ai_func = self.ai_models.get(model_name)
        if not ai_func:
            self.log("Unknown AI model selected.")
            return
        try:
            response = await ai_func(prompt)
        except Exception as e:
            response = f"AI error: {str(e)}"
        self.log(response)

    async def handle_image_generation(self, model_name, prompt):
        response = await dummy_image_gen(model_name, prompt)
        self.log(response)

    async def handle_audio_generation(self, model_name, prompt):
        response = await dummy_audio_gen(model_name, prompt)
        self.log(response)

    async def handle_video_generation(self, model_name, prompt):
        response = await dummy_video_gen(model_name, prompt)
        self.log(response)

    async def handle_file_upload_generation(self, model_name, prompt):
        if not self.uploaded_file_content:
            self.log("No file uploaded. Please upload a file first.")
            return
        response = await dummy_file_process(self.uploaded_file_content)
        self.log(response)

    def handle_simple_command(self, command):
        command = command.lower().strip()
        if command == "/clear":
            self.console.configure(state=tk.NORMAL)
            self.console.delete("1.0", tk.END)
            self.console.configure(state=tk.DISABLED)
        elif command == "/help":
            self.log("Commands available: /clear, /help, /status, /togglegraph, /modeltube")
        elif command == "/status":
            self.show_system_status()
        elif command == "/togglegraph":
            self.toggle_graph()
        elif command == "/modeltube":
            self.toggle_modeltube()
        else:
            self.log(f"Unknown command: {command}")

    def log(self, message):
        timestamp = datetime.now().strftime("[%H:%M:%S] ")
        full_msg = f"{timestamp}{message}\n"
        self.console.configure(state=tk.NORMAL)
        self.console.insert(tk.END, full_msg)
        self.console.see(tk.END)
        self.console.configure(state=tk.DISABLED)
        print(full_msg, end='')  # Also print to terminal

    def update_system_stats(self):
        cpu_percent = psutil.cpu_percent()
        ram_percent = psutil.virtual_memory().percent
        gpu_percent = self.get_gpu_usage_percent()

        self.cpu_data.append(cpu_percent)
        self.ram_data.append(ram_percent)
        self.gpu_data.append(gpu_percent)

        max_len = 30
        if len(self.cpu_data) > max_len:
            self.cpu_data.pop(0)
            self.ram_data.pop(0)
            self.gpu_data.pop(0)

        if self.graph_visible:
            self.cpu_line.set_data(range(len(self.cpu_data)), self.cpu_data)
            self.ram_line.set_data(range(len(self.ram_data)), self.ram_data)
            self.gpu_line.set_data(range(len(self.gpu_data)), self.gpu_data)
            self.ax.set_xlim(0, max_len)
            self.ax.set_ylim(0, 100)
            self.canvas.draw_idle()

        self.after(1000, self.update_system_stats)

    def get_gpu_usage_percent(self):
        # Dummy GPU usage for now
        return random.randint(0, 100)

    def show_system_status(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        os_info = platform.system() + " " + platform.release()
        status_message = (f"System Status:\n"
                          f"CPU Usage: {cpu}%\n"
                          f"RAM Usage: {ram}%\n"
                          f"Disk Usage: {disk}%\n"
                          f"OS: {os_info}")
        self.log(status_message)

    def toggle_graph(self):
        self.graph_visible = not self.graph_visible
        if self.graph_visible:
            self.graph_frame.grid()
        else:
            self.graph_frame.grid_remove()

    def toggle_modeltube(self):
        self.modeltube_on = not self.modeltube_on
        if self.modeltube_on:
            self.modeltube_btn.configure(text="ModelTube ON", style="On.TButton")
            self.log("ModelTube mode enabled. (No f*cks given mode)")
        else:
            self.modeltube_btn.configure(text="ModelTube OFF", style="TButton")
            self.log("ModelTube mode disabled. (Back to boring admin life)")

    def terminal_input_listener(self):
        # Listens for terminal input from the actual console where the app is launched.
        while True:
            try:
                cmd = input()
                if cmd.strip():
                    self.log(f"[Terminal] Executing command: {cmd.strip()}")
                    if cmd.startswith("/"):
                        self.handle_simple_command(cmd)
                    else:
                        asyncio.run_coroutine_threadsafe(
                            self.generation_handlers.get(self.gen_type_var.get(), self.handle_none_generation)(
                                self.model_var.get(), cmd.strip()), self.loop)
            except Exception as e:
                self.log(f"Terminal input listener error: {e}")

def runAdminPanel():
    app = AdminPanel()
    app.mainloop()
