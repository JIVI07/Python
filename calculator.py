import tkinter as tk
from tkinter import messagebox
import os
from datetime import datetime

class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculator")
        self.root.geometry("300x400")
        self.root.resizable(False, False)
        
        self.history_file = "calculations.txt"
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w') as f:
                f.write("Calculation History:\n")
        
        self.expression = tk.StringVar()
        self.expression.set("")
        
        self.result = tk.StringVar()
        self.result.set("0")
        
        self.create_widgets()

        self.last_button_operator = False
        self.last_button_equals = False
    
    def create_widgets(self):
     
        display_frame = tk.Frame(self.root, height=100)
        display_frame.pack(expand=True, fill='both', padx=10, pady=10)
      
        expression_label = tk.Label(
            display_frame, 
            textvariable=self.expression, 
            anchor='e', 
            font=('Arial', 12),
            fg='gray'
        )
        expression_label.pack(expand=True, fill='both')
        
        result_label = tk.Label(
            display_frame, 
            textvariable=self.result, 
            anchor='e', 
            font=('Arial', 24, 'bold')
        )
        result_label.pack(expand=True, fill='both')
       
        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        buttons = [
            ['C', '⌫', '%', '/'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['0', '.', '=']
        ]
      
        for i, row in enumerate(buttons):
            for j, button_text in enumerate(row):
             
                if button_text == '=':
                    btn = tk.Button(
                        buttons_frame, 
                        text=button_text, 
                        font=('Arial', 14, 'bold'),
                        command=lambda x=button_text: self.on_button_click(x),
                        bg='#4CAF50',
                        fg='white'
                    )
                    btn.grid(row=i, column=j, columnspan=2, sticky='nsew', padx=2, pady=2)
                else:
                  
                    if button_text in ['/', '*', '-', '+', '%']:
                        bg_color = '#FF9800'
                        fg_color = 'white'
                    elif button_text in ['C', '⌫']:
                        bg_color = '#f44336'
                        fg_color = 'white'
                    else:
                        bg_color = '#e0e0e0'
                        fg_color = 'black'
                    
                    btn = tk.Button(
                        buttons_frame, 
                        text=button_text, 
                        font=('Arial', 14),
                        command=lambda x=button_text: self.on_button_click(x),
                        bg=bg_color,
                        fg=fg_color
                    )
                    
                    if button_text == '0':
                        btn.grid(row=i, column=j, columnspan=2, sticky='nsew', padx=2, pady=2)
                    else:
                        btn.grid(row=i, column=j, sticky='nsew', padx=2, pady=2)
       
        for i in range(5):
            buttons_frame.grid_rowconfigure(i, weight=1)
        for j in range(4):
            buttons_frame.grid_columnconfigure(j, weight=1)
    
    def on_button_click(self, button_text):
        current_result = self.result.get()
        current_expression = self.expression.get()
        
        if button_text == 'C':
            self.expression.set("")
            self.result.set("0")
            self.last_button_operator = False
            self.last_button_equals = False
            return
        
        if button_text == '⌫':
            if current_result != '0':
                if len(current_result) > 1:
                    self.result.set(current_result[:-1])
                else:
                    self.result.set("0")
            return
       
        if button_text == '=':
            try:
                full_expression = current_expression + current_result
              
                calculation_result = eval(full_expression)
             
                if isinstance(calculation_result, float):
                  
                    if calculation_result.is_integer():
                        calculation_result = int(calculation_result)
                    else:
                       
                        calculation_result = round(calculation_result, 8)
                
                self.save_calculation(full_expression, calculation_result)
                
                self.expression.set(full_expression + " =")
                self.result.set(str(calculation_result))
                self.last_button_equals = True
                
            except Exception as e:
                messagebox.showerror("Error", f"Invalid calculation: {e}")
                self.expression.set("")
                self.result.set("0")
            return
      
        if button_text in ['+', '-', '*', '/', '%']:
            if current_expression and not self.last_button_operator and not self.last_button_equals:
             
                self.expression.set(current_expression + current_result + button_text)
                self.result.set("0")
            elif not self.last_button_operator:
               
                self.expression.set(current_result + button_text)
                self.result.set("0")
            self.last_button_operator = True
            self.last_button_equals = False
            return
        
        if button_text in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']:
            if self.last_button_equals:
           
                self.expression.set("")
                self.result.set(button_text)
                self.last_button_equals = False
            else:
          
                if button_text == '.':
                    if '.' in current_result:
                        return  
                    if current_result == '0':
                        self.result.set('0' + button_text)
                        return
                
                if current_result == '0' and button_text != '.':
                    self.result.set(button_text)
                else:
                    self.result.set(current_result + button_text)
            
            self.last_button_operator = False
            return
    
    def save_calculation(self, expression, result):
        """Save the calculation to the history file with a timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.history_file, 'a') as f:
            f.write(f"{timestamp}: {expression} = {result}\n")

if __name__ == "__main__":
    root = tk.Tk()
    calculator = Calculator(root)
    root.mainloop()


    