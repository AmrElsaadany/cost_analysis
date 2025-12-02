import streamlit as st
import pandas as pd

# 1. Initialize session state
if 'taxes' not in st.session_state:
    st.session_state.taxes = {}
if 'item_costs' not in st.session_state:
    st.session_state.item_costs = pd.DataFrame(columns=['item_name', 'base_price', 'individual_overhead'])
if 'default_overhead' not in st.session_state:
    st.session_state.default_overhead = 10 # Default overhead in percent

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

# Item input using st.data_editor
st.session_state.item_costs = st.data_editor(st.session_state.item_costs, num_rows="dynamic", use_container_width=True)

# Calculate button
if st.button("Calculate Final Prices"):
    if not st.session_state.item_costs.empty:
        # Create a copy to store results
        results_df = st.session_state.item_costs.copy()

        # Calculate combined tax multiplier
        total_tax_multiplier = 1.0 + sum(st.session_state.taxes.values()) / 100.0

        # Apply calculations
        final_prices = []
        for index, row in results_df.iterrows():
            item_price = row['base_price']
            
            # Determine overhead for the item (individual or default)
            overhead_rate = row.get('individual_overhead', st.session_state.default_overhead) / 100.0
            
            # Final price calculation: base_price * (1 + total_tax_rate + overhead_rate)
            final_price = item_price * (total_tax_multiplier + overhead_rate)
            final_prices.append(final_price)

        results_df['final_price'] = final_prices
        
        st.subheader("Final Cost Analysis")
        st.dataframe(results_df)
    else:
        st.warning("Please add some items to the table before calculating.")

