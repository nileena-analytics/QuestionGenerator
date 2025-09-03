#Importing required libraries
import tkinter as tk
from frontend.gui import QuestionGeneratorGUI

"""
This is the main entry point for the app.
Creating a Tkinter root window and initializing QuestionGeneratorGUI class 
which builds the full interface. The root.mainloop() call will starts the GUI, 
which keeps the application running until the user closes it.
"""

if __name__ == "__main__":
    root = tk.Tk()
    app = QuestionGeneratorGUI()
    root.mainloop()
