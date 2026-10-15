import streamlit as st
import json
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Налаштування сторінки
st.set_page_config(page_title="ОВДП Ultimate Портфель", page_icon="📊", layout="wide")

DATA_FILE = "ovdp_pro_data.json"

# --- КАСТОМНІ CSS СТИЛІ ---
st.markdown("""
    <style>
    /* Яскраво-білі чіткі цифри для шапки метрик */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"], [data-testid="stMetricDelta"] {
        color: #ffffff !important;
    }
    div[data-testid="metric-container"] * {
        color: #ffffff !important;
    }

    /* Компактні кнопки */
    div.stButton > button {
        border-radius: 8px !important;
        font-weight: bold !important;
        width: 100% !important;
    }
    </style>
""", unsafe_allow_html=True)

# Початкові дані за замовчуванням
DEFAULT_BONDS = [
    {"isin": "UA4000239081", "name": "ОВДП Позиція 1", "price": 1082.05, "coupon": 80.80, "total_coupons": 6, "ytm": 16.85, "maturity": "20.02.2027", "qty": 5},
    {"isin": "UA4000204861", "name": "ОВДП Позиція 2", "price": 1045.00, "coupon": 45.00, "total_coupons": 4, "ytm": 15.50, "maturity": "15.10.2026", "qty": 10}
]

CHART_COLORS = ["#2ecc71", "#3498db", "#e74c3c", "#f1c40f", "#9b59b6", "#1abc9c", "#e67e22", "#e84393"]

# Завантаження та збереження даних
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

# --- БОКОВА ПАНЕЛЬ (НАЛАШТУВАННЯ ТА ТЕМИ) ---
st.sidebar.title("⚙️ Керування")
theme = st.sidebar.selectbox("Оберіть тему оформлення:", ["Темна (Класична)", "Світла", "Смарагдова"])

# Налаштування кольорів та фону залежно від теми
if theme == "Світла":
    fig_bg = "#ffffff"
    text_color = "#2c3e50"
    st.markdown("""
        <style>
        .stApp { background-color: #f8f9fa; color: #2c3e50; }
        </style>
    """, unsafe_allow_html=True)
elif theme == "Смарагдова":
    fig_bg = "#0f2518"
    text_color = "#e8f8f0"
    st.markdown("""
        <style>
        .stApp { background-color: #0b1f14; color: #e8f8f0; }
        </style>
    """, unsafe_allow_html=True)
else: # Темна (Класична)
    fig_bg = "#1e1e1e"
    text_color = "white"
    st.markdown("""
        <style>
        .stApp { background-color: #121212; color: white; }
        </style>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.subheader("📂 Резервна копія")

# Кнопки Експорту / Імпорту
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

# --- ГОЛОВНИЙ ЕКРАН ---
st.title("📊 Облік портфеля ОВДП та Ланцюжок Реінвестування")

# Розрахунок загальних показників
total_inv = sum(b["price"] * b["qty"] for b in st.session_state.bonds)
total_net_profit = sum((b["coupon"] * b.get("total_coupons", 6) - (b["price"] - 1000.0)) * b["qty"] for b in st.session_state.bonds)
total_payout = sum((1000.0 * b["qty"]) + ((b["coupon"] * b.get("total_coupons", 6) - (b["price"] - 1000.0)) * b["qty"]) for b in st.session_state.bonds)
weighted_ytm = sum(b["ytm"] * (b["price"] * b["qty"]) for b in st.session_state.bonds) / total_inv if total_inv > 0 else 0

# Виведення метрик у шапці
m1, m2, m3, m4 = st.columns(4)
m1.metric("Загальні інвестиції", f"{total_inv:,.2f} ₴")
m2.metric("Загальний чистий дохід", f"+{total_net_profit:,.2f} ₴")
m3.metric("До виплати загалом", f"{total_payout:,.2f} ₴")
m4.metric("Середній YTM", f"{weighted_ytm:.2f}%")

st.markdown("---")

# Створення вкладок
tab1, tab2, tab3 = st.tabs(["📊 Портфель та Облігації", "📈 Динамічні графіки й Реінвест", "📋 Аналітичний звіт"])

# --- ВКЛАДКА 1: ПОРТФЕЛЬ ---
with tab1:
    st.subheader("Список позицій у портфелі")

    # Кнопка додавання нової облігації
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

    # Відображення карток з чіткими кольоровими рамками акцій
    for idx, b in enumerate(st.session_state.bonds):
        color = CHART_COLORS[idx % len(CHART_COLORS)]

        # Відкриваємо кольорову рамку
        st.markdown(f'''
            <div style="border: 2px solid {color}; border-radius: 15px; padding: 18px; margin-bottom: 20px; background-color: rgba(255, 255, 255, 0.02);">
                <h4 style="margin-top: 0; color: {color};">● {b['isin']} — {b.get('name', 'ОВДП')}</h4>
                <p style="margin-bottom: 5px;"><b>Ціна:</b> {b['price']} ₴ | <b>Купон:</b> {b['coupon']} ₴ ({b.get('total_coupons', 6)} вип.) | <b>YTM:</b> {b['ytm']}% | <b>Погашення:</b> {b['maturity']}</p>
                <p style="margin-bottom: 15px;"><b>Кількість:</b> {b['qty']} шт. | <b>Інвестиції:</b> {b['price'] * b['qty']:,.2f} ₴</p>
        ''', unsafe_allow_html=True)

        # Кнопки керування
        c_minus, c_plus, c_del = st.columns(3)
        
        with c_minus:
            if st.button("➖ Менше", key=f"minus_{idx}"):
                if b['qty'] > 0:
                    b['qty'] -= 1
                    save_data(st.session_state.bonds)
                    st.rerun()
        with c_plus:
            if st.button("➕ Більше", key=f"plus_{idx}"):
                b['qty'] += 1
                save_data(st.session_state.bonds)
                st.rerun()
        with c_del:
            if st.button("❌ Видалити", key=f"del_{idx}"):
                del st.session_state.bonds[idx]
                save_data(st.session_state.bonds)
                st.rerun()

        # Закриваємо рамку
        st.markdown('</div>', unsafe_allow_html=True)

# --- ВКЛАДКА 2: ГРАФІКИ ТА РЕІНВЕСТУВАННЯ ---
with tab2:
    st.subheader("📈 Динамічні графіки росту та ланцюжок реінвестування")

    monthly_contrib = st.number_input("Щомісячне додаткове поповнення портфеля (₴):", value=15000.0)

    st.markdown("### 🌟 Ланцюжок реінвестування персонального капіталу")
    st.markdown("Вкажіть періоди, ставки та початкові суми. Після закінчення періоду кошти автоматично переносяться далі під новий відсоток.")

    if 'reinvest_periods' not in st.session_state:
        st.session_state.reinvest_periods = [
            {"start": "16.10.2026", "end": "16.10.2027", "rate": 16.5, "initial": 50000.0},
            {"start": "16.10.2027", "end": "16.10.2028", "rate": 14.0, "initial": 0.0}
        ]

    for p_idx, period in enumerate(st.session_state.reinvest_periods):
        col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns([2, 2, 2, 2, 1])
        period["start"] = col_p1.text_input(f"Старт {p_idx+1}", period["start"], key=f"p_start_{p_idx}")
        period["end"] = col_p2.text_input(f"Кінець {p_idx+1}", period["end"], key=f"p_end_{p_idx}")
        period["rate"] = col_p3.number_input(f"Ставка % {p_idx+1}", value=period["rate"], key=f"p_rate_{p_idx}")
        period["initial"] = col_p4.number_input(f"Сума {p_idx+1}", value=period["initial"], key=f"p_init_{p_idx}")

        if col_p5.button("🗑️", key=f"del_p_{p_idx}") and len(st.session_state.reinvest_periods) > 1:
            st.session_state.reinvest_periods.pop(p_idx)
            st.rerun()

    if st.button("➕ Додати період реінвестування"):
        last_end = st.session_state.reinvest_periods[-1]["end"] if st.session_state.reinvest_periods else "20.02.2028"
        st.session_state.reinvest_periods.append({"start": last_end, "end": "20.02.2029", "rate": 12.0, "initial": 0.0})
        st.rerun()

    # Побудова графіка за допомогою Matplotlib
    fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
    fig.patch.set_facecolor(fig_bg)
    ax.set_facecolor(fig_bg)

    today = datetime.now()
    max_days = 365 * 3
    total_steps = 60
    step_days = max(1, max_days // total_steps)

    for idx, b in enumerate(st.session_state.bonds):
        color = CHART_COLORS[idx % len(CHART_COLORS)]
        b_inv = b["price"] * b["qty"]
        daily_rate = (b.get("ytm", 16.0) / 100.0) / 365.0

        try:
            mat_date = datetime.strptime(b.get("maturity", "20.02.2028"), "%d.%m.%Y")
        except ValueError:
            mat_date = today + timedelta(days=730)

        days_to_mat = max(1, (mat_date - today).days)
        x_vals, y_vals = [], []

        for step in range(total_steps + 1):
            current_days = min(days_to_mat, int(step * step_days))
            years_passed = current_days / 365.0
            cur_val = b_inv * ((1 + daily_rate) ** current_days)
            x_vals.append(years_passed)
            y_vals.append(cur_val)
            if current_days >= days_to_mat:
                break

        ax.plot(x_vals, y_vals, label=f"{b['isin']} ({b.get('name', 'ОВДП')})", color=color, linewidth=2.5)

    parsed_periods = []
    for p in st.session_state.reinvest_periods:
        try:
            parsed_periods.append({
                "start": datetime.strptime(p["start"].strip(), "%d.%m.%Y"),
                "end": datetime.strptime(p["end"].strip(), "%d.%m.%Y"),
                "rate": p["rate"] / 100.0,
                "initial": p["initial"]
            })
        except ValueError:
            pass

    if parsed_periods:
        chain_x, chain_y = [], []
        current_capital = 0.0

        for i, period in enumerate(parsed_periods):
            p_start, p_end, p_rate, p_init = period["start"], period["end"], period["rate"], period["initial"]
            if p_init > 0 or i == 0:
                current_capital += p_init

            days_in_period = max(1, (p_end - p_start).days)
            daily_r = p_rate / 365.0
            sim_days = 0

            while sim_days <= days_in_period:
                day_date = p_start + timedelta(days=sim_days)
                if day_date >= today:
                    from_today = (day_date - today).days
                    current_capital *= (1 + daily_r)
                    chain_x.append(from_today / 365.0)
                    chain_y.append(current_capital)
                sim_days += max(1, days_in_period // 20)

        if chain_x:
            ax.plot(chain_x, chain_y, label="🌟 Персональний реінвест (ланцюжок)", color="#ff3838", linewidth=3.5, linestyle="--")

    ax.set_title("Динаміка портфеля та реінвестування", color=text_color, fontsize=12, fontweight="bold")
    ax.set_xlabel("Роки", color=text_color)
    ax.set_ylabel("Сума (₴)", color=text_color)
    ax.tick_params(colors=text_color)
    for spine in ax.spines.values():
        spine.set_color(text_color)
    ax.legend(facecolor=fig_bg, edgecolor="none", labelcolor=text_color, fontsize=9)
    ax.grid(True, linestyle=":", alpha=0.3, color=text_color)
    fig.tight_layout()

    st.pyplot(fig)

# --- ВКЛАДКА 3: АНАЛІТИЧНИЙ ЗВІТ ---
with tab3:
    st.subheader("📋 Структурований звіт за датами погашення")

    def parse_date(bond):
        try:
            return datetime.strptime(bond.get("maturity", "31.12.2099"), "%d.%m.%Y")
        except ValueError:
            return datetime(2099, 12, 31)

    sorted_bonds = sorted(st.session_state.bonds, key=parse_date)

    report_md = f"""
### 📊 Загальні підсумки портфеля:
- **Загальна сума інвестицій:** {total_inv:,.2f} ₴
- **Загальний чистий прибуток:** +{total_net_profit:,.2f} ₴
- **Сума до виплати при закритті:** {total_payout:,.2f} ₴
- **Середньозважений YTM:** {weighted_ytm:.2f}%

---
### 📅 Закриття позицій (від найближчої до найдальшої):
"""
    for b in sorted_bonds:
        pos_inv = b["price"] * b["qty"]
        t_coupons = b.get("total_coupons", 6)
        total_coup = b["coupon"] * t_coupons * b["qty"]
        price_diff_loss = (b["price"] - 1000.0) * b["qty"]
        net_profit = total_coup - price_diff_loss
        nominal_payout_pos = 1000.0 * b["qty"] + net_profit

        report_md += f"""
- **{b['isin']} — {b.get('name', 'Без назви')}**
  * 📅 Дата закриття: **{b.get('maturity', 'Не вказано')}**
  * 📦 Кількість: `{b['qty']} шт.` | Інвестиції: `{pos_inv:,.2f} ₴`
  * 🎟️ Сума купонів: `+{total_coup:,.2f} ₴` | Збиток на номіналі: `-{price_diff_loss:,.2f} ₴`
  * 💵 Чистий дохід: `+{net_profit:,.2f} ₴` | 🏁 До виплати: `{nominal_payout_pos:,.2f} ₴`
"""
    st.markdown(report_md)