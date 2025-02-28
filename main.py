import os
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Form
import csv
import uuid
from database import SessionLocal
from models import Request, Product, Image
from image_processing import process_images

app = FastAPI()

@app.post("/upload/")
async def upload_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    webhook_url: str = Form(None)  
):
    try:
        request_id = str(uuid.uuid4())
        db = SessionLocal()
        new_request = Request(id=request_id, status="Pending")
        db.add(new_request)
        db.commit()

        contents = await file.read()
        csv_data = contents.decode().splitlines()
        rows = csv.reader(csv_data)

        header = next(rows, None)
        if header is None or len(header) < 3:
            raise HTTPException(status_code=400, detail="Invalid CSV format")

        for row in rows:
            if len(row) < 3:
                print(f"Skipping invalid row: {row}")
                continue

            serial, product_name, input_urls = row
            new_product = Product(request_id=request_id, name=product_name)
            db.add(new_product)
            db.commit()

            for url in input_urls.split(','):
                db.add(Image(product_id=new_product.id, input_url=url.strip()))

        db.commit()

        background_tasks.add_task(process_images, request_id, webhook_url)

        return {"request_id": request_id, "message": "Processing started"}

    except Exception as e:
        print(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/status/{request_id}")
def get_status(request_id: str):
    db = SessionLocal()
    request = db.query(Request).filter_by(id=request_id).first()

    if not request:
        raise HTTPException(status_code=404, detail="Request ID not found")

    images = db.query(Image).join(Product).filter(Product.request_id == request_id).all()

    image_data = []
    for img in images:
        original_filepath = f"static/original/{os.path.basename(img.output_url).replace('_compressed', '')}"
        compressed_filepath = f"static/processed/{os.path.basename(img.output_url)}"

        original_size = os.path.getsize(original_filepath) if os.path.exists(original_filepath) else None
        compressed_size = os.path.getsize(compressed_filepath) if os.path.exists(compressed_filepath) else None

        image_data.append({
            "input_url": img.input_url,
            "output_url": img.output_url,
            "original_size": original_size,
            "compressed_size": compressed_size
        })

    return {
        "request_id": request_id,
        "status": request.status,
        "images": image_data
    }
