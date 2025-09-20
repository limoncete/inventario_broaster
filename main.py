from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt

from database import get_db, init_db
from models import User, Inventario, Movimiento
from utils import verify_password, get_password_hash

SECRET_KEY = "CAMBIA_ESTO_POR_UNA_CLAVE_SEGURA"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

app = FastAPI(title="Inventario Restaurante API")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# -------------------- AUTH -------------------- #
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return user

def require_roles(*roles):
    def decorator(user: User):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="No tienes permisos")
        return user
    return decorator

# -------------------- LOGIN -------------------- #
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    access_token = create_access_token({"sub": user.username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}

# -------------------- INVENTARIO -------------------- #
@app.get("/inventario")
def listar_inventario(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Inventario).all()

@app.post("/inventario")
def agregar_producto(nombre: str, cantidad: float, unidad: str = "u", stock_min: float | None = None,
                     db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_roles("admin", "manager")(user)
    nombre = nombre.strip().lower()
    prod = db.query(Inventario).filter_by(producto=nombre).first()
    if prod:
        prod.cantidad += cantidad
        if stock_min is not None:
            prod.stock_min = stock_min
    else:
        prod = Inventario(producto=nombre, cantidad=cantidad, unidad=unidad, stock_min=stock_min)
        db.add(prod)
    db.commit()
    mov = Movimiento(producto_id=prod.id, tipo="entrada", cantidad=cantidad, usuario_id=user.id)
    db.add(mov)
    db.commit()
    return {"msg": "Producto agregado/actualizado"}

@app.post("/inventario/retirar/{nombre}")
def retirar_producto(nombre: str, cantidad: float, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_roles("admin", "manager", "staff")(user)
    nombre = nombre.strip().lower()
    prod = db.query(Inventario).filter_by(producto=nombre).first()
    if not prod:
        raise HTTPException(404, "Producto no encontrado")
    if prod.cantidad < cantidad:
        raise HTTPException(400, "Stock insuficiente")
    prod.cantidad -= cantidad
    db.commit()
    mov = Movimiento(producto_id=prod.id, tipo="salida", cantidad=cantidad, usuario_id=user.id)
    db.add(mov)
    db.commit()
    return {"msg": f"Retirados {cantidad} {prod.unidad}"}
