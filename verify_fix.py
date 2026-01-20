from PIL import Image
import os

path = r'c:\Users\Justin Lorenz\Downloads\capstone-main\accounts\static\accounts\favicon.png'
with open('verify_output.txt', 'w', encoding='utf-8') as f:
    try:
        img = Image.open(path)
        f.write(f"Refreshed Dimensions: {img.size}\n")
    except Exception as e:
        f.write(f"Error: {e}\n")
