"""ui"""
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from huffman import compress_file, decompress_file

def run_ui():
    """_summary_
    """
    root = tk.Tk()
    root.title("Huffman Compression/Decompression")
    root.geometry("400x250")

    selected_file = tk.StringVar(root)

    def choose_file():
        path = filedialog.askopenfilename()
        if path:
            selected_file.set(path)
            file_label.config(text=os.path.basename(path))

    def compress_action():
        filepath = selected_file.get()
        if filepath:
            try:
                out_path = compress_file(filepath)
                messagebox.showinfo("Success", f"File compressed as: {out_path}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showwarning("Warning", "Please select a file first.")

    def decompress_action():
        filepath = selected_file.get()
        if filepath:
            try:
                out_path = decompress_file(filepath)
                messagebox.showinfo("Success", f"File decompressed as: {out_path}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showwarning("Warning", "Please select a file first.")

    choose_btn = tk.Button(root, text="Choose File", command=choose_file, font=("Arial", 12))
    choose_btn.pack(pady=10)

    file_label = tk.Label(root, text="No file selected", font=("Arial", 14))
    file_label.pack(pady=10)

    compress_btn = tk.Button(root, text="Compress", command=compress_action, font=("Arial", 14))
    compress_btn.pack(pady=10)

    decompress_btn = tk.Button(root, text="Decompress", command=decompress_action, font=("Arial", 14))
    decompress_btn.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    run_ui()
