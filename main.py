import tkinter as tk
from dashboard import Dashboard
import matplotlib.pyplot as plt

def run_dashboard() -> None:
    root = tk.Tk()
    app = Dashboard(root)

    def on_close():
        plt.close("all")
        root.quit()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

if __name__ == "__main__":
    run_dashboard()