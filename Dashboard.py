import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px  # Import Plotly Express


# Function to load data
def load_data():
    data = pd.read_csv('Processed_Unit.csv')
    return data

# Main app function
def run():
    st.set_page_config(page_title="Eco Emissions Dashboard", page_icon="🌿", layout="wide")
    st.title("Eco Emissions Dashboard 🌿")

    # Load the data
    data = load_data()
    all_data = data.copy()

    # Sidebar - User Input Features with descriptive labels
    st.sidebar.header('User Input Features')
    default_company_name = 'ABBVIE LTD.'
    company_name = st.sidebar.text_input('Company Name', value=default_company_name)
    date_range = st.sidebar.slider('Select a date range', 2010, 2022, (2010, 2022))
    emission_type = st.sidebar.selectbox('Select emission type', ['CO2', 'CH4', 'N2O'])

    # Filtering data based on user input
    if company_name:
        data = data[data['Facility.Name'].str.contains(company_name, case=False, na=False)]
    data = data[(data['Year'] >= date_range[0]) & (data['Year'] <= date_range[1])]
    emission_col = f'{emission_type}_emissions'  # Adjusted to match the column name exactly
    filtered_data = data[['Facility.Name', 'Sector', 'Year', emission_col]]

    # Pivot the filtered_data DataFrame
    pivoted_data = filtered_data.pivot_table(index=['Facility.Name', 'Sector'], 
                                             columns='Year', 
                                             values=emission_col, 
                                             fill_value=0)

    # First row for the pivoted table
    st.write("## Filtered Data")
    st.dataframe(pivoted_data)

    # Additional Step: Filter data for companies in the same sector as the selected company
    selected_company_sector = data.loc[data['Facility.Name'].str.contains(company_name, case=False, na=False), 'Sector'].iloc[0]
    sector_data = all_data[all_data['Sector'] == selected_company_sector]

    # Aggregate total emissions for each company in the sector
    total_emissions_by_company = sector_data.groupby('Facility.Name')[emission_col].sum().sort_values(ascending=False)

    # Check if the selected company is in the dataset and its position
    selected_company_emissions = total_emissions_by_company[total_emissions_by_company.index.str.contains(company_name, case=False)]

    # If the selected company is not in the top 10, include it separately for comparison
    if selected_company_emissions.empty:
        top_companies = total_emissions_by_company.head(10)
    else:
        # Use pd.concat instead of append to combine Series
        top_companies = pd.concat([total_emissions_by_company.head(10), selected_company_emissions]).drop_duplicates()

    # Convert the Series to a DataFrame for Plotly
    top_companies_df = top_companies.reset_index()
    top_companies_df.columns = ['Facility.Name', emission_col]

    # Ensure the selected company is highlighted in the DataFrame
    top_companies_df['Highlight'] = top_companies_df['Facility.Name'].apply(lambda x: 'Selected Company' if x == company_name else 'Other Companies')

    # Second row with three metrics in columns
    col1, col2, col3 = st.columns(3)
    with col1:
        total_emissions = data[emission_col].sum()
        st.metric(label="Total Emissions", value=f"{total_emissions:.2f}")
    with col2:
        max_emissions_year = data.loc[data[emission_col].idxmax(), 'Year']
        max_emissions_value = data[emission_col].max()
        st.metric(label="Year with Highest Emissions", value=f"{max_emissions_year}", delta=f"{max_emissions_value:.2f}")
    with col3:
        avg_annual_increase = data[emission_col].diff().mean()
        st.metric(label="Average Annual Increase in Emissions", value=f"{avg_annual_increase:.2f}")

    # Third row for the line chart
    emission_data = data.groupby('Year').agg({emission_col: 'sum'}).reset_index()
    line_chart = alt.Chart(emission_data).mark_line(point=True).encode(
        x=alt.X('Year:N', axis=alt.Axis(title='Year')),
        y=alt.Y(f'{emission_col}:Q', axis=alt.Axis(title='Emissions')),
        tooltip=[alt.Tooltip('Year:N', title='Year'), alt.Tooltip(f'{emission_col}:Q', title='Emissions')]
    ).properties(
        title=f'Annual {emission_type} Emissions Over Time'
    )
    st.altair_chart(line_chart, use_container_width=True)

    # Fourth row for the updated bar chart using Plotly
    fig = px.bar(top_companies_df, x='Facility.Name', y=emission_col,
                 color='Highlight', color_discrete_map={'Selected Company': 'orange', 'Other Companies': 'steelblue'},
                 labels={emission_col: 'Emissions', 'Facility.Name': 'Company'},
                 title=f'Top Companies {emission_type} Emissions Comparison in Sector')
    fig.update_layout(xaxis_title="Company", yaxis_title="Emissions", xaxis={'categoryorder':'total descending'})
    fig.update_xaxes(tickangle=45)

    st.plotly_chart(fig, use_container_width=True)



# Run the main function
if __name__ == "__main__":
    run()