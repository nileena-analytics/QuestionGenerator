##Importing required libraries
import customtkinter as ctk
from tkinter import filedialog, messagebox
from backend.nlp_engine import generate_questions

#GUI for the application
class QuestionGeneratorGUI:
    def __init__(self):
        #Appearance and Theme
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        #App window
        self.root = ctk.CTk()
        self.root.title("✨ Automated Question Generator ✨")
        self.root.geometry("800x600")

        #Title label
        self.title_label = ctk.CTkLabel(self.root, text="Automated Question Generator",
                                        font=("Arial Rounded MT Bold", 22))
        self.title_label.pack(pady=20)

        #Input field
        self.input_frame = ctk.CTkFrame(self.root, corner_radius=15)
        self.input_frame.pack(padx=20, pady=10, fill="x")

        self.input_label = ctk.CTkLabel(self.input_frame, text="Enter a paragraph:", font=("Arial", 14))
        self.input_label.pack(anchor="w", padx=10, pady=5)

        self.input_text = ctk.CTkTextbox(self.input_frame, height=150, font=("Arial", 12))
        self.input_text.pack(padx=10, pady=5, fill="x")

        #Generate Button
        self.generate_button = ctk.CTkButton(self.root, text="⚡ Generate Questions",
                                             command=self.on_generate_click, width=200, height=40)
        self.generate_button.pack(pady=10)

        # Output section
        self.output_frame = ctk.CTkFrame(self.root, corner_radius=15)
        self.output_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.output_label = ctk.CTkLabel(self.output_frame, text="Generated Questions:", font=("Arial", 14))
        self.output_label.pack(anchor="w", padx=10, pady=5)

        self.output_box = ctk.CTkTextbox(self.output_frame, height=200, font=("Arial", 12))
        self.output_box.pack(padx=10, pady=5, fill="both", expand=True)

        #Starting the event loop to keep the window running
        self.root.mainloop()

#funcction to generate the questions
    def on_generate_click(self):
        #Getting text from input and removing trailing newline or spaces
        paragraph = self.input_text.get("1.0", "end-1c").strip()
         #Clearing output box
        self.output_box.delete("1.0", "end")

        #Handling empty output with message
        if not paragraph:
            self.output_box.insert("end", "Please enter a Input.\n")
            return

        #Calling backend NLP engine to generate questions
        questions = generate_questions(paragraph)

        if not questions:
            self.output_box.insert("end", "No valid questions generated.\n")
        else:
            for i, q in enumerate(questions, 1):
                self.output_box.insert("end", f"{i}. {q}\n\n")

    #Function to clear both input and output
    def clear_texts(self):
        self.input_text.delete("1.0", "end")
        self.output_box.delete("1.0", "end")

#Entry point to start the app
if __name__ == "__main__":
    QuestionGeneratorGUI()
