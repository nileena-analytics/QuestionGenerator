# Automated QuestionGenerator
A simple Python application which generates meaningful questions from any given paragraph.
This project combines NLP models with a modern Tkinter GUI for interactive use.

# 🚀 Features

📖 Paragraph to Question Generation using a fine-tuned T5 Question Generator.

🎯 Semantic Deduplication with Sentence-BERT embeddings to avoid duplicate or similar questions.

✅ Filters vague/unhelpful questions.

🖥️ Modern GUI built using CustomTkinter.

⚡ Works entirely offline (CPU) once models are downloaded.


# 🛠️ Tech Stack

* Python 3.9+

* Hugging Face Transformers – for T5 question generation

* SentenceTransformers– for semantic similarity & deduplication

* Tkinter / CustomTkinter – frontend GUI


# ▶️ Usage

Run the app using the command :  $python main.py

Paste or type a paragraph in the input box.

Click Generate Questions.

See unique, filtered questions appear in the output box.
