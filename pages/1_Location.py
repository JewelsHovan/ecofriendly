import streamlit as st
from utilis_location import *

def main():
    st.set_page_config(page_title="Eco Emissions Location Dashboard", page_icon="🌿", layout="wide")
    st.title("Location-Based Emissions Analysis")

    data = load_data('Processed_Unit.csv')

    st.sidebar.header("Filter Options")
    state = st.sidebar.text_input("State", "")
    city = st.sidebar.text_input("City", "")

    filtered_data = filter_data(data, city, state)

    if not filtered_data.empty:
        # First row of visualizations
        col1, col2 = st.columns(2)
        with col1:
            plot_co2_emissions_by_year(filtered_data)
        with col2:
            plot_emissions_distribution(filtered_data)

        # Second row of visualizations
        col3, col4 = st.columns(2)
        with col3:
            plot_emissions_by_sector(filtered_data)
        with col4:
            plot_dynamic_scatter(filtered_data)
    else:
        st.write("No data available for the selected filters.")

if __name__ == "__main__":
    main()
