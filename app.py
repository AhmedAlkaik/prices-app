import streamlit as st
import pandas as pd

# Configure mobile-friendly page layout
st.set_page_config(page_title="البحث عن أسعار العدسات", page_icon="👓", layout="centered")

@st.cache_data
def load_data():
    # utf-8-sig removes hidden Windows BOM characters
    # sep="," forces it to ignore Excel's regional settings
    df = pd.read_csv("prices.csv", encoding="utf-8-sig", sep=",")
    
    # Strip any accidental invisible spaces from the column headers
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# Custom CSS to ensure right-to-left alignment for Arabic text
st.markdown("""
    <style>
        .block-container {
            direction: rtl;
            text-align: right;
        }
    </style>
""", unsafe_allow_html=True)

st.title("👓 نظارات مستر بلو - أسعار العدسات")
st.markdown("اختر نوع العدسة وأدخل مقاسات SPH و CYL بدقة.")

# Section 1: Lens Selection
st.subheader("1. مواصفات العدسة")
col1, col2 = st.columns(2)

with col1:
    categories = df['Lens_Category'].unique()
    selected_category = st.selectbox("الفئة", categories)

with col2:
    filtered_lenses = df[df['Lens_Category'] == selected_category]['Lens_Name'].unique()
    selected_lens = st.selectbox("اسم العدسة", filtered_lenses)

st.divider()

# Section 2: Prescription Inputs
st.subheader("2. مقاسات الكشف")
col3, col4 = st.columns(2)

with col3:
    sph_input = st.number_input("SPH (الكروي)", min_value=-24.00, max_value=20.00, value=0.00, step=0.25, format="%.2f")

with col4:
    cyl_input = st.number_input("CYL (الأسطواني)", min_value=-8.00, max_value=8.00, value=0.00, step=0.25, format="%.2f")

st.divider()

# Section 3: Engine & Output
if st.button("ابحث عن السعر", type="primary", use_container_width=True):
    # Filter the dataframe for the specific lens and power boundaries
    match = df[
        (df['Lens_Name'] == selected_lens) & 
        (df['SPH_Lower'] <= sph_input) & (df['SPH_Upper'] >= sph_input) &
        (df['CYL_Lower'] <= cyl_input) & (df['CYL_Upper'] >= cyl_input)
    ]
    
    if not match.empty:
        # Extract the matched data
        price = match['Price'].iloc[0]
        diameter = match['Diameter'].iloc[0]
        
        st.success("✅ متاح")
        
        # Display large metric cards for easy reading on the shop floor
        m_col1, m_col2 = st.columns(2)
        m_col1.metric(label="سعر الجملة", value=f"{int(price)} EGP")
        m_col2.metric(label="قطر العدسة", value=f"{int(diameter)} mm")
        
    else:
        st.error("⚠️ خارج المخزون")
