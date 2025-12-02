import streamlit as st
import pandas as pd
import numpy as np

# Force sidebar to be expanded by default and set page config
st.set_page_config(page_title="Cost Analysis Application", initial_sidebar_state="expanded", layout="wide")

# 1. Initialize session state (Modified part from previous answer)
if 'taxes' not in st.session_state:
    st.session_state.taxes = {}
if 'item_costs' not in st.session_state:
    # Initialize the DataFrame with explicit dtypes to prevent mixed-type errors
    st.session_state.item_costs = pd.DataFrame(
        columns=['item_name', 'base_price', 'individual_overhead']
    ).astype({'item_name': str, 'base_price': np.float64, 'individual_overhead': np.float64})
if 'default_overhead' not in st.session_state:
    st.session_state.default_overhead = 10.0 # Use a float for consistency

st.title("Cost Analysis Application")

# 2. Sidebar for inputs
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

# Item input using st.data_editor - This updates session_state automatically upon edit
st.session_state.item_costs = st.data_editor(st.session_state.item_costs, num_rows="dynamic", use_container_width=True, key='editor')

# Calculate button
if st.button("Calculate Final Prices"):
    # This block executes when the button is clicked
    df_to_process = st.session_state.item_costs.copy()

    # CRITICAL FIX: Ensure all relevant columns are numeric before calculation
    try:
        df_to_process['base_price'] = pd.to_numeric(df_to_process['base_price'], errors='coerce').fillna(0)
        df_to_process['individual_overhead'] = pd.to_numeric(df_to_process['individual_overhead'], errors='coerce')
    except ValueError as e:
        st.error(f"Error converting prices to numbers: {e}")
        st.stop()

    if not df_to_process.empty:
        # Calculate combined tax multiplier
        total_tax_multiplier = 1.0 + sum(st.session_state.taxes.values()) / 100.0

        # Apply calculations
        final_prices = []
        for index, row in df_to_process.iterrows():
            item_price = row['base_price']
            
            # Determine overhead for the item (use default if individual is NaN/None)
            # .fillna() handles cases where the user left the individual overhead field empty
            overhead_rate = row['individual_overhead'].fillna(st.session_state.default_overhead) / 100.0
            
            # Final price calculation: base_price * (1 + total_tax_rate + overhead_rate)
            final_price = item_price * (total_tax_multiplier + overhead_rate)
            final_prices.append(final_price)

        # Update the dataframe in session state used for display
        st.session_state.final_results = df_to_process
        st.session_state.final_results['final_price'] = final_prices
        
        # Display results below
        st.subheader("Final Cost Analysis")
        # Use a new key for the final results dataframe to ensure it updates
        st.dataframe(st.session_state.final_results, use_container_width=True)

    else:
        st.warning("Please add some items to the table before calculating.")

# Display final results persistently if they exist in session state, even after reruns
if 'final_results' in st.session_state and not st.session_state.final_results.empty:
    st.subheader("Final Cost Analysis")
    st.dataframe(st.session_state.final_results, use_container_width=True)
