import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Inventario Restaurante", page_icon="📦", layout="centered")
st.title("📦 Inventario Restaurante")

if "token" not in st.session_state:
    st.subheader("🔐 Login")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Login"):
        r = requests.post(f"{API_URL}/token", data={"username": username, "password": password})
        if r.status_code == 200:
            data = r.json()
            st.session_state["token"] = data["access_token"]
            st.session_state["role"] = data["role"]
            st.success("Login correcto")
        else:
            st.error("Usuario o contraseña incorrectos")
else:
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    role = st.session_state["role"]

    menu = st.sidebar.radio("Menú", ["📋 Ver inventario"])
    if role in ["admin", "manager"]:
        menu = st.sidebar.radio("Menú", ["📋 Ver inventario", "➕ Agregar producto", "➖ Retirar producto", "📝 Ajustar stock mínimo"])
    if role == "admin":
        menu = st.sidebar.radio("Menú", ["📋 Ver inventario", "➕ Agregar producto", "➖ Retirar producto", "📝 Ajustar stock mínimo", "🧑‍💼 Gestionar usuarios"])

    if menu == "📋 Ver inventario":
        r = requests.get(f"{API_URL}/inventario", headers=headers)
        if r.status_code == 200:
            data = r.json()
            st.table(data)
    elif menu == "➕ Agregar producto" and role in ["admin", "manager"]:
        st.subheader("Agregar producto")
        nombre = st.text_input("Nombre")
        cantidad = st.number_input("Cantidad", min_value=0.0, step=0.1)
        unidad = st.selectbox("Unidad", ["u","kg","litros","cajas"])
        stock_min = st.number_input("Stock mínimo", min_value=0.0, step=0.1)
        if st.button("Agregar"):
            r = requests.post(f"{API_URL}/inventario",
                              headers=headers,
                              params={"nombre": nombre, "cantidad": cantidad, "unidad": unidad, "stock_min": stock_min})
            if r.status_code == 200:
                st.success("Producto agregado")
            else:
                st.error("Error")
    elif menu == "➖ Retirar producto":
        st.subheader("Retirar producto")
        nombre = st.text_input("Nombre del producto a retirar")
        cantidad = st.number_input("Cantidad a retirar", min_value=0.0, step=0.1)
        if st.button("Retirar"):
            r = requests.post(f"{API_URL}/inventario/retirar/{nombre}",
                              headers=headers,
                              params={"cantidad": cantidad})
            if r.status_code == 200:
                st.success(r.json()["msg"])
            else:
                st.error("Error al retirar producto")
    elif menu == "🚪 Cerrar sesión":
        del st.session_state["token"]
        st.success("Sesión cerrada")

