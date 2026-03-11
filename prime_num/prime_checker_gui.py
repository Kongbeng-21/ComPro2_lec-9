import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import requests

# Base URL for the FastAPI Backend (You must implement this!)
API_URL = "http://127.0.0.1:8000/primes/"
TIMEOUT_SECONDS = 30

class PrimeCheckerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Prime Checker API UI")
        self.root.geometry("800x600")
        self.root.configure(bg="white")
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background="white", fieldbackground="white", foreground="black", rowheight=25)
        style.configure("Treeview.Heading", background="#f4f4f4", foreground="black", font=('Arial', 10, 'bold'))
        style.configure("TProgressbar", background="#4CAF50", troughcolor="#e0e0e0")
        
        # State tracking
        self.is_running = False
        self.total_tasks = 0
        self.completed_tasks = 0
        self.start_time = 0
        
        self._build_ui()

    def _build_ui(self):
        # 1. Top Frame: Input Area
        top_frame = tk.Frame(self.root, bg="white")
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(top_frame, text="Enter Large Numbers (One per line):", bg="white", fg="black", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.input_text = scrolledtext.ScrolledText(top_frame, height=15, width=40, bg="white", fg="black", insertbackground="black")
        self.input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # Add some default very large numbers
        default_nums = "100\n1000\n2000\n3000\n10000\n50\n100\n1000\n2000\n3000\n10000\n50\n"
        self.input_text.insert(tk.END, default_nums)

        # Buttons
        btn_frame = tk.Frame(top_frame, bg="white")
        btn_frame.pack(side=tk.RIGHT, padx=10)
        
        style = ttk.Style()
        style.configure("White.TButton", background="white", foreground="black", font=("Arial", 12, "bold"))
        
        self.start_btn = ttk.Button(btn_frame, text="Start", command=self.start_processing, style="White.TButton")
        self.start_btn.pack(fill=tk.X, pady=2)
        
        self.cancel_btn = ttk.Button(btn_frame, text="Cancel", command=self.cancel_processing, state=tk.DISABLED, style="White.TButton")
        self.cancel_btn.pack(fill=tk.X, pady=2)

        # 2. Middle Frame: Progress & Timer
        mid_frame = tk.Frame(self.root, bg="white")
        mid_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(mid_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.pct_label = tk.Label(mid_frame, text="0%", width=5, bg="white", fg="black", font=("Arial", 10))
        self.pct_label.pack(side=tk.LEFT)
        
        self.time_label = tk.Label(mid_frame, text="Duration: 0.0s", font=("Arial", 10, "bold"), bg="white", fg="black")
        self.time_label.pack(side=tk.RIGHT)

        # 3. Bottom Frame: Results Table
        bot_frame = tk.Frame(self.root, bg="white")
        bot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("col_query", "col_total", "col_last", "col_next", "col_time")
        self.tree = ttk.Treeview(bot_frame, columns=columns, show="headings")
        
        self.tree.heading("col_query", text="Query Number")
        self.tree.heading("col_total", text="Total Primes Before")
        self.tree.heading("col_last", text="Last Prime Before")
        self.tree.heading("col_next", text="Next Prime After")
        self.tree.heading("col_time", text="Time Taken (s)")
        
        self.tree.column("col_query", width=120, anchor=tk.CENTER)
        self.tree.column("col_total", width=150, anchor=tk.CENTER)
        self.tree.column("col_last", width=150, anchor=tk.CENTER)
        self.tree.column("col_next", width=150, anchor=tk.CENTER)
        self.tree.column("col_time", width=100, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(bot_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def start_processing(self):
        # 1. Read input numbers
        raw_text = self.input_text.get("1.0", tk.END).strip()
        if not raw_text:
            return
            
        try:
            numbers = [int(n.strip()) for n in raw_text.split("\n") if n.strip()]
        except ValueError:
            tk.messagebox.showerror("Error", "Please enter valid integers only.")
            return

        # 2. Reset UI state
        self.tree.delete(*self.tree.get_children())
        self.is_running = True
        self.total_tasks = len(numbers)
        self.completed_tasks = 0
        self.start_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self.pct_label.config(text="0%")
        
        self.start_time = time.time()
        self.update_timer()

        # 3. Launch threads for each number concurrently
        for num in numbers:
            t = threading.Thread(target=self.fetch_prime_data, args=(num,))
            t.daemon = True
            t.start()

    def cancel_processing(self):
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)

    def update_timer(self):
        if self.is_running and self.completed_tasks < self.total_tasks:
            elapsed = time.time() - self.start_time
            self.time_label.config(text=f"Duration: {elapsed:.1f}s")
            self.root.after(100, self.update_timer) # Schedule next UI update

    def fetch_prime_data(self, number):
        try:
            # 1. Send the request to the FastAPI backend (allows exactly +1 sec for backend to cleanly timeout)
            response = requests.get(f"{API_URL}{number}", timeout=TIMEOUT_SECONDS + 1)
            
            if not self.is_running: 
                return # Abort if user clicked cancel during the delay
                
            if response.status_code == 200:
                data = response.json()
                
                # 2. Safely update the Tkinter UI from this background thread
                self.root.after(0, self.add_result_row, 
                                data["query_number"], 
                                data["primes_before"], 
                                data["last_prime_before"], 
                                data["next_prime_after"], 
                                data["time_taken"])
            else:
                self.root.after(0, self.add_error_row, number, "API Error")
                
        except requests.exceptions.RequestException:
             if self.is_running:
                 self.root.after(0, self.add_error_row, number, "Connection Failed")

    def add_result_row(self, query_num, total, last_p, next_p, t_taken):
        if not self.is_running: return
        self.tree.insert("", tk.END, values=(query_num, total, last_p, next_p, f"{t_taken}s"))
        self.increment_progress()

    def add_error_row(self, query_num, error_msg):
        if not self.is_running: return
        self.tree.insert("", tk.END, values=(query_num, "---", "---", "---", error_msg))
        self.increment_progress()

    def increment_progress(self):
        self.completed_tasks += 1
        pct = int((self.completed_tasks / self.total_tasks) * 100)
        self.progress_var.set(pct)
        self.pct_label.config(text=f"{pct}%")
        
        if self.completed_tasks >= self.total_tasks:
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.cancel_btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = PrimeCheckerGUI(root)
    root.mainloop()
