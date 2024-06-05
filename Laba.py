import tkinter as tk
from tkinter import filedialog, Text, messagebox
import re
from collections import Counter
import os
import pymorphy2
from datetime import datetime


# Singleton Pattern for Logger
class Logger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Logger, cls).__new__(cls, *args, **kwargs)
            cls._instance._init_log_file()
        return cls._instance

    def _init_log_file(self):
        self.log_file = os.path.join(os.path.dirname(__file__), 'log.txt')
        with open(self.log_file, 'w') as f:
            f.write("Log File Initialized\n")

    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, 'a') as f:
            f.write(f"{timestamp} - {message}\n")


logger = Logger()


# Strategy Pattern for text analysis
class TextAnalysisStrategy:
    def analyze(self, text):
        pass


class AbsoluteFrequencyStrategy(TextAnalysisStrategy):
    def analyze(self, text):
        words = re.findall(r'\b\w+\b', text.lower())
        freq = Counter(words)
        return freq


class RelativeFrequencyStrategy(TextAnalysisStrategy):
    def analyze(self, text):
        words = re.findall(r'\b\w+\b', text.lower())
        total_words = len(words)
        freq = Counter(words)
        rel_freq = {word: (count / total_words) * 100 for word, count in freq.items()}
        return rel_freq


class SentenceCountStrategy(TextAnalysisStrategy):
    def analyze(self, text):
        sentences = re.split(r'[.!?]', text)
        return len([s for s in sentences if s.strip()])


class InflectionHighlightStrategy(TextAnalysisStrategy):
    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()

    def analyze(self, text, selected_words):
        inflections = {}
        words = re.findall(r'\b\w+\b', text.lower())
        for word in selected_words:
            lemma = self.morph.parse(word)[0].normal_form
            inflections[lemma] = []
            for w in words:
                if self.morph.parse(w)[0].normal_form == lemma:
                    inflection = w[len(lemma):]
                    inflections[lemma].append(inflection)
        return inflections


class UniqueWordsCountStrategy(TextAnalysisStrategy):
    def analyze(self, text):
        words = re.findall(r'\b\w+\b', text.lower())
        unique_words = set(words)
        return len(unique_words)


class TextAnalyzer:
    def __init__(self, strategy):
        self._strategy = strategy

    def set_strategy(self, strategy):
        self._strategy = strategy

    def analyze(self, text, *args):
        return self._strategy.analyze(text, *args)


# GUI Application
class TextAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text Analysis App")

        self.text_area = Text(root, wrap='word')
        self.text_area.pack(expand=1, fill='both')

        self.menu = tk.Menu(root)
        root.config(menu=self.menu)

        file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)

        analyze_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Analyze", menu=analyze_menu)
        analyze_menu.add_command(label="Absolute Frequency", command=self.show_absolute_frequency)
        analyze_menu.add_command(label="Relative Frequency", command=self.show_relative_frequency)
        analyze_menu.add_command(label="Sentence Count", command=self.show_sentence_count)
        analyze_menu.add_command(label="Highlight Inflections", command=self.show_inflections)
        analyze_menu.add_command(label="Unique Words Count", command=self.show_unique_words_count)

        self.file_path = None

    def open_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if self.file_path:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, text)
                logger.log(f"Opened file: {self.file_path}")

    def save_file(self):
        if self.file_path:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                text = self.text_area.get(1.0, tk.END)
                file.write(text)
                logger.log(f"Saved file: {self.file_path}")
        else:
            messagebox.showerror("Error", "No file is open.")

    def show_absolute_frequency(self):
        text = self.text_area.get(1.0, tk.END)
        analyzer = TextAnalyzer(AbsoluteFrequencyStrategy())
        result = analyzer.analyze(text)
        logger.log(f"Absolute Frequency Result: {result}")
        messagebox.showinfo("Absolute Frequency", str(result))

    def show_relative_frequency(self):
        text = self.text_area.get(1.0, tk.END)
        analyzer = TextAnalyzer(RelativeFrequencyStrategy())
        result = analyzer.analyze(text)
        logger.log(f"Relative Frequency Result: {result}")
        messagebox.showinfo("Relative Frequency", str(result))

    def show_sentence_count(self):
        text = self.text_area.get(1.0, tk.END)
        analyzer = TextAnalyzer(SentenceCountStrategy())
        result = analyzer.analyze(text)
        logger.log(f"Sentence Count Result: {result}")
        messagebox.showinfo("Sentence Count", str(result))

    def show_inflections(self):
        try:
            selected_text = self.text_area.selection_get()
            selected_words = re.findall(r'\b\w+\b', selected_text.lower())
            text = self.text_area.get(1.0, tk.END)
            analyzer = TextAnalyzer(InflectionHighlightStrategy())
            result = analyzer.analyze(text, selected_words)
            logger.log(f"Inflections Result for {selected_words}: {result}")
            messagebox.showinfo("Inflections", str(result))
        except tk.TclError:
            messagebox.showerror("Error", "No text selected.")

    def show_unique_words_count(self):
        text = self.text_area.get(1.0, tk.END)
        analyzer = TextAnalyzer(UniqueWordsCountStrategy())
        result = analyzer.analyze(text)
        logger.log(f"Unique Words Count Result: {result}")
        messagebox.showinfo("Unique Words Count", str(result))


if __name__ == "__main__":
    root = tk.Tk()
