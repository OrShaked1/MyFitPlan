import streamlit as st
import pandas as pd
import psycopg2
import os

st.set_page_config(page_title="📚 ניהול מאגר")

st.header("📚 ניהול מאגר מזונות")

# פרטי חיבור
SUPABASE_HOST = "db.ifykewhyhxkyffvnfblm.supabase.co"
SUPABASE_DB = "postgres"
SUPABASE_USER = "postgres"
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD")
SUPABASE_PORT = 5432

# יצירת חיבור למסד הנתונים
conn = psycopg2.connect(
    host=SUPABASE_HOST,
    database=SUPABASE_DB,
    user=SUPABASE_USER,
    password=SUPABASE_PASSWORD,
    port=SUPABASE_PORT
)
cur = conn.cursor()

# טען את המאגר
df = pd.read_sql("SELECT * FROM food_db ORDER BY food;", conn)

# ➕ הוספה
with st.form("add_food"):
    st.subheader("➕ הוסף מזון")
    f = st.text_input("שם")
    c = st.number_input("פחמימה/100 גרם", 0.0)
    p = st.number_input("חלבון/100 גרם", 0.0)
    fat = st.number_input("שומן/100 גרם", 0.0)
    cal = st.number_input("קלוריות/100 גרם", 0.0)
    if st.form_submit_button("💾 שמור"):
        insert_query = """
            INSERT INTO food_db (food, carb_per_100g, protein_per_100g, fat_per_100g, calories_per_100g)
            VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(insert_query, (f, c, p, fat, cal))
        conn.commit()
        st.success(f"✅ נוסף {f}")
        st.experimental_rerun()

# 📄 הצגת המאגר
st.divider()
st.subheader("📄 מאגר מזון קיים")

if df.empty:
    st.info("📂 המאגר עדיין ריק.")
else:
    st.dataframe(df, use_container_width=True)

    st.divider()
    st.subheader("🗑️ מחיקת פריט מהמאגר")

    option = st.selectbox("בחרי פריט למחיקה:", df["food"].unique())
    if st.button("🗑️ מחק פריט"):
        delete_query = "DELETE FROM food_db WHERE food = %s"
        cur.execute(delete_query, (option,))
        conn.commit()
        st.success(f"🗑️ נמחק {option}")
        st.experimental_rerun()

# סגירת החיבורים
cur.close()
conn.close()
