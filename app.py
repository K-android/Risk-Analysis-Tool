import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from io import BytesIO

def monte_carlo_simulation(material_mean, material_std, labor_mean, labor_std, other_mean, other_std, num_simulations=10000):
    """
    Runs a Monte Carlo simulation to estimate construction costs.
    """
    # Simulate cost variations
    material_costs = np.random.normal(material_mean, material_std, num_simulations)
    labor_costs = np.random.normal(labor_mean, labor_std, num_simulations)
    other_expenses = np.random.normal(other_mean, other_std, num_simulations)
    
    # Total cost
    total_costs = material_costs + labor_costs + other_expenses
    
    # Create DataFrame for exporting
    results_df = pd.DataFrame({
        "Material Costs": material_costs,
        "Labor Costs": labor_costs,
        "Other Expenses": other_expenses,
        "Total Costs": total_costs
    })
    
    return results_df, total_costs

def save_results(results_df):
    """ Saves the simulation results to an Excel file and provides download link. """
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        results_df.to_excel(writer, index=False)
    output.seek(0)
    return output

# Streamlit UI Setup
st.title("Construction Risk & Cost Estimator")

st.sidebar.header("Input Parameters")
material_mean = st.sidebar.number_input("Material Mean Cost", value=100000.0)
material_std = st.sidebar.number_input("Material Std Dev", value=10000.0)
labor_mean = st.sidebar.number_input("Labor Mean Cost", value=50000.0)
labor_std = st.sidebar.number_input("Labor Std Dev", value=5000.0)
other_mean = st.sidebar.number_input("Other Expenses Mean Cost", value=20000.0)
other_std = st.sidebar.number_input("Other Expenses Std Dev", value=2000.0)

if st.sidebar.button("Run Simulation"):
    results_df, total_costs = monte_carlo_simulation(
        material_mean, material_std, labor_mean, labor_std, other_mean, other_std
    )
    
    # Display Statistics
    avg_cost = np.mean(total_costs)
    cost_90 = np.percentile(total_costs, 90)
    cost_99 = np.percentile(total_costs, 99)
    
    st.write(f"### Simulation Results")
    st.write(f"**Average Project Cost:** ₹{avg_cost:,.2f}")
    st.write(f"**90% of Projects Will Cost Below:** ₹{cost_90:,.2f}")
    st.write(f"**99% of Projects Will Cost Below:** ₹{cost_99:,.2f}")
    
    # Plot Histogram
    fig, ax = plt.subplots()
    ax.hist(total_costs, bins=50, color='blue', alpha=0.7)
    ax.axvline(avg_cost, color='red', linestyle='dashed', label="Median Cost")
    ax.axvline(cost_90, color='orange', linestyle='dashed', label="90% Risk Cost")
    ax.set_xlabel("Total Project Cost (₹)")
    ax.set_ylabel("Frequency")
    ax.set_title("Monte Carlo Simulation for Construction Cost Estimation")
    ax.legend()
    st.pyplot(fig)
    
    # Provide Downloadable File
    st.download_button(
        label="Download Simulation Results", 
        data=save_results(results_df), 
        file_name="simulation_results.xlsx", 
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
