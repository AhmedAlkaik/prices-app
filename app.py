import streamlit as st
import pandas as pd

# Mobile-optimized configuration
st.set_page_config(page_title="تسعير عدسات النظارات", page_icon="👓", layout="centered")

@st.cache_data
def load_data():
    # Load CSV safely
    df = pd.read_csv("prices.csv", encoding="utf-8-sig", sep=",")
    df.columns = df.columns.str.strip()
    
    # 1. HUMAN LOGIC: Classify every row in the CSV into its specific Sign Table
    def assign_sign_table(row):
        sph_l, sph_u = row['SPH_Lower'], row['SPH_Upper']
        cyl_l, cyl_u = row['CYL_Lower'], row['CYL_Upper']
        
        if sph_u <= 0 and cyl_u <= 0:
            return "-/-"
        elif sph_l >= 0 and cyl_l >= 0:
            return "+/+"
        elif sph_l >= 0 and cyl_u <= 0:
            return "+/-"
        return "Mixed"
        
    df['Sign_Table'] = df.apply(assign_sign_table, axis=1)
    return df

df = load_data()

# RTL layout styling for Arabic interface
st.markdown("""
    <style>
        .block-container {
            direction: rtl;
            text-align: right;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.4rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("👓 حاسبة أسعار العدسات")
st.caption("احسب سعر العدسة الفردية أو الزوج بالكامل بدقة.")

# Helper function using Human Search Logic
def get_lens_quote(lens_name, sph, cyl):
    transposed_msg = ""
    
    # 2. OPTICAL TRANSPOSITION: If prescription is (-/+) we convert to (-/-)
    if sph < 0 and cyl > 0:
        sph = sph + cyl
        cyl = -cyl
        transposed_msg = f" (تم تحويل المقاس إلى SPH {sph:.2f} / CYL {cyl:.2f})"
        
    # 3. IDENTIFY TARGET TABLE (+/+, -/-, +/-)
    if sph >= 0 and cyl >= 0:
        target_table = "+/+"
    elif sph <= 0 and cyl <= 0:
        target_table = "-/-"
    elif sph > 0 and cyl < 0:
        target_table = "+/-"
    else:
        target_table = "Mixed"
        
    # 4. FILTER: Go to Table -> Find CYL bounds -> Find SPH bounds
    match = df[
        (df['Lens_Name'] == lens_name) & 
        (df['Sign_Table'] == target_table) &
        (df['CYL_Lower'] <= cyl) & (df['CYL_Upper'] >= cyl) &
        (df['SPH_Lower'] <= sph) & (df['SPH_Upper'] >= sph)
    ]
    
    if not match.empty:
        pair_price = float(match['Price'].iloc[0])
        single_price = pair_price / 2.0
        diameter = match['Diameter'].iloc[0]
        availability = match['Availability'].iloc[0] if 'Availability' in match.columns else "غير محدد"
        
        return {
            "available": True,
            "single_price": single_price,
            "pair_price": pair_price,
            "diameter": diameter,
            "availability": availability,
            "transposed_msg": transposed_msg
        }
    return {"available": False, "transposed_msg": transposed_msg}

categories = sorted(df['Lens_Category'].dropna().unique())

# ----------------- العدسة الأولى (R / OD) -----------------
st.subheader("1. العدسة الأولى (العين اليمنى / R)")
col1, col2 = st.columns(2)
with col1:
    cat_1 = st.selectbox("الفئة", categories, key="cat_1")
with col2:
    lenses_1 = df[df['Lens_Category'] == cat_1]['Lens_Name'].unique()
    lens_1 = st.selectbox("اسم العدسة", lenses_1, key="lens_1")

col3, col4 = st.columns(2)
with col3:
    sph_1 = st.number_input("SPH (الكروي)", min_value=-24.00, max_value=20.00, value=0.00, step=0.25, format="%.2f", key="sph_1")
with col4:
    cyl_1 = st.number_input("CYL (الأسطواني)", min_value=-8.00, max_value=8.00, value=0.00, step=0.25, format="%.2f", key="cyl_1")

# ----------------- العدسة الثانية (L / OS) -----------------
st.divider()
has_second_lens = st.toggle("إضافة العدسة الثانية (العين اليسرى / L)", value=True)

cat_2, lens_2, sph_2, cyl_2 = None, None, None, None

if has_second_lens:
    same_type = st.checkbox("نفس نوع وخامة العدسة الأولى", value=True)
    
    col5, col6 = st.columns(2)
    if same_type:
        cat_2 = cat_1
        lens_2 = lens_1
        with col5:
            st.info(f"الفئة: {cat_2}")
        with col6:
            st.info(f"النوع: {lens_2}")
    else:
        with col5:
            cat_2 = st.selectbox("الفئة (العين اليسرى)", categories, key="cat_2")
        with col6:
            lenses_2 = df[df['Lens_Category'] == cat_2]['Lens_Name'].unique()
            lens_2 = st.selectbox("اسم العدسة (العين اليسرى)", lenses_2, key="lens_2")

    col7, col8 = st.columns(2)
    with col7:
        sph_2 = st.number_input("SPH (الكروي)", min_value=-24.00, max_value=20.00, value=0.00, step=0.25, format="%.2f", key="sph_2")
    with col8:
        cyl_2 = st.number_input("CYL (الأسطواني)", min_value=-8.00, max_value=8.00, value=0.00, step=0.25, format="%.2f", key="cyl_2")

st.divider()

# ----------------- حساب السعر الإجمالي -----------------
if st.button("احسب السعر", type="primary", use_container_width=True):
    res_1 = get_lens_quote(lens_1, sph_1, cyl_1)
    
    st.markdown("### تفاصيل التكلفة:")
    
    # Check First Lens
    if res_1["available"]:
        st.success(f"العدسة الأولى: مقاس متاح {res_1['transposed_msg']}")
        m1_col1, m1_col2, m1_col3 = st.columns(3)
        m1_col1.metric(label="سعر فردي", value=f"{res_1['single_price']:.1f} EGP")
        m1_col2.metric(label="القطر", value=f"{int(res_1['diameter'])} mm")
        m1_col3.metric(label="التوافر", value=str(res_1['availability']))
    else:
        st.error(f"العدسة الأولى: ⚠️ خارج المخزون / غير متاحة في الجدول {res_1['transposed_msg']}")
        
    # Check Second Lens if enabled
    if has_second_lens:
        res_2 = get_lens_quote(lens_2, sph_2, cyl_2)
        if res_2["available"]:
            st.success(f"العدسة الثانية: مقاس متاح {res_2['transposed_msg']}")
            m2_col1, m2_col2, m2_col3 = st.columns(3)
            m2_col1.metric(label="سعر فردي", value=f"{res_2['single_price']:.1f} EGP")
            m2_col2.metric(label="القطر", value=f"{int(res_2['diameter'])} mm")
            m2_col3.metric(label="التوافر", value=str(res_2['availability']))
        else:
            st.error(f"العدسة الثانية: ⚠️ خارج المخزون / غير متاحة في الجدول {res_2['transposed_msg']}")
            
        # Display Total Pair Price if both or either are available
        if res_1["available"] and res_2["available"]:
            total_pair = res_1['single_price'] + res_2['single_price']
            st.markdown("---")
            st.metric(label="إجمالي سعر الزوج (عدستين)", value=f"{total_pair:.0f} EGP")
    else:
        if res_1["available"]:
            st.caption(f"سعر الزوج الكامل من هذا المقاس: {res_1['pair_price']:.0f} EGP")
