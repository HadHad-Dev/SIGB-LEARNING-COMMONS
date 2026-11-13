from PIL import Image, ImageTk

def load_image(path, size):
        return ImageTk.PhotoImage(Image.open(path).resize(size, Image.ADAPTIVE))