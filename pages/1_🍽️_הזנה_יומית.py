import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime
import os

st.set_page_config(page_title="🍽️ הזנה יומית")

st.header("🍽️ הוספת מזון ליומן")

CARB_UNIT = 20
PROTEIN_UNIT = 25
FAT_UNIT = 10

# פרטי החיבור שלך (שימי את הסיסמה כ-Environment Variable!)
SUPABASE_HOST = "db.ifykewhyhxkyffvnfblm.supabase.co"
SUPABASE_DB = "postgres"
SUPABASE_USER = "postgres"
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD")
SUPABASE_PORT = 5432

conn = psycopg2.connect(
    host=SUPABASE_HOST,
    database=SUPABASE_DB,
    user=SUPABASE_USER,
    password=SUPABASE_PASSWORD,
    port=SUPABASE_PORT
)
cur = conn.cursor()

# 📌 קריאה ממאגר המזונות
foods_df = pd.read_sql("SELECT * FROM food_db;", conn)

if foods_df.empty:
    st.warning("⚠️ אין מאגר מזונות.")
    st.stop()

# 📌 טופס הזנה
with st.form("log_food"):
    f = st.selectbox("מזון:", foods_df["food"].unique())
    g = st.number_input("גרם:", 0.0)
    if st.form_submit_button("➕ הוסף ליומן"):
        row = foods_df[foods_df["food"] == f].iloc[0]
        carb = g * row["carb_per_100g"] / 100
        pro = g * row["protein_per_100g"] / 100
        fat = g * row["fat_per_100g"] / 100
        cal = carb * 4 + pro * 4 + fat * 9

        # הוספה ליומן ב-DB
        insert_query = """
            INSERT INTO food_log
            (date, food, grams, carb_g, protein_g, fat_g, carb_units, protein_units, fat_units, calories)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cur.execute(insert_query, (
            datetime.today().strftime('%Y-%m-%d'),
            f, g, carb, pro, fat,
            carb / CARB_UNIT,
            pro / PROTEIN_UNIT,
            fat / FAT_UNIT,
            cal
        ))
        conn.commit()
        st.success(f"✅ נוסף {f}!")

# 📌 סיכום יומי והמחיקה
st.header("📋 מה הזנתי היום")

today_str = datetime.today().strftime('%Y-%m-%d')
daily_log = pd.read_sql(f"SELECT * FROM food_log WHERE date = '{today_str}';", conn)

if daily_log.empty:
    st.info("🙋‍♀️ לא הוזנו פריטים היום עדיין.")
else:
    st.dataframe(
        daily_log[["food","grams","carb_units","protein_units","fat_units","calories"]],
        use_container_width=True
    )

    totals = daily_log[["carb_units","protein_units","fat_units","calories"]].sum()
    st.write(
        f"🔢 סה\"כ עד כה: "
        f"🥖 פחמימה {totals['carb_units']:.2f} | "
        f"🍗 חלבון {totals['protein_units']:.2f} | "
        f"🥑 שומן {totals['fat_units']:.2f} | "
        f"🔥 קלוריות {totals['calories']:.0f}"
    )

    st.divider()
    st.subheader("🗑️ ניהול פריטים")

    for idx, row in daily_log.iterrows():
        col1, col2 = st.columns([8, 1])
        with col1:
            st.write(
                f"{row['food']} - {row['grams']} גרם | "
                f"🥖 {row['carb_units']:.2f} יח׳ | "
                f"🍗 {row['protein_units']:.2f} יח׳ | "
                f"🥑 {row['fat_units']:.2f} יח׳ | "
                f"🔥 {row['calories']:.0f} קק\"ל"
            )
        with col2:
            if st.button("🗑️ מחק", key=f"del_{idx}"):
                delete_query = "DELETE FROM food_log WHERE id = %s;"
                cur.execute(delete_query, (row['id'],))
                conn.commit()
                st.success(f"✅ נמחק {row['food']}")
                st.experimental_rerun()

cur.close()
conn.close()
