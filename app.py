import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import streamlit as st
from io import BytesIO

def monte_carlo_simulation(material_mean, material_std, labor_mean, labor_std, other_mean, other_std, inflation_rate, delay_risk, num_simulations=10000):
    """
    Runs a Monte Carlo simulation to estimate construction costs using Triangular Distribution for better accuracy.
    """
    material_costs = np.random.triangular(material_mean - material_std, material_mean, material_mean + material_std, num_simulations)
    labor_costs = np.random.triangular(labor_mean - labor_std, labor_mean, labor_mean + labor_std, num_simulations)
    other_expenses = np.random.triangular(other_mean - other_std, other_mean, other_mean + other_std, num_simulations)
    
    total_costs = material_costs + labor_costs + other_expenses
    
    # Adjusting for inflation and delay risks
    inflation_factor = 1 + (inflation_rate / 100)
    delay_factor = 1 + (delay_risk / 100)
    total_costs *= (inflation_factor * delay_factor)
    
    results_df = pd.DataFrame({
        "Material Costs": material_costs,
        "Labor Costs": labor_costs,
        "Other Expenses": other_expenses,
        "Total Costs": total_costs
    })
    
    return results_df, total_costs

def save_results(results_df):
    """ Saves the simulation results to an Excel file and provides a download link. """
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        results_df.to_excel(writer, index=False)
    output.seek(0)
    return output

def load_past_reports():
    """ Loads past construction reports from a CSV file """
    try:
        return pd.read_csv("past_reports.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["Project Name", "Total Cost", "Completion Time", "Major Risks"])

# Streamlit UI Setup
st.title("Construction Risk & Cost Estimator")
st.sidebar.header("Input Parameters")

material_mean = st.sidebar.slider("Material Mean Cost (₹)", 50000, 500000, 100000)
material_std = st.sidebar.slider("Material Std Dev (₹)", 5000, 50000, 10000)
labor_mean = st.sidebar.slider("Labor Mean Cost (₹)", 20000, 200000, 50000)
labor_std = st.sidebar.slider("Labor Std Dev (₹)", 2000, 20000, 5000)
other_mean = st.sidebar.slider("Other Expenses Mean Cost (₹)", 10000, 100000, 20000)
other_std = st.sidebar.slider("Other Expenses Std Dev (₹)", 1000, 10000, 2000)
inflation_rate = st.sidebar.slider("Expected Inflation Rate (%)", 0, 20, 5)
delay_risk = st.sidebar.slider("Expected Delay Impact (%)", 0, 30, 10)

if st.sidebar.button("Run Simulation"):
    results_df, total_costs = monte_carlo_simulation(
        material_mean, material_std, labor_mean, labor_std, other_mean, other_std, inflation_rate, delay_risk
    )
    
    avg_cost = np.mean(total_costs)
    cost_90 = np.percentile(total_costs, 90)
    cost_99 = np.percentile(total_costs, 99)
    
    st.write("### Simulation Results")
    st.write(f"**Average Project Cost:** ₹{avg_cost:,.2f}")
    st.write(f"**90% of Projects Will Cost Below:** ₹{cost_90:,.2f}")
    st.write(f"**99% of Projects Will Cost Below:** ₹{cost_99:,.2f}")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(total_costs, bins=50, kde=True, color='blue', alpha=0.7)
    ax.axvline(avg_cost, color='red', linestyle='dashed', label="Median Cost")
    ax.axvline(cost_90, color='orange', linestyle='dashed', label="90% Risk Cost")
    ax.set_xlabel("Total Project Cost (₹)")
    ax.set_ylabel("Frequency")
    ax.set_title("Monte Carlo Simulation for Construction Cost Estimation")
    ax.legend()
    st.pyplot(fig)
    
    # Sensitivity Analysis (Which cost affects the total cost the most)
    corr = results_df.corr()["Total Costs"].drop("Total Costs")
    st.write("### Sensitivity Analysis")
    st.bar_chart(corr)
    
    # Provide Downloadable File
    st.download_button(
        label="Download Simulation Results", 
        data=save_results(results_df), 
        file_name="simulation_results.xlsx", 
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Past Construction Reports Page
st.sidebar.header("View Past Reports")
if st.sidebar.button("Load Past Reports"):
    past_reports = load_past_reports()
    st.write("### Past Construction Reports")
    st.dataframe(past_reports)
    
    if st.sidebar.button("Export Past Reports"):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            past_reports.to_excel(writer, index=False)
        output.seek(0)
        st.download_button("Download Past Reports", data=output, file_name="past_reports.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

