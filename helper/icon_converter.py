from PIL import Image
import os

def create_icons(source_file="images/icon.png"):
    if not os.path.exists(source_file):
        print(f"Error: {source_file} not found.")
        return

    img = Image.open(source_file)

    # 1. Create Windows Icon (.ico)
    # Windows likes having multiple sizes embedded in one file for scaling
    icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    img.save("app.ico", format='ICO', sizes=icon_sizes)
    print("✓ Created app.ico")

    # 2. Create macOS Icon (.icns)
    # Pillow can generate a basic ICNS file directly
    # Note: For a production-perfect Mac icon, the native 'iconutil' method (Option 2) is superior,
    # but this works for most simple internal tools.
    img.save("app.icns", format='ICNS')
    print("✓ Created app.icns")

if __name__ == "__main__":
    create_icons()