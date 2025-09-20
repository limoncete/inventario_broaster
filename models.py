from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(Enum("admin", "manager", "staff", name="user_roles"), nullable=False)
    movimientos = relationship("Movimiento", back_populates="user")

class Inventario(Base):
    __tablename__ = "inventario"
    id = Column(Integer, primary_key=True)
    producto = Column(String(200), unique=True, nullable=False)
    cantidad = Column(Float, nullable=False, default=0.0)
    unidad = Column(String(20), nullable=True)
    stock_min = Column(Float, nullable=True)
    movimientos = relationship("Movimiento", back_populates="producto_obj")

class Movimiento(Base):
    __tablename__ = "movimientos"
    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey("inventario.id"))
    tipo = Column(String(10), nullable=False)
    cantidad = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    usuario_id = Column(Integer, ForeignKey("users.id"))
    nota = Column(String(255), nullable=True)
    producto_obj = relationship("Inventario", back_populates="movimientos")
    user = relationship("User", back_populates="movimientos")
