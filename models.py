from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Request(Base):
    __tablename__ = "requests"
    id = Column(String(36), primary_key=True)  # UUID requires length
    status = Column(Enum("Pending", "Processing", "Completed", name="status_enum"), default="Pending")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String(36), ForeignKey("requests.id"))
    name = Column(String(255))  # String must have a length

class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    input_url = Column(String(2083))  # URLs can be long
    output_url = Column(String(2083), nullable=True)  # Output URLs can be long too
