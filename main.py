import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from PIL import Image
import numpy as np
import threading


# Constants
DELIMITER = '1111111111111110'  # Unique delimiter to mark the end of the message




# Function to convert message to binary
def message_to_binary(message):
   return ''.join(format(ord(char), '08b') for char in message) + DELIMITER




# Function to convert binary to message
def binary_to_message(binary_data):
   bytes_data = [binary_data[i:i + 8] for i in range(0, len(binary_data), 8)]
   return ''.join(chr(int(byte, 2)) for byte in bytes_data)




# Function to check if the image size is sufficient
def is_image_sufficient(image_size, message_length):
   return message_length <= image_size[0] * image_size[1] * 3




# Function to update progress
def update_progress(progress_bar, value):
   progress_bar['value'] = value
   progress_bar.update_idletasks()




# Function to encode a message into an image using numpy for faster processing
def encode_message(image_path, message, save_path, progress_bar):
   try:
       # Load and convert image
       image = Image.open(image_path).convert("RGB")
       binary_message = message_to_binary(message)


       # Convert image to numpy array
       image_array = np.array(image)


       # Check if the image can hold the message
       if not is_image_sufficient(image_array.shape, len(binary_message)):
           messagebox.showwarning("Error", "The selected image is too small to hold the message.")
           return


       # Flatten the image array for easier manipulation
       flat_image_array = image_array.flatten()


       # Encode the message into the image
       for index, bit in enumerate(binary_message):
           flat_image_array[index] = (flat_image_array[index] & ~1) | int(bit)


           # Update progress
           update_progress(progress_bar, index * 100 / len(binary_message))


       # Reshape the flat array back to the original image shape
       encoded_image_array = flat_image_array.reshape(image_array.shape)


       # Convert numpy array back to image
       encoded_image = Image.fromarray(encoded_image_array.astype('uint8'))


       # Save the encoded image
       encoded_image.save(save_path)
       messagebox.showinfo("Success", f"Message encoded successfully and saved as {save_path}")


   except Exception as e:
       messagebox.showerror("Error", f"Failed to encode message: {str(e)}")
   finally:
       progress_bar['value'] = 0




# Function to decode a message from an image using numpy for faster processing
def decode_message(image_path, progress_bar):
   try:
       # Load and convert image
       image = Image.open(image_path).convert("RGB")


       # Convert image to numpy array
       image_array = np.array(image)


       # Flatten the image array
       flat_image_array = image_array.flatten()


       binary_message = ""


       # Extract the binary message from image pixels
       for index, value in enumerate(flat_image_array):
           binary_message += str(value & 1)


           # Update progress
           update_progress(progress_bar, index * 100 / len(flat_image_array))


           # Check if the delimiter is found
           if binary_message[-16:] == DELIMITER:
               binary_message = binary_message[:-16]
               message = binary_to_message(binary_message)
               messagebox.showinfo("Decoded Message", f"Message: {message}")
               return


       messagebox.showinfo("Result", "No hidden message found!")


   except Exception as e:
       messagebox.showerror("Error", f"Failed to decode message: {str(e)}")
   finally:
       progress_bar['value'] = 0




# GUI functions
def select_image():
   image_path = filedialog.askopenfilename(filetypes=[("PNG Images", "*.png"), ("JPEG Images", "*.jpg"), ("All Files", "*.*")])
   if image_path:
       image_entry.delete(0, tk.END)
       image_entry.insert(0, image_path)




def save_encoded_image():
   return filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Images", "*.png")])




def encode():
   image_path = image_entry.get()
   message = message_entry.get("1.0", tk.END).strip()


   if not image_path:
       messagebox.showwarning("Input Error", "Please select an image.")
       return


   if not message:
       messagebox.showwarning("Input Error", "Please enter a message to encode.")
       return


   save_path = save_encoded_image()
   if not save_path:
       messagebox.showwarning("Input Error", "Please select a location to save the encoded image.")
       return


   threading.Thread(target=encode_message, args=(image_path, message, save_path, progress_bar)).start()




def decode():
   image_path = image_entry.get()


   if not image_path:
       messagebox.showwarning("Input Error", "Please select an image.")
       return


   threading.Thread(target=decode_message, args=(image_path, progress_bar)).start()




# Tkinter GUI setup
root = tk.Tk()
root.title("Steganography Tool - The Pycodes")
root.geometry("600x600")


# GUI components
tk.Label(root, text="Select Image:").pack(pady=5)
image_entry = tk.Entry(root, width=60)
image_entry.pack(pady=5)
tk.Button(root, text="Browse", command=select_image).pack(pady=5)


tk.Label(root, text="Message to Encode:").pack(pady=5)
message_entry = scrolledtext.ScrolledText(root, width=70, height=10)
message_entry.pack(pady=5)


progress_bar = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=400, mode='determinate')
progress_bar.pack(pady=10)


tk.Button(root, text="Encode Message", command=encode).pack(pady=10)
tk.Button(root, text="Decode Message", command=decode).pack(pady=5)


root.mainloop()
