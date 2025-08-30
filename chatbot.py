import nltk
import tkinter as tk
from tkinter import scrolledtext, ttk
import random
import string
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class Chatbot:
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        
        # Define patterns and responses
        self.patterns = {
            'greeting': {
                'patterns': [
                    r'hello', r'hi', r'hey', r'howdy', r'hola',
                    r'good morning', r'good afternoon', r'good evening'
                ],
                'responses': [
                    "Hello! How can I help you today?",
                    "Hi there! What can I do for you?",
                    "Hey! How can I assist you?"
                ]
            },
            'goodbye': {
                'patterns': [
                    r'bye', r'goodbye', r'see you', r'farewell',
                    r'catch you later', r'have a good one'
                ],
                'responses': [
                    "Goodbye! Have a great day!",
                    "See you later!",
                    "Bye! Come back if you have more questions."
                ]
            },
            'thanks': {
                'patterns': [
                    r'thanks', r'thank you', r'appreciate it',
                    r'cheers', r'nice one'
                ],
                'responses': [
                    "You're welcome!",
                    "Happy to help!",
                    "Anytime!",
                    "My pleasure!"
                ]
            },
            'name': {
                'patterns': [
                    r'what is your name', r'who are you',
                    r'are you a bot', r'are you human'
                ],
                'responses': [
                    "I'm a chatbot created to assist you.",
                    "You can call me ChatBot. I'm here to help!",
                    "I'm an AI assistant. What can I do for you?"
                ]
            },
            'help': {
                'patterns': [
                    r'help', r'what can you do', r'how does this work',
                    r'what are my options'
                ],
                'responses': [
                    "I can answer questions, provide information, or just chat!",
                    "I'm here to help with any questions you might have.",
                    "You can ask me about various topics, or we can just have a conversation."
                ]
            },
            'weather': {
                'patterns': [
                    r'weather', r'forecast', r'raining', r'sunny',
                    r'temperature', r'how is the weather'
                ],
                'responses': [
                    "I don't have access to real-time weather data. You might want to check a weather app!",
                    "For weather information, I recommend checking a dedicated weather service.",
                    "I'm not connected to weather services, but I can help with other questions!"
                ]
            },
            'time': {
                'patterns': [
                    r'time', r'what time is it', r'current time',
                    r'what is the time'
                ],
                'responses': [
                    "I don't have access to the current time. Please check your device's clock.",
                    "For the current time, you might want to check your phone or computer clock."
                ]
            },
            'joke': {
                'patterns': [
                    r'tell me a joke', r'make me laugh', r'joke',
                    r'funny story', r'entertain me'
                ],
                'responses': [
                    "Why don't scientists trust atoms? Because they make up everything!",
                    "Why did the scarecrow win an award? Because he was outstanding in his field!",
                    "What do you call a fake noodle? An impasta!",
                    "Why couldn't the bicycle stand up by itself? It was two tired!"
                ]
            },
            'how_are_you': {
                'patterns': [
                    r'how are you', r'how do you feel', r'are you ok'
                ],
                'responses': [
                    "I'm functioning well, thank you for asking!",
                    "I'm just a program, but I'm operating as expected!",
                    "I don't have feelings, but I'm here to help you!"
                ]
            },
            'default': {
                'patterns': [],
                'responses': [
                    "I'm not sure I understand. Could you rephrase that?",
                    "That's interesting. Can you tell me more?",
                    "I'm still learning. Could you try asking differently?",
                    "I don't have a response for that. Maybe ask something else?"
                ]
            }
        }

    def preprocess_text(self, text):
        # Convert to lowercase
        text = text.lower()
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        # Tokenize
        tokens = word_tokenize(text)
        # Remove stopwords and stem
        tokens = [self.stemmer.stem(token) for token in tokens if token not in self.stop_words]
        return tokens

    def match_pattern(self, user_input):
        user_tokens = self.preprocess_text(user_input)
        
        best_match = None
        highest_score = 0
        
        for intent, data in self.patterns.items():
            if intent == 'default':
                continue
                
            for pattern in data['patterns']:
                # Simple pattern matching
                if re.search(pattern, user_input.lower()):
                    score = len(pattern.split())  # Longer patterns get higher scores
                    if score > highest_score:
                        highest_score = score
                        best_match = intent
        
        return best_match if best_match else 'default'

    def get_response(self, user_input):
        intent = self.match_pattern(user_input)
        return random.choice(self.patterns[intent]['responses'])


class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Rule-Based Chatbot")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        self.chatbot = Chatbot()
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🤖 Rule-Based Chatbot", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=60, height=20)
        self.chat_display.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        self.chat_display.config(state=tk.DISABLED)
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        self.user_input = ttk.Entry(input_frame, width=50)
        self.user_input.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.user_input.bind('<Return>', lambda event: self.send_message())
        
        send_button = ttk.Button(input_frame, text="Send", command=self.send_message)
        send_button.grid(row=0, column=1)
        
        # Configure input frame grid
        input_frame.columnconfigure(0, weight=1)
        
        # Add initial bot message
        self.add_message("Bot", "Hello! I'm a rule-based chatbot. How can I help you today?")
        
    def add_message(self, sender, message):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
    def send_message(self):
        user_text = self.user_input.get().strip()
        if user_text:
            self.add_message("You", user_text)
            self.user_input.delete(0, tk.END)
            
            # Get bot response
            response = self.chatbot.get_response(user_text)
            self.add_message("Bot", response)


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotGUI(root)
    root.mainloop()