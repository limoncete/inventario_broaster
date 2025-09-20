# inventario_broaster
# sugerencia de distribucion.
# backend/
    main.py
    database.py
    models.py
    utils.py
# ponerlo en marcha
cd backend
python -c "from database import init_db; init_db()"  # Inicializar DB
uvicorn main:app --reload
# crear un usuario admin
from backend.database import SessionLocal
from backend.models import User
from backend.utils import get_password_hash

db = SessionLocal()
admin = User(username="admin", password_hash=get_password_hash("1234"), role="admin")
db.add(admin)
db.commit()
db.close()
# Front End
cd frontend
streamlit run app.py
# abre el navegador http://localhost:8983

# MISMA RED LOCAL

# 1. Levantas la API con host 0.0.0.0 para aceptar conexiones de la LAN :
uvicorn main:app --host 0.0.0.0 --port 8000
# 2. obtienes la ip del host  ejemplo 192.168.2.68
# 3. En streamlit configuras:
API_URL = "http://192.168.1.50:8000"
