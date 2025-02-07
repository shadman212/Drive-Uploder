import os
import mimetypes
import customtkinter
import tkinter as tk
from tkinter import filedialog, messagebox
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

# Set theme and appearance
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

# Initialize the main window
root = customtkinter.CTk()
root.title("GOOGLE DRIVE MANAGER")
root.geometry("1000x600")
root.minsize(1000, 700)
root.configure(bg="#0A0A0A")  # Dark background

# Global variables
mFile = None
file_list = {}
current_user = None  # Track the current user

# Google Drive authentication
SCOPES = ['https://www.googleapis.com/auth/drive']

# Define different PARENT_FOLDER_ID for each user
PARENT_FOLDER_IDS = {
    "USER 1": "1F2oxw2W4o1MAL0iQdVkzCc2Zjw4z5XoM",  # USER 1 folder ID
    "USER 2": "1eniCO53xi-ysqeOYmPjKWoX8F5q_9NAa",  # USER 2 folder ID
    "USER 3": "1ZyNqPeaOkZC2uVWDnlLKg6QuEF5JOMUA",  # USER 3 folder ID
}

def authenticate(user):
    """Authenticate and return Google Drive credentials based on the user."""
    if user == "USER 1":
        SERVICE_ACCOUNT_FILE = 'credentials.json'
    elif user == "USER 2":
        SERVICE_ACCOUNT_FILE = 'credentials_user2.json'
    elif user == "USER 3":
        SERVICE_ACCOUNT_FILE = 'credentials_user3.json'
    else:
        raise ValueError("Invalid user specified.")

    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds

def choose_file():
    """Open a file dialog and store the selected file."""
    global mFile
    mFile = filedialog.askopenfilename(title="Select a File")
    if mFile:
        file_label.configure(text=f"Selected: {os.path.basename(mFile)}")
    else:
        file_label.configure(text="No file selected")

def upload_file():
    """Upload the selected file to Google Drive."""
    global mFile, current_user
    if not mFile:
        messagebox.showerror("Error", "No file selected!")
        return

    try:
        creds = authenticate(current_user)
        service = build("drive", "v3", credentials=creds)

        file_name = os.path.basename(mFile)
        mime_type, _ = mimetypes.guess_type(mFile)
        mime_type = mime_type if mime_type else "application/octet-stream"

        file_metadata = {
            "name": file_name,
            "parents": [PARENT_FOLDER_IDS[current_user]]
        }

        media = MediaFileUpload(mFile, mimetype=mime_type)

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()

        file_id = file.get('id')
        file_list[file_name] = file_id  # Store file in dictionary
        list_files()  # Refresh UI with new file
        file_label.configure(text=f"Uploaded: {file_name}")
        messagebox.showinfo("Success", f"File uploaded successfully: {file_name}")
        mFile = None  # Reset the selected file after upload
    except Exception as e:
        print(f"Error during upload: {e}")  # Log the error for debugging
        messagebox.showerror("Upload Error", str(e))

def list_files():
    """Fetch all files from the Google Drive folders for all users and display them in a single list."""
    global current_user
    file_list.clear()
    file_listbox.delete(0, "end")  # Clear old list

    for user, PARENT_FOLDER_ID in PARENT_FOLDER_IDS.items():
        if not PARENT_FOLDER_ID:
            continue  # Skip if folder ID is not set for the user

        try:
            creds = authenticate(user)
            service = build("drive", "v3", credentials=creds)

            query = f"'{PARENT_FOLDER_ID}' in parents and trashed=false"
            results = service.files().list(q=query, fields="files(id, name)").execute()
            files = results.get('files', [])

            for file in files:
                file_list[file["name"]] = (file["id"], user)  # Store file ID and user
                # Format the file list with better structure
                file_listbox.insert("end", f"{file['name']:40}  [from {user}]")  # Add padding for readability
        except Exception as e:
            messagebox.showerror("List Files Error", str(e))


def download_file():
    """Download the selected file from Google Drive."""
    global current_user
    try:
        selected_index = file_listbox.curselection()

        if not selected_index:
            messagebox.showerror("Error", "Please select a file to download.")
            return

        selected_file = file_listbox.get(selected_index)
        file_name = selected_file.split(" -------->from ")[0]  # Extract the file name

        if file_name not in file_list:
            messagebox.showerror("Error", "File not found in list.")
            return

        file_id, user = file_list[file_name]
        save_path = filedialog.asksaveasfilename(defaultextension="", initialfile=file_name)

        if not save_path:
            return  # User canceled download

        creds = authenticate(user)
        service = build("drive", "v3", credentials=creds)

        request = service.files().get_media(fileId=file_id)
        with open(save_path, "wb") as file:
            file.write(request.execute())

        messagebox.showinfo("Success", f"File downloaded: {save_path}")

    except Exception as e:
        messagebox.showerror("Download Error", str(e))

def show_user_1_page():
    """Show the Google Drive Manager page for USER 1."""
    global current_user
    current_user = "USER 1"
    user_frame.pack_forget()  # Hide the user selection frame
    drive_frame.pack(pady=10, padx=10, fill="both", expand=True)  # Show the drive manager frame
    list_files()  # Refresh file list for the selected user

def show_user_2_page():
    """Show the Google Drive Manager page for USER 2."""
    global current_user
    current_user = "USER 2"
    user_frame.pack_forget()  # Hide the user selection frame
    drive_frame.pack(pady=10, padx=10, fill="both", expand=True)  # Show the drive manager frame
    list_files()  # Refresh file list for the selected user

def show_user_3_page():
    """Show the Google Drive Manager page for USER 3."""
    global current_user
    current_user = "USER 3"
    user_frame.pack_forget()  # Hide the user selection frame
    drive_frame.pack(pady=10, padx=10, fill="both", expand=True)  # Show the drive manager frame
    list_files()  # Refresh file list for the selected user

def show_user_selection():
    """Show the user selection page."""
    drive_frame.pack_forget()  # Hide the drive manager frame
    user_frame.pack(pady=10, padx=10, fill="both", expand=True)  # Show the user selection frame

# **User Selection Page**
user_frame = customtkinter.CTkFrame(root, fg_color="#222831", corner_radius=15)
user_frame.pack(pady=10, padx=10, fill="both", expand=True)

user_label = customtkinter.CTkLabel(user_frame, text="SELECT USER", font=("Courier New", 24), text_color="#EEEEEE")
user_label.pack(pady=20)

user1_btn = customtkinter.CTkButton(user_frame, text="USER 1", width=250, height=50, fg_color="#000c66", command=show_user_1_page)
user1_btn.pack(pady=10)

user2_btn = customtkinter.CTkButton(user_frame, text="USER 2", width=250, height=50, fg_color="#000c66", command=show_user_2_page)
user2_btn.pack(pady=10)

user3_btn = customtkinter.CTkButton(user_frame, text="USER 3", width=250, height=50, fg_color="#000c66", command=show_user_3_page)
user3_btn.pack(pady=10)

# **Google Drive Manager Page**
drive_frame = customtkinter.CTkFrame(root, fg_color="#222831", corner_radius=15)

choose_file_btn = customtkinter.CTkButton(drive_frame, text="🎮 Choose File", width=250, height=50, fg_color="#00ADB5", command=choose_file)
choose_file_btn.pack(pady=10)

file_label = customtkinter.CTkLabel(drive_frame, text="No file selected", font=("Courier New", 16), text_color="#EEEEEE")
file_label.pack(pady=5)

upload_btn = customtkinter.CTkButton(drive_frame, text="⬆ Upload to Drive", width=250, height=50, fg_color="#FF5722", command=upload_file)
upload_btn.pack(pady=10)

refresh_btn = customtkinter.CTkButton(drive_frame, text="🔄 Refresh File List", width=250, height=50, fg_color="#393E46", command=list_files)
refresh_btn.pack(pady=10)

file_listbox = tk.Listbox(drive_frame, width=70, height=10, bg="#0A0A0A", fg="#00ADB5", font=("Courier New", 14))
file_listbox.pack(pady=10)

download_btn = customtkinter.CTkButton(drive_frame, text="⬇ Download Selected File", width=250, height=50, fg_color="#FFC107", command=download_file)
download_btn.pack(pady=10)

back_btn = customtkinter.CTkButton(drive_frame, text="🔙 Back to User Selection", width=350, height=50, fg_color="#000c66", command=show_user_selection)
back_btn.pack(pady=10)

  # User 3 color (blue)

# Start with the user selection page
show_user_selection()

root.mainloop()
