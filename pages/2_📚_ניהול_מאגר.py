import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="📚 ניהול מאגר")

st.header("📚 ניהול מאגר מזונות")
FOODS_FILE = "food_db.csv"

# טען או צור את הקובץ
if os.path.exists(FOODS_FILE):
    df = pd.read_csv(FOODS_FILE)
else:
    df = pd.DataFrame(columns=[
        "Food",
        "Carb_per_100g",
        "Protein_per_100g",
        "Fat_per_100g",
        "Calories_per_100g"
    ])
    df.to_csv(FOODS_FILE, index=False)

# ➕ הוספה
with st.form("add_food"):
    st.subheader("➕ הוסף מזון")
    f = st.text_input("שם")
    c = st.number_input("פחמימה/100 גרם", 0.0)
    p = st.number_input("חלבון/100 גרם", 0.0)
    fat = st.number_input("שומן/100 גרם", 0.0)
    cal = st.number_input("קלוריות/100 גרם", 0.0)
    if st.form_submit_button("💾 שמור"):
        df = pd.concat(
            [df, pd.DataFrame([[f, c, p, fat, cal]], columns=df.columns)],
            ignore_index=True
        )
        df.to_csv(FOODS_FILE, index=False)
        st.success(f"✅ נוסף {f}")

# 📄 הצגת הטבלה עם כפתורי מחיקה
st.divider()
st.subheader("📄 מאגר מזון קיים")

if df.empty:
    st.info("📂 המאגר עדיין ריק.")
else:
    for idx, row in df.iterrows():
        col1, col2 = st.columns([8, 1])
        with col1:
            st.write(
                f"{row['Food']} | 🍚 פחמ' {row['Carb_per_100g']} | "
                f"🍗 חלבון {row['Protein_per_100g']} | 🥑 שומן {row['Fat_per_100g']} | "
                f"🔥 קלוריות {row['Calories_per_100g']}"
            )
        with col2:
            if st.button("🗑️ מחק", key=f"del_{idx}"):
                df = df.drop(idx)
                df.to_csv(FOODS_FILE, index=False)
                st.success(f"🗑️ נמחק {row['Food']}")
                st.rerun()

# אם תרצי להשאיר גם בלוק עריכה רגיל — תשאירי מתחת או תורידי
