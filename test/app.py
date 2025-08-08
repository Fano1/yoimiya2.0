# main_gui.py
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import asyncio
import threading

from ai import run_command_async

class AdminPanel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Admin Panel")
        self.geometry("700x500")
        self.configure(bg="#1e1e1e")

        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever, daemon=True).start()

        self.create_widgets()

    def create_widgets(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TLabel", foreground="white", background="#1e1e1e", font=("Segoe UI", 13))
        style.configure("TButton", font=("Segoe UI", 11), padding=6)
        style.configure("TCombobox", fieldbackground="white", background="white")

        # Title
        ttk.Label(self, text="AI Admin Panel Interface", font=("Segoe UI", 16, "bold")).pack(pady=10)

        # Model Selector Dropdown (can be used for different AI behaviors)
        self.model_var = tk.StringVar()
        self.model_dropdown = ttk.Combobox(self, textvariable=self.model_var, state="readonly", width=35)
        self.model_dropdown['values'] = [
            "General Admin Mode",
            "System Diagnostics",
            "Friendly Chat Mode",
            "Strict Admin Mode",
            "Joke Mode",
        ]
        self.model_dropdown.current(0)
        self.model_dropdown.pack(pady=5)

        # Custom Input Field
        self.input_field = tk.Entry(self, font=("Segoe UI", 12), width=60)
        self.input_field.pack(pady=10)
        self.input_field.bind("<Return>", lambda e: self.execute_command())

        # Send Button
        send_button = ttk.Button(self, text="Send Command", command=self.execute_command)
        send_button.pack(pady=5)

        # Output / Console
        self.console = tk.Text(self, height=15, bg="#2d2d2d", fg="lime", insertbackground='white', font=("Consolas", 10))
        self.console.pack(padx=10, pady=15, fill="both", expand=True)

    def execute_command(self):
        user_input = self.input_field.get().strip()
        mode = self.model_var.get()

        if not user_input:
            self.log("⚠️ Type something before sending.")
            return

        self.log(f"📤 [{mode}] {user_input}")
        asyncio.run_coroutine_threadsafe(self.run_async(user_input, mode), self.loop)
        self.input_field.delete(0, tk.END)

    async def run_async(self, user_input, mode):
        # Optionally customize input based on mode
        modified_input = self.format_input(user_input, mode)
        response = await run_command_async(modified_input)
        self.log(response)

    def format_input(self, msg, mode):
        # Let’s prep the prompt based on selected mode
        if mode == "System Diagnostics":
            return f"Run diagnostics and report status: {msg}"
        elif mode == "Friendly Chat Mode":
            return f"Talk casually and friendly: {msg}"
        elif mode == "Strict Admin Mode":
            return f"Respond formally like a strict system admin: {msg}"
        elif mode == "Joke Mode":
            return f"Make it funny: {msg}"
        return msg  # default

    def log(self, message):
        timestamp = datetime.now().strftime("[%H:%M:%S] ")
        self.console.insert(tk.END, f"{timestamp} {message}\n")
        self.console.see(tk.END)


if __name__ == "__main__":
    app = AdminPanel()
    app.mainloop()
