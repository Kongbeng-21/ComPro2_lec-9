import tkinter as tk
from tkinter import ttk
import requests
import re
import time


def fetch_title(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers, timeout=5)

    match = re.search(r"<title>(.*?)</title>", response.text, re.IGNORECASE)

    if match:
        return match.group(1).strip()

    return "No title found"


def log(msg):
    log_box.insert(tk.END, msg + "\n")
    log_box.see(tk.END)
    root.update()


def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    
    # Try to sort numerically if possible (for Duration)
    try:
        l.sort(key=lambda t: float(t[0].replace('s', '')), reverse=reverse)
    except ValueError:
        l.sort(reverse=reverse)

    # rearrange items in sorted positions
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    # reverse sort next time
    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))


def run_sequential():
    # Clear previous results
    for item in result_table.get_children():
        result_table.delete(item)
    log_box.delete("1.0", tk.END)

    urls = url_box.get("1.0", tk.END).strip().split("\n")

    start_time = time.time()
    log(f"Start time: {time.strftime('%H:%M:%S', time.localtime(start_time))}")

    for url in urls:
        url = url.strip()
        if not url:
            continue

        step_start = time.time()
        log(f"Fetching {url}")

        title = "ERROR"
        duration = 0.0
        try:
            title = fetch_title(url)
            log(f"   -> {title}")
        except Exception as e:
            title = f"Error: {str(e)}"
            log(f"   ERROR: {e}")

        step_end = time.time()
        duration = step_end - step_start
        log(f"Completed in {duration:.2f} seconds\n")
        
        result_table.insert("", tk.END, values=(url, title, f"{duration:.2f}s"))

    end_time = time.time()
    log("-------------------")
    log(f"Total time: {end_time - start_time:.2f} seconds")


# GUI
root = tk.Tk()
root.title("Web Title Fetcher (Sequential Version)")
root.geometry("800x900")
root.configure(bg="white")

style = ttk.Style()
style.theme_use('clam')
style.configure("Treeview", background="white", foreground="black", fieldbackground="white", rowheight=25)
style.configure("Treeview.Heading", background="#f0f0f0", foreground="black", relief="flat")
style.map("Treeview", background=[('selected', '#e1e1e1')], foreground=[('selected', 'black')])

# URL input
tk.Label(root, text="Enter URLs (one per line)", bg="white", font=("Arial", 10, "bold")).pack(pady=(10, 0))

url_box = tk.Text(root, height=12, bg="white", fg="black", insertbackground="black", relief="solid", borderwidth=1)
url_box.pack(fill="x", padx=20, pady=5)

url_box.insert(
    tk.END,
"""https://www.ku.ac.th
https://www.google.com
https://www.wikipedia.org
https://www.python.org
https://www.nasa.gov
https://www.apple.com
https://www.imdb.com
https://www.ted.com
https://www.github.com"""
)

# Start button
start_btn = tk.Button(root, text="Start Fetching", command=run_sequential, 
                      bg="white", fg="black", highlightbackground="white", 
                      font=("Arial", 10, "bold"), padx=20)
start_btn.pack(pady=10)

# Log output
tk.Label(root, text="Processing Log", bg="white", font=("Arial", 10, "bold")).pack()
log_box = tk.Text(root, height=8, bg="white", fg="#444", insertbackground="black", relief="solid", borderwidth=1)
log_box.pack(fill="x", padx=20, pady=5)

# Results Table
tk.Label(root, text="Results Table (Click headers to sort)", bg="white", font=("Arial", 10, "bold")).pack(pady=(10, 0))

columns = ("URL", "Title", "Duration")
result_table = ttk.Treeview(root, columns=columns, show="headings", height=10)

# Define headings and sorting
for col in columns:
    result_table.heading(col, text=col, command=lambda c=col: treeview_sort_column(result_table, c, False))
    if col == "URL":
        result_table.column(col, width=250)
    elif col == "Title":
        result_table.column(col, width=350)
    else:
        result_table.column(col, width=100, anchor="center")

result_table.pack(fill="both", expand=True, padx=20, pady=(5, 20))

root.mainloop()