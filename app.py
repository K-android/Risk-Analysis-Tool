import streamlit as st
st.set_page_config(page_title="Construction Risk & Cost Estimator", layout="wide")

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import requests
from io import BytesIO

# Function to fetch real-time construction material costs
def fetch_material_prices():
    api_url = "https://api.example.com/construction-costs"  # Replace with actual API
    try:
        response = requests.get(api_url)
        data = response.json()
        return {
            "cement": data.get("cement", 500),
            "steel": data.get("steel", 60000),
            "sand": data.get("sand", 1200),
            "bricks": data.get("bricks", 8)
        }
    except Exception as e:
        st.warning("⚠️ Failed to fetch real-time data. Using default values.")
        return {"cement": 500, "steel": 60000, "sand": 1200, "bricks": 8}

def fetch_labor_rates():
    api_url = "https://api.example.com/labor-costs"  # Replace with actual API
    try:
        response = requests.get(api_url)
        data = response.json()
        return data.get("average_labor_cost", 500)
    except Exception as e:
        st.warning("⚠️ Failed to fetch real-time labor costs. Using default values.")
        return 500

def fetch_weather_forecast():
    api_url = "https://api.weather.com/construction-forecast"  # Replace with actual API
    try:
        response = requests.get(api_url)
        data = response.json()
        return data.get("forecast", "No recent weather updates.")
    except Exception as e:
        st.warning("⚠️ Failed to fetch weather forecast data.")
        return "No recent weather updates."

def fetch_regulatory_data():
    api_url = "https://api.example.com/construction-regulations"  # Replace with actual API
    try:
        response = requests.get(api_url)
        data = response.json()
        return data.get("regulatory_updates", "No recent updates.")
    except Exception as e:
        st.warning("⚠️ Failed to fetch regulatory data.")
        return "No recent updates."

def fetch_legal_risks():
    api_url = "https://api.example.com/legal-risk-analysis"  # Replace with actual API
    try:
        response = requests.get(api_url)
        data = response.json()
        return data.get("legal_risks", "No legal risks detected.")
    except Exception as e:
        st.warning("⚠️ Failed to fetch legal risk data.")
        return "No legal risks detected."

def ai_cost_estimation(material_cost, labor_cost, other_cost, inflation_rate, delay_risk):
    risk_factor = 1 + (inflation_rate / 100) + (delay_risk / 100)
    return (material_cost + labor_cost + other_cost) * risk_factor

def monte_carlo_simulation(material_mean, material_std, labor_mean, labor_std, other_mean, other_std, inflation_rate, delay_risk, interest_rate, equipment_cost, overhead_cost, num_simulations=10000):
    material_costs = np.random.triangular(material_mean - material_std, material_mean, material_mean + material_std, num_simulations)
    labor_costs = np.random.triangular(labor_mean - labor_std, labor_mean, labor_mean + labor_std, num_simulations)
    other_expenses = np.random.triangular(other_mean - other_std, other_mean, other_mean + other_std, num_simulations)
    
    total_costs = material_costs + labor_costs + other_expenses + equipment_cost + overhead_cost
    
    inflation_factor = 1 + (inflation_rate / 100)
    delay_factor = 1 + (delay_risk / 100)
    interest_factor = 1 + (interest_rate / 100)
    total_costs *= (inflation_factor * delay_factor * interest_factor)
    
    results_df = pd.DataFrame({
        "Material Costs": material_costs,
        "Labor Costs": labor_costs,
        "Other Expenses": other_expenses,
        "Equipment Costs": equipment_cost,
        "Overhead Costs": overhead_cost,
        "Total Costs": total_costs
    })
    
    return results_df, total_costs

real_time_prices = fetch_material_prices()
real_time_labor = fetch_labor_rates()
regulatory_updates = fetch_regulatory_data()
weather_forecast = fetch_weather_forecast()
legal_risks = fetch_legal_risks()

def save_results(results_df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        results_df.to_excel(writer, index=False)
    output.seek(0)
    return output

st.title("🏗️ Construction Risk & Cost Estimator")
st.markdown("---")

st.sidebar.header("🔧 Input Parameters")
st.sidebar.subheader("📌 Real-Time Costs")
st.sidebar.write(f"🧱 Cement: ₹{real_time_prices['cement']} per bag")
st.sidebar.write(f"🔩 Steel: ₹{real_time_prices['steel']} per ton")
st.sidebar.write(f"🏖️ Sand: ₹{real_time_prices['sand']} per cubic meter")
st.sidebar.write(f"🧱 Bricks: ₹{real_time_prices['bricks']} per unit")
st.sidebar.write(f"👷 Labor Cost: ₹{real_time_labor} per hour")

st.sidebar.subheader("🌤️ Weather Forecast")
st.sidebar.write(weather_forecast)

st.sidebar.subheader("📜 Regulatory Updates")
st.sidebar.write(regulatory_updates)

st.sidebar.subheader("⚖️ Legal Risk Analysis")
st.sidebar.write(legal_risks)

material_cost = st.sidebar.number_input("Material Cost (₹)", value=real_time_prices['cement']*100)
labor_cost = st.sidebar.number_input("Labor Cost (₹)", value=real_time_labor*1000)
other_cost = st.sidebar.number_input("Other Expenses (₹)", value=50000)
inflation_rate = st.sidebar.slider("Expected Inflation Rate (%)", 0, 20, 5)
delay_risk = st.sidebar.slider("Expected Delay Impact (%)", 0, 30, 10)

st.sidebar.markdown("---")
run_simulation = st.sidebar.button("▶️ Run Simulation")

if run_simulation:
    results_df, total_costs = monte_carlo_simulation(material_cost, 10000, labor_cost, 5000, other_cost, 2000, inflation_rate, delay_risk, 5, 20000, 50000)
    
    st.subheader("📊 Cost Distribution")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(total_costs, bins=50, kde=True, color='blue', alpha=0.7)
    ax.set_xlabel("Total Project Cost (₹)")
    ax.set_ylabel("Frequency")
    ax.set_title("Monte Carlo Simulation for Cost Estimation")
    st.pyplot(fig)
    
    st.subheader("📈 Cost Breakdown")
    st.bar_chart(results_df.mean())
    
    st.download_button(
        label="📥 Download Simulation Results", 
        data=save_results(results_df), 
        file_name="simulation_results.xlsx", 
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

