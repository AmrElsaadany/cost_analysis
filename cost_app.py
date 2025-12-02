import streamlit as st
import pandas as pd
import numpy as np

# Force sidebar to be expanded by default and set page config
st.set_page_config(page_title="Cost Analysis Application", initial_sidebar_state="expanded", layout="wide")

# 1. Initialize session state
if 'taxes' not in st.session_state:
    st.session_state.taxes = {}
if 'item_costs' not in st.session_state:
    # Initialize the DataFrame with explicit dtypes
    st.session_state.item_costs = pd.DataFrame(
        columns=['item_name', 'base_price', 'individual_overhead']
    ).astype({'item_name': str, 'base_price': np.float64, 'individual_overhead': np.float64})
if 'default_overhead' not in st.session_state:
    st.session_state.default_overhead = 10.0 # Use a float for consistency

st.title("Cost Analysis Application")

# 2. Sidebar for inputs (remains the same)
with st.sidebar:
    st.header("Configuration")

    # Tax Input
    with st.form("tax_form"):
        st.subheader("Add Tax")
        tax_name = st.text_input("Tax Name")
        tax_value = st.number_input("Tax Percentage (%)", min_value=0.0, step=0.1)
        add_tax_button = st.form_submit_button("Save Tax")
        if add_tax_button and tax_name:
            st.session_state.taxes[tax_name] = tax_value
            st.success(f"Added tax '{tax_name}' at {tax_value}%")

    # Display saved taxes
    with st.expander("View Saved Taxes"):
        if st.session_state.taxes:
            for name, value in st.session_state.taxes.items():
                st.write(f"**{name}**: {value}%")
        else:
            st.write("No taxes saved yet.")

    # Default Overhead
    st.subheader("Default Overhead")
    st.session_state.default_overhead = st.number_input("Default Overhead (%)", min_value=0.0, step=0.1, value=st.session_state.default_overhead)

# 3. Main area for item data and results
st.header("Item Price Input")

# Item input using st.data_editor
st.session_state.item_costs = st.data_editor(st.session_state.item_costs, num_rows="dynamic", use_container_width=True, key='editor')

# Calculate button and Vectorized Logic (FIXED SECTION)
if st.button("Calculate Final Prices"):
    df_to_process = st.session_state.item_costs.copy()

    if not df_to_process.empty:
        # CRITICAL FIX: Ensure columns are numeric before calculations and fill NaNs safely
        df_to_process['base_price'] = pd.to_numeric(df_to_process['base_price'], errors='coerce').fillna(0)
        
        # Fill empty individual overheads with the default global overhead value using .fillna() on the Series
        effective_overhead_percent = df_to_process['individual_overhead'].fillna(st.session_state.default_overhead)
        
        # Calculate the total tax multiplier
        total_tax_multiplier = 1.0 + sum(st.session_state.taxes.values()) / 100.0

        # Perform the final calculation using vectorized operations (no loop needed)
        # Final Price = base_price * (total_tax_multiplier + (effective_overhead_percent / 100.0))
        df_to_process['final_price'] = df_to_process['base_price'] * (total_tax_multiplier + (effective_overhead_percent / 100.0))
        
        # Store results for persistent display
        st.session_state.final_results = df_to_process
        
    else:
        st.warning("Please add some items to the table before calculating.")

# Display final results persistently if they exist in session state, even after reruns
if 'final_results' in st.session_state and not st.session_state.final_results.empty:
    st.subheader("Final Cost Analysis")
    st.dataframe(st.session_state.final_results, use_container_width=True)
