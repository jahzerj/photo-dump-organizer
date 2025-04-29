import os
import shutil
import re
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk

class PhotoOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Organizer")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Create GUI elements
        self.setup_ui()
        
        # Initialize variables
        self.is_processing = False
    
    def setup_ui(self):
        # Frame for folder selection
        folder_frame = ttk.Frame(self.root, padding="10")
        folder_frame.pack(fill=tk.X)
        
        # Folder path input
        ttk.Label(folder_frame, text="Folder Path:").pack(side=tk.LEFT, padx=(0, 5))
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(folder_frame, textvariable=self.path_var, width=50)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Browse button
        ttk.Button(folder_frame, text="Browse", command=self.browse_folder).pack(side=tk.RIGHT)
        
        # Progress frame
        progress_frame = ttk.Frame(self.root, padding="10")
        progress_frame.pack(fill=tk.X)
        
        # Progress bar
        ttk.Label(progress_frame, text="Progress:").pack(anchor=tk.W)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, length=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Status
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(progress_frame, textvariable=self.status_var).pack(anchor=tk.W)
        
        # Stats frame
        stats_frame = ttk.Frame(self.root, padding="10")
        stats_frame.pack(fill=tk.X)
        
        # Stats fields
        self.stats_frame = ttk.LabelFrame(stats_frame, text="Statistics")
        self.stats_frame.pack(fill=tk.X)
        
        self.moved_var = tk.StringVar(value="Files moved: 0")
        self.skipped_var = tk.StringVar(value="Files skipped: 0")
        self.folders_var = tk.StringVar(value="Folders created: 0")
        
        ttk.Label(self.stats_frame, textvariable=self.moved_var).pack(anchor=tk.W, pady=2)
        ttk.Label(self.stats_frame, textvariable=self.skipped_var).pack(anchor=tk.W, pady=2)
        ttk.Label(self.stats_frame, textvariable=self.folders_var).pack(anchor=tk.W, pady=2)
        
        # Log frame
        log_frame = ttk.Frame(self.root, padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(log_frame, text="Log:").pack(anchor=tk.W)
        self.log = scrolledtext.ScrolledText(log_frame, height=10)
        self.log.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill=tk.X)
        
        self.organize_button = ttk.Button(button_frame, text="Organize Photos", command=self.start_organizing)
        self.organize_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(side=tk.RIGHT, padx=5)
    
    def log_message(self, message):
        self.log.insert(tk.END, message + "\n")
        self.log.see(tk.END)  # Scroll to the end
    
    def browse_folder(self):
        # Use askopenfilename instead of askdirectory to show files
        # But we'll extract the directory from the selected file
        file_path = filedialog.askopenfilename(
            title="Select any file in the target directory",
            filetypes=[("All files", "*.*")]
        )
        if file_path:
            # Extract the directory path from the selected file
            folder_path = os.path.dirname(file_path)
            self.path_var.set(folder_path)
            self.log_message(f"Selected folder: {folder_path}")
    
    def start_organizing(self):
        if self.is_processing:
            return
            
        source_dir = self.path_var.get().strip()
        if not source_dir or not os.path.isdir(source_dir):
            self.log_message("Error: Please enter a valid directory path.")
            return
        
        # Reset UI
        self.progress_var.set(0)
        self.moved_var.set("Files moved: 0")
        self.skipped_var.set("Files skipped: 0")
        self.folders_var.set("Folders created: 0")
        self.log.delete(1.0, tk.END)
        
        # Start processing in a separate thread
        self.is_processing = True
        self.organize_button.config(state=tk.DISABLED)
        self.status_var.set("Processing...")
        
        threading.Thread(target=self.organize_photos, args=(source_dir,), daemon=True).start()
    
    def organize_photos(self, source_dir):
        try:
            # Pattern to match the date in filenames like PXL_20230507_060812369
            date_pattern = re.compile(r'PXL_(\d{4})(\d{2})\d{2}')
            
            # Dictionary to store folders already created
            created_folders = {}
            
            # Count for statistics
            moved_files = 0
            skipped_files = 0
            folders_created = 0
            
            # Get all files in the source directory
            all_files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]
            total_files = len(all_files)
            
            for i, filename in enumerate(all_files):
                file_path = os.path.join(source_dir, filename)
                
                # Update progress
                self.progress_var.set((i + 1) / total_files * 100)
                self.root.update_idletasks()
                
                # Try to match date pattern in filename
                match = date_pattern.search(filename)
                if match:
                    year = match.group(1)
                    month = match.group(2)
                    target_folder_name = f"{year}.{month}"
                    target_folder_path = os.path.join(source_dir, target_folder_name)
                    
                    # Create the target folder if it doesn't exist
                    if target_folder_name not in created_folders:
                        os.makedirs(target_folder_path, exist_ok=True)
                        created_folders[target_folder_name] = True
                        folders_created += 1
                        self.folders_var.set(f"Folders created: {folders_created}")
                        self.log_message(f"Created folder: {target_folder_name}")
                    
                    # Move the file to the target folder
                    target_file_path = os.path.join(target_folder_path, filename)
                    shutil.move(file_path, target_file_path)
                    moved_files += 1
                    self.moved_var.set(f"Files moved: {moved_files}")
                    self.log_message(f"Moved: {filename} -> {target_folder_name}/")
                else:
                    skipped_files += 1
                    self.skipped_var.set(f"Files skipped: {skipped_files}")
                    self.log_message(f"Skipped: {filename} (doesn't match pattern)")
            
            summary = f"\nSummary: Moved {moved_files} files, Skipped {skipped_files} files, Created {folders_created} folders"
            self.log_message(summary)
            self.status_var.set("Completed")
            
        except Exception as e:
            self.log_message(f"Error: {str(e)}")
            self.status_var.set("Error")
        
        finally:
            self.is_processing = False
            self.organize_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoOrganizerApp(root)
    root.mainloop()