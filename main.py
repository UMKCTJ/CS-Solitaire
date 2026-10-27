
import tkinter as tk
from gui import SolitaireGUI

def main():
    root = tk.Tk()
    app = SolitaireGUI(root) 
    root.mainloop()

if __name__ == "__main__":
    main()