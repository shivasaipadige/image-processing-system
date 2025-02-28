# Image Processing System

## 🚀 Overview
This system processes image data asynchronously from a CSV file. Users can upload a CSV containing product names and image URLs, and the system will:
1. Validate and store the request.
2. Asynchronously download and compress images.
3. Store the processed images and update the database.
4. Provide an API to check the status.
5. Trigger a webhook once processing is completed.

## 🛠️ Features
- **Asynchronous Processing**: Background tasks for non-blocking image compression.
- **Database Management**: Stores request data and image processing results.
- **Webhook Integration**: Notifies the user when all images are processed.
- **API Endpoints**:
  - POST /upload/ – Upload a CSV file for processing.
  - GET /status/{request_id} – Check the processing status.

## 📊 Workflow Diagram
The following diagram illustrates the system's processing flow:

![image](https://github.com/user-attachments/assets/0fac1041-0250-44d6-94dd-07be1cbbcd6f)



## 📜 Low-Level Design (LLD)
### **1. System Overview**
The system processes image data from CSV files asynchronously, compresses images, and stores the results in a database. Users can:
1. Upload a CSV file containing product names and image URLs.
2. Receive a request ID to track processing status.
3. Query the system for processing status.
4. Receive a webhook notification upon completion.

### **2. Component Breakdown**
#### **API Endpoints**
- **Upload API (POST /upload/)**:
  - Accepts a CSV file.
  - Validates the file format.
  - Stores data in the database.
  - Returns a unique request ID.
  - Starts asynchronous image processing.
- **Status API (GET /status/{request_id})**:
  - Returns the current processing status.
  - Provides image URLs (input and processed images).
- **Webhook Notification**:
  - Triggers a callback to a provided URL upon completion.

#### **Database Schema**
**Tables & Attributes:**
- **requests** (Tracks each request)
  - id (UUID, Primary Key)
  - status (Pending, Processing, Completed)
  - created_at (Timestamp)
- **products** (Stores product data)
  - id (Primary Key)
  - request_id (Foreign Key → requests.id)
  - name (Product Name)
- **images** (Stores input & output image URLs)
  - id (Primary Key)
  - product_id (Foreign Key → products.id)
  - input_url (Original image URL)
  - output_url (Processed image URL, nullable)

#### **Image Processing Worker**
- Fetches unprocessed images from the database.
- Downloads images, compresses them by 50%.
- Saves the processed images.
- Updates the database with output image URLs.
- Marks request as Completed after processing all images.
- Sends a webhook callback if a webhook URL is provided.
