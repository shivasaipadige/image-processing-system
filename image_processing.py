import os
import requests
from PIL import Image
from io import BytesIO
import uuid
from database import SessionLocal
from models import Request, Image as ImageModel, Product

def process_images(request_id, webhook_url=None):  
    db = SessionLocal()
    request = db.query(Request).filter_by(id=request_id).first()
    if not request:
        print(f"Request ID {request_id} not found")
        return

    request.status = "Processing"
    db.commit()

    original_dir = "static/original"
    processed_dir = "static/processed"
    os.makedirs(original_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)

    images = db.query(ImageModel).join(Product).filter(Product.request_id == request_id).all()

    for img in images:
        try:
            print(f"Downloading image: {img.input_url}")

            response = requests.get(img.input_url, timeout=10)
            response.raise_for_status()

            file_id = uuid.uuid4().hex
            filename = f"{file_id}.jpg"

            original_filepath = os.path.join(original_dir, filename)
            with open(original_filepath, "wb") as f:
                f.write(response.content)

            original_size = os.path.getsize(original_filepath)
            print(f"Original Image Saved: {original_filepath} ({original_size} bytes)")

            compressed_filename = f"{file_id}_compressed.jpg"
            compressed_filepath = os.path.join(processed_dir, compressed_filename)

            image = Image.open(original_filepath)
            image.save(compressed_filepath, "JPEG", quality=50)

            compressed_size = os.path.getsize(compressed_filepath)
            print(f"Compressed Image Saved: {compressed_filepath} ({compressed_size} bytes)")

            db.query(ImageModel).filter(ImageModel.id == img.id).update({
                "output_url": f"/{compressed_filepath}"
            })
            db.commit()

            img.processed_info = {
                "input_url": img.input_url,
                "output_url": f"/{compressed_filepath}",
                "original_size": original_size,
                "compressed_size": compressed_size
            }

        except Exception as e:
            print(f"Error processing image {img.input_url}: {e}")

    request.status = "Completed"
    db.commit()

    if webhook_url:
        print(f"Triggering Webhook: {webhook_url}")
        try:
            response = requests.post(webhook_url, json={
                "request_id": request_id,
                "status": "Completed",
                "images": [{"input_url": img.input_url, "output_url": img.output_url} for img in images]
            })
            print(f"Webhook Response: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Failed to send webhook: {e}")
