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
total_payout = sum((1000.0 * b["qty"]) + ((b["coupon"] * b.get("total_coupons", 6) - (b["price"] - 1000.0)) * b["qty"]) for b in st.session_state.bonds)
weighted_ytm = (sum(b["ytm"] * (b["price"] * b["qty"]) for b in st.session_state.bonds) / total_inv) if total_inv > 0 else 0.0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Загальні інвестиції", f"{total_inv:,.2f} ₴")
m2.metric("Загальний чистий дохід", f"+{total_net_profit:,.2f} ₴")
m3.metric("До виплати загалом", f"{total_payout:,.2f} ₴")
m4.metric("Середній YTM", f"{weighted_ytm:.2f}%")

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📊 Портфель та Облігації", "📈 Динамічні графіки й Реінвест", "📋 Аналітичний звіт"])

with tab1:
    st.subheader("Список позицій у портфелі")

    with st.expander("➕ Додати нову облігацію"):
        with st.form("add_bond_form"):
            col_a, col_b = st.columns(2)
            new_isin = col_a.text_input("ISIN код", "UA4000...")
            new_name = col_b.text_input("Назва", "ОВДП")

            col_c, col_d = st.columns(2)
            new_price = col_c.number_input("Ціна купівлі (₴)", value=1000.0)
            new_coupon = col_d.number_input("Сума 1 купона (₴)", value=40.0)

            col_e, col_f = st.columns(2)
            new_tot_coup = col_e.number_input("Кількість виплат купонів", value=6, step=1)
            new_ytm = col_f.number_input("YTM (%)", value=16.0)

            col_g, col_h = st.columns(2)
            new_mat = col_g.text_input("Дата погашення (ДД.ММ.РРРР)", "20.02.2028")
            new_qty = col_h.number_input("Кількість шт.", value=1, step=1)

            submit_add = st.form_submit_button("Зберегти облігацію")
            if submit_add:
                st.session_state.bonds.append({
                    "isin": new_isin, "name": new_name, "price": new_price,
                    "coupon": new_coupon, "total_coupons": int(new_tot_coup),
                    "ytm": new_ytm, "maturity": new_mat, "qty": int(new_qty)
                })
                save_data(st.session_state.bonds)
                st.success("Облігацію додано!")
                st.rerun()

    for idx, b in enumerate(st.session_state.bonds):
        color = CHART_COLORS[idx % len(CHART_COLORS)]
        pos_inv = b['price'] * b['qty']

        with st.container(border=True):
            st.markdown(f"<h4 style='margin-top: 0; margin-bottom: 8px; color: {color};'>● {b['isin']} — {b.get('name', 'ОВДП')}</h4>", unsafe_allow_html=True)
            st.write(f"**Ціна:**