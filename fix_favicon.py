from PIL import Image
import os

path = r'c:\Users\Justin Lorenz\Downloads\capstone-main\accounts\static\accounts\favicon.png'

if not os.path.exists(path):
    print(f"File not found: {path}")
    exit(1)

try:
    img = Image.open(path)
    print(f"Original Dimensions: {img.size}")
    
    if img.size[0] == img.size[1]:
        print("Image is already square.")
    else:
        # Determine new square size
        new_size = max(img.size)
        
        # Create new transparent image
        new_img = Image.new("RGBA", (new_size, new_size), (0, 0, 0, 0))
        
        # Calculate position to paste original image (center)
        left = (new_size - img.size[0]) // 2
        top = (new_size - img.size[1]) // 2
        
        # Paste (using mask if available to preserve transparency)
        if img.mode == 'RGBA':
             new_img.paste(img, (left, top), img)
        else:
             new_img.paste(img, (left, top))
        
        # Save
        new_img.save(path, format="PNG")
        print(f"Resized to square: {new_img.size}")
        print("Saved successfully.")

except Exception as e:
    print(f"An error occurred: {e}")
