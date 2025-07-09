import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="🍽️ הזנה יומית")

st.header("🍽️ הוספת מזון ליומן")
FOODS_FILE = "food_db.csv"
LOG_FILE = "food_log.csv"

CARB_UNIT = 20
PROTEIN_UNIT = 25
FAT_UNIT = 10

# טען מאגר מזונות
if os.path.exists(FOODS_FILE):
    foods_df = pd.read_csv(FOODS_FILE)
else:
    st.warning("⚠️ אין מאגר מזונות.")
    st.stop()

# טען יומן אכילה
if os.path.exists(LOG_FILE):
    log_df = pd.read_csv(LOG_FILE)
else:
    log_df = pd.DataFrame(columns=[
        "Date","Food","Grams","Carb_g","Protein_g","Fat_g",
        "Carb_units","Protein_units","Fat_units","Calories"
    ])
    log_df.to_csv(LOG_FILE, index=False)

# 📌 טופס הזנה
with st.form("log_food"):
    f = st.selectbox("מזון:", foods_df["Food"].unique())
    g = st.number_input("גרם:", 0.0)
    if st.form_submit_button("➕ הוסף ליומן"):
        row = foods_df[foods_df["Food"] == f].iloc[0]
        carb = g * row["Carb_per_100g"] / 100
        pro = g * row["Protein_per_100g"] / 100
        fat = g * row["Fat_per_100g"] / 100
        cal = carb * 4 + pro * 4 + fat * 9

        new_row = pd.DataFrame([[
            datetime.today().strftime('%Y-%m-%d'),
            f, g, carb, pro, fat,
            carb / CARB_UNIT, pro / PROTEIN_UNIT, fat / FAT_UNIT,
            cal
        ]], columns=log_df.columns)

        log_df = pd.concat([log_df, new_row], ignore_index=True)
        log_df.to_csv(LOG_FILE, index=False)
        st.success(f"✅ נוסף {f}!")

# 📌 סיכום יומי והמחיקה
st.header("📋 מה הזנתי היום")

today_str = datetime.today().strftime('%Y-%m-%d')
daily_log = log_df[log_df["Date"] == today_str]

if daily_log.empty:
    st.info("🙋‍♀️ לא הוזנו פריטים היום עדיין.")
else:
    # טבלה עם סיכום
    st.dataframe(
        daily_log[["Food","Grams","Carb_units","Protein_units","Fat_units","Calories"]],
        use_container_width=True
    )

    # סיכום כולל
    totals = daily_log[["Carb_units","Protein_units","Fat_units","Calories"]].sum()
    st.write(
        f"🔢 סה\"כ עד כה: "
        f"🥖 פחמימה {totals['Carb_units']:.2f} | "
        f"🍗 חלבון {totals['Protein_units']:.2f} | "
        f"🥑 שומן {totals['Fat_units']:.2f} | "
        f"🔥 קלוריות {totals['Calories']:.0f}"
    )

    st.divider()
    st.subheader("🗑️ ניהול פריטים")

    for idx, row in daily_log.iterrows():
        col1, col2 = st.columns([8, 1])
        with col1:
            st.write(
                f"{row['Food']} - {row['Grams']} גרם | "
                f"🥖 {row['Carb_units']:.2f} יח׳ | "
                f"🍗 {row['Protein_units']:.2f} יח׳ | "
                f"🥑 {row['Fat_units']:.2f} יח׳ | "
                f"🔥 {row['Calories']:.0f} קק\"ל"
            )
        with col2:
            if st.button("🗑️ מחק", key=f"del_{idx}"):
                log_df = log_df.drop(idx)
                log_df.to_csv(LOG_FILE, index=False)
                st.success(f"✅ נמחק {row['Food']}")
                st.rerun()

