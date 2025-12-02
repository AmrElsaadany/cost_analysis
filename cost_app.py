import streamlit as st
import pandas as pd
import numpy as np # Import numpy

# ... (st.title and sidebar code remains the same) ...

# 1. Initialize session state (Modified part)
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

# ... (Sidebar code remains the same) ...

# 3. Main area for item data and results
st.header("Item Price Input")

# Item input using st.data_editor
# The editor will now handle consistent data types correctly
st.session_state.item_costs = st.data_editor(st.session_state.item_costs, num_rows="dynamic", use_container_width=True)

# ... (Calculate button logic remains the same) ...

