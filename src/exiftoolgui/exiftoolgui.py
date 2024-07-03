import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import json

class ExifToolGUI:
    @staticmethod
    def check_exiftool():
        try:
            result = subprocess.run(['exiftool', '-ver'], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except FileNotFoundError:
            raise FileNotFoundError("ExifTool not found. Please install ExifTool and ensure it's in your system PATH.")
        except subprocess.CalledProcessError:
            raise RuntimeError("ExifTool is installed but not working properly.")

    def __init__(self, master=None, string_var_class=None):
        # Check for ExifTool before initializing GUI
        try:
            exiftool_version = self.check_exiftool()
            print(f"ExifTool version {exiftool_version} found.")
        except (FileNotFoundError, RuntimeError) as e:
            messagebox.showerror("ExifTool Error", str(e))
            raise

        self.master = master if master else tk.Tk()
        self.master.title("ExifTool GUI")
        self.master.geometry("900x600")
        self.StringVar = string_var_class if string_var_class else tk.StringVar

        self.create_widgets()
        self.current_file = None
        self.batch_directory = None

    def create_widgets(self):
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.master)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # View tab
        self.view_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.view_frame, text="View EXIF")
        self.create_view_tab()

        # Edit tab
        self.edit_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.edit_frame, text="Edit EXIF")
        self.create_edit_tab()

        # Remove tab
        self.remove_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.remove_frame, text="Remove EXIF")
        self.create_remove_tab()

        # Batch tab
        self.batch_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.batch_frame, text="Batch Process")
        self.create_batch_tab()

    def create_view_tab(self):
        self.view_frame.columnconfigure(0, weight=1)
        self.view_frame.rowconfigure(1, weight=1)

        ttk.Button(self.view_frame, text="Browse Image", command=self.browse_file).grid(
            row=0, column=0, pady=10
        )
        self.view_text = scrolledtext.ScrolledText(
            self.view_frame, wrap=tk.WORD, width=80, height=30
        )
        self.view_text.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    def create_edit_tab(self):
        self.edit_frame.columnconfigure(1, weight=1)

        ttk.Button(
            self.edit_frame, text="Select Image", command=self.select_image_for_edit
        ).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(self.edit_frame, text="Tag:").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        self.tag_entry = ttk.Entry(self.edit_frame)
        self.tag_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(self.edit_frame, text="Value:").grid(
            row=2, column=0, padx=5, pady=5, sticky="e"
        )
        self.value_entry = ttk.Entry(self.edit_frame)
        self.value_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(self.edit_frame, text="Apply Edit", command=self.apply_edit).grid(
            row=3, column=1, pady=10
        )

    def create_remove_tab(self):
        ttk.Button(
            self.remove_frame, text="Select Image", command=self.select_image_for_remove
        ).grid(row=0, column=0, pady=10)
        ttk.Button(
            self.remove_frame, text="Remove All EXIF Data", command=self.remove_all_exif
        ).grid(row=1, column=0, pady=10)

    def create_batch_tab(self):
        self.batch_frame.columnconfigure(0, weight=1)
        self.batch_frame.rowconfigure(4, weight=1)

        ttk.Button(
            self.batch_frame, text="Select Directory", command=self.select_directory
        ).grid(row=0, column=0, pady=10)
        self.batch_operation = tk.StringVar()
        ttk.Radiobutton(
            self.batch_frame,
            text="View EXIF",
            variable=self.batch_operation,
            value="view",
        ).grid(row=1, column=0)
        ttk.Radiobutton(
            self.batch_frame,
            text="Remove EXIF",
            variable=self.batch_operation,
            value="remove",
        ).grid(row=2, column=0)
        ttk.Button(self.batch_frame, text="Process", command=self.batch_process).grid(
            row=3, column=0, pady=10
        )
        self.batch_text = scrolledtext.ScrolledText(
            self.batch_frame, wrap=tk.WORD, width=80, height=20
        )
        self.batch_text.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")

    def run_exiftool(self, args):
        try:
            result = subprocess.run(
                ["exiftool"] + args, capture_output=True, text=True, check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error: {e.stderr}"
        except FileNotFoundError:
            return "Error: ExifTool not found. Please make sure it's installed and in your PATH."

    def pretty_print_json(self, text):
        lines = text.split("\n")
        pretty_lines = []
        for line in lines:
            if ":" in line:
                tag, value = line.split(":", 1)
                value = value.strip()
                try:
                    # Try to parse the value as JSON
                    json_data = json.loads(value)
                    # If successful, pretty print the JSON
                    pretty_json = json.dumps(json_data, indent=2)
                    pretty_lines.append(f"{tag}:\n{pretty_json}")
                except json.JSONDecodeError:
                    # If it's not valid JSON, keep the original line
                    pretty_lines.append(line)
            else:
                pretty_lines.append(line)
        return "\n".join(pretty_lines)

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff")]
        )
        if file_path:
            self.current_file = file_path
            exif_data = self.run_exiftool([file_path])
            pretty_exif_data = self.pretty_print_json(exif_data)
            self.view_text.delete(1.0, tk.END)
            self.view_text.insert(tk.END, pretty_exif_data)

    def select_image_for_edit(self):
        self.current_file = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff")]
        )

    def apply_edit(self):
        if not self.current_file:
            messagebox.showerror("Error", "No image selected")
            return
        tag = self.tag_entry.get()
        value = self.value_entry.get()
        if not tag or not value:
            messagebox.showerror("Error", "Both tag and value must be provided")
            return
        result = self.run_exiftool([f"-{tag}={value}", self.current_file])
        messagebox.showinfo("Result", result)

    def select_image_for_remove(self):
        self.current_file = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff")]
        )

    def remove_all_exif(self):
        if not self.current_file:
            messagebox.showerror("Error", "No image selected")
            return
        result = self.run_exiftool(["-all=", "-overwrite_original", self.current_file])
        messagebox.showinfo("Result", result)

    def select_directory(self):
        self.batch_directory = filedialog.askdirectory()

    def batch_process(self):
        if not self.batch_directory:
            messagebox.showerror("Error", "No directory selected")
            return

        operation = self.batch_operation.get()
        if operation == "view":
            result = self.run_exiftool(['-recurse', self.batch_directory])
            result = self.pretty_print_json(result)
        elif operation == "remove":
            result = self.run_exiftool(['-all=', '-overwrite_original', '-recurse', self.batch_directory])
        else:
            result = "Please select an operation"
        self.batch_text.delete(1.0, tk.END)
        self.batch_text.insert(tk.END, result)

    def create_batch_tab(self):
        self.batch_frame.columnconfigure(0, weight=1)
        self.batch_frame.rowconfigure(4, weight=1)

        ttk.Button(self.batch_frame, text="Select Directory", command=self.select_directory).grid(row=0, column=0, pady=10)
        self.batch_operation = self.StringVar()
        ttk.Radiobutton(self.batch_frame, text="View EXIF", variable=self.batch_operation, value="view").grid(row=1, column=0)
        ttk.Radiobutton(self.batch_frame, text="Remove EXIF", variable=self.batch_operation, value="remove").grid(row=2, column=0)
        ttk.Button(self.batch_frame, text="Process", command=self.batch_process).grid(row=3, column=0, pady=10)
        self.batch_text = scrolledtext.ScrolledText(self.batch_frame, wrap=tk.WORD, width=80, height=20)
        self.batch_text.grid(row=4, column=0, padx=10, pady=10, sticky='nsew')

    def run(self):
        self.master.mainloop()

    @classmethod
    def main(cls):
        try:
            root = tk.Tk()
            app = cls(root)
            app.run()
        except (FileNotFoundError, RuntimeError):
            sys.exit(1)
