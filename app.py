import streamlit as st
import pandas as pd

# Configure mobile-friendly page layout
st.set_page_config(page_title="Lens Price Lookup", page_icon="👓", layout="centered")

@st.cache_data
def load_data():
    # Load the mapped pricing database
    return pd.read_csv("prices.csv")

df = load_data()

st.title("👓 Mr. Blue Optical - Lens Lookup")
st.markdown("Select the lens type and enter the exact SPH and CYL prescription powers.")

# Section 1: Lens Selection
st.subheader("1. Lens Specification")
col1, col2 = st.columns(2)

with col1:
    categories = df['Lens_Category'].unique()
    selected_category = st.selectbox("Category", categories)

with col2:
    filtered_lenses = df[df['Lens_Category'] == selected_category]['Lens_Name'].unique()
    selected_lens = st.selectbox("Lens Name", filtered_lenses)

st.divider()

# Section 2: Prescription Inputs
st.subheader("2. Prescription Powers")
col3, col4 = st.columns(2)

with col3:
    sph_input = st.number_input("SPH (Sphere)", min_value=-24.00, max_value=20.00, value=0.00, step=0.25, format="%.2f")

with col4:
    cyl_input = st.number_input("CYL (Cylinder)", min_value=-8.00, max_value=8.00, value=0.00, step=0.25, format="%.2f")

st.divider()

# Section 3: Engine & Output
if st.button("Lookup Price", type="primary", use_container_width=True):
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
        
        st.success("✅ Match Found")
        
        # Display large metric cards for easy reading on the shop floor
        m_col1, m_col2 = st.columns(2)
        m_col1.metric(label="Wholesale Price", value=f"{int(price)} EGP")
        m_col2.metric(label="Blank Diameter", value=f"{int(diameter)} mm")
        
    else:
        st.error("⚠️ No price found for this specific combination.")
        st.info("Check if the powers exceed the manufacturer's standard ranges or if a specialized surfacing order is required.")