import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import streamlit as st
import requests
from io import BytesIO

# Function to fetch real-time construction material costs
def fetch_material_prices():
    api_url = "https://api.example.com/construction-costs"  # Replace with actual API
    try:
        response = requests.get(api_url)
        data = response.json()
        return {
            "cement": data.get("cement", 500),  # Default value if not found
            "steel": data.get("steel", 60000),
            "sand": data.get("sand", 1200),
            "bricks": data.get("bricks", 8)
        }
    except Exception as e:
        st.warning("⚠️ Failed to fetch real-time data. Using default values.")
        return {"cement": 500, "steel": 60000, "sand": 1200, "bricks": 8}

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

# Fetch real-time material costs
real_time_prices = fetch_material_prices()

def save_results(results_df):
    """ Saves the simulation results to an Excel file and provides a download link. """
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        results_df.to_excel(writer, index=False)
    output.seek(0)
    return output

# Streamlit UI Setup
st.set_page_config(page_title="Construction Risk & Cost Estimator", layout="wide")
st.title("🏗️ Construction Risk & Cost Estimator")
st.markdown("---")

# Sidebar for Inputs
st.sidebar.header("🔧 Input Parameters")

st.sidebar.subheader("📌 Real-Time Material Costs")
st.sidebar.write(f"🧱 Cement: ₹{real_time_prices['cement']} per bag")
st.sidebar.write(f"🔩 Steel: ₹{real_time_prices['steel']} per ton")
st.sidebar.write(f"🏖️ Sand: ₹{real_time_prices['sand']} per cubic meter")
st.sidebar.write(f"🧱 Bricks: ₹{real_time_prices['bricks']} per unit")

material_mean = st.sidebar.slider("Material Mean Cost (₹)", 50000, 500000, 100000)
material_std = st.sidebar.slider("Material Std Dev (₹)", 5000, 50000, 10000)
labor_mean = st.sidebar.slider("Labor Mean Cost (₹)", 20000, 200000, 50000)
labor_std = st.sidebar.slider("Labor Std Dev (₹)", 2000, 20000, 5000)
other_mean = st.sidebar.slider("Other Expenses Mean Cost (₹)", 10000, 100000, 20000)
other_std = st.sidebar.slider("Other Expenses Std Dev (₹)", 1000, 10000, 2000)
inflation_rate = st.sidebar.slider("Expected Inflation Rate (%)", 0, 20, 5)
delay_risk = st.sidebar.slider("Expected Delay Impact (%)", 0, 30, 10)

st.sidebar.markdown("---")
run_simulation = st.sidebar.button("▶️ Run Simulation")

if run_simulation:
    results_df, total_costs = monte_carlo_simulation(
        material_mean, material_std, labor_mean, labor_std, other_mean, other_std, inflation_rate, delay_risk
    )
    
    avg_cost = np.mean(total_costs)
    cost_90 = np.percentile(total_costs, 90)
    cost_99 = np.percentile(total_costs, 99)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="📊 Average Project Cost", value=f"₹{avg_cost:,.2f}")
        st.metric(label="🔶 90% of Projects Cost Below", value=f"₹{cost_90:,.2f}")
        st.metric(label="🔴 99% of Projects Cost Below", value=f"₹{cost_99:,.2f}")
    
    with col2:
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.histplot(total_costs, bins=50, kde=True, color='blue', alpha=0.7)
        ax.axvline(avg_cost, color='red', linestyle='dashed', label="Median Cost")
        ax.axvline(cost_90, color='orange', linestyle='dashed', label="90% Risk Cost")
        ax.set_xlabel("Total Project Cost (₹)")
        ax.set_ylabel("Frequency")
        ax.set_title("Monte Carlo Simulation for Construction Cost Estimation")
        ax.legend()
        st.pyplot(fig)
    
    st.markdown("---")
    st.subheader("📌 Sensitivity Analysis")
    corr = results_df.corr()["Total Costs"].drop("Total Costs")
    st.bar_chart(corr)
    
    st.download_button(
        label="📥 Download Simulation Results", 
        data=save_results(results_df), 
        file_name="simulation_results.xlsx", 
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
