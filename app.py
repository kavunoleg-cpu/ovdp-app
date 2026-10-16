import streamlit as st
import json
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

st.set_page_config(page_title="ОВДП Ultimate Портфель", page_icon="📊", layout="wide")

DATA_FILE = "ovdp_pro_data.json"

st.markdown("""
    <style>
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"], [data-testid="stMetricDelta"] {
        color: #ffffff !important;
    }
    div[data-testid="metric-container"] * {
        color: #ffffff !important;
    }
    
    div.stButton > button {
        border-radius: 6px !important;
        font-weight: bold !important;
        width: 100% !important;
        color: white !important;
        border: none !important;
        padding: 4px 8px !important;
        min-height: 32px !important;
    }
    div.stButton:nth-of-type(1) > button {
        background-color: #2980b9 !important;
    }
    div.stButton:nth-of-type(2) > button {
        background-color: #27ae60 !important;
    }
    div.stButton:nth-of-type(3) > button {
        background-color: #c0392b !important;
    }
    </style>
""", unsafe_allow_html=True)

DEFAULT_BONDS = [
    {"isin": "UA4000239081", "name": "ОВДП Позиція 1", "price": 1082.05, "coupon": 80.80, "total_coupons": 6, "ytm": 16.85, "maturity": "20.02.2027", "qty": 5},
    {"isin": "UA4000204861", "name": "ОВДП Позиція 2", "price": 1045.00, "coupon": 45.00, "total_coupons": 4, "ytm": 15.50, "maturity": "15.10.2026", "qty": 10}
]

CHART_COLORS = ["#2ecc71", "#3498db", "#e74c3c", "#f1c40f", "#9b59b6", "#1abc9c", "#e67e22", "#e84393"]

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_BONDS

def save_data(bonds):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(bonds, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Помилка збереження: {e}")

if 'bonds' not in st.session_state:
    st.session_state.bonds = load_data()

st.sidebar.title("⚙️ Керування")
theme = st.sidebar.selectbox("Оберіть тему оформлення:", ["Темна (Класична)", "Світла", "Смарагдова"])

if theme == "Світла":
    fig_bg = "#ffffff"
    text_color = "#2c3e50"
    st.markdown("""<style>.stApp { background-color: #f8f9fa; color: #2c3e50; }</style>""", unsafe_allow_html=True)
elif theme == "Смарагдова":
    fig_bg = "#0f2518"
    text_color = "#e8f8f0"
    st.markdown("""<style>.stApp { background-color: #0b1f14; color: #e8f8f0; }</style>""", unsafe_allow_html=True)
else:
    fig_bg = "#1e1e1e"
    text_color = "white"
    st.markdown("""<style>.stApp { background-color: #121212; color: white; }</style>""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.subheader("📂 Резервна копія")

json_str = json.dumps(st.session_state.bonds, ensure_ascii=False, indent=4)
st.sidebar.download_button(label="💾 Експорт JSON", data=json_str, file_name="ovdp_portfolio.json", mime="application/json")

uploaded_file = st.sidebar.file_uploader("📂 Імпорт JSON", type=["json"])
if uploaded_file is not None:
    try:
        st.session_state.bonds = json.load(uploaded_file)
        save_data(st.session_state.bonds)
        st.sidebar.success("Дані успішно завантажено!")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Помилка читання файлу: {e}")

st.title("📊 Облік портфеля ОВДП та Ланцюжок Реінвестування")

total_inv = sum(b["price"] * b["qty"] for b in st.session_state.bonds)
total_net_profit = sum((b["coupon"] * b.get("total_coupons", 6) - (b["price"] - 1000.0)) * b["qty"] for b in st.session_state.bonds)
total_payout = sum((1000.0 * b["qty"]) + ((b["coupon"] * b.get("total