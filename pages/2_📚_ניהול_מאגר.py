import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="📚 ניהול מאגר")

st.header("📚 ניהול מאגר מזונות")
FOODS_FILE = "food_db.csv"

if os.path.exists(FOODS_FILE):
    df = pd.read_csv(FOODS_FILE)
else:
    df = pd.DataFrame(columns=["Food","Carb_per_100g","Protein_per_100g","Fat_per_100g"])
    df.to_csv(FOODS_FILE, index=False)

# הוספה
with st.form("add_food"):
    st.subheader("➕ הוסף מזון")
    f = st.text_input("שם")
    c = st.number_input("פחמימה/100 גרם", 0.0)
    p = st.number_input("חלבון/100 גרם", 0.0)
    fat = st.number_input("שומן/100 גרם", 0.0)
    if st.form_submit_button("שמור"):
        df = pd.concat([df, pd.DataFrame([[f,c,p,fat]], columns=df.columns)], ignore_index=True)
        df.to_csv(FOODS_FILE, index=False)
        st.success(f"נוסף {f}")

# עריכה
if not df.empty:
    st.subheader("✏️ ערוך מזון")
    option = st.selectbox("בחר:", df["Food"].unique())
    row = df[df["Food"]==option].iloc[0]
    c = st.number_input("פחמימה", 0.0, value=row["Carb_per_100g"])
    p = st.number_input("חלבון", 0.0, value=row["Protein_per_100g"])
    fat = st.number_input("שומן", 0.0, value=row["Fat_per_100g"])
    if st.button("עדכן"):
        df.loc[df["Food"]==option, ["Carb_per_100g","Protein_per_100g","Fat_per_100g"]] = [c,p,fat]
        df.to_csv(FOODS_FILE, index=False)
        st.success(f"עודכן {option}")
    if st.button("מחק"):
        df = df[df["Food"]!=option]
        df.to_csv(FOODS_FILE, index=False)
        st.success(f"נמחק {option}")

st.dataframe(df)
