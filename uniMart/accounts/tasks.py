from celery import shared_task
from PIL import Image

@shared_task
def resize_image(image):
    img = Image.open(image)
    if img.height > 300 or img.width > 300:
        output_size = (300, 300)
        img.thumbnail(output_size)
        img.save(image)