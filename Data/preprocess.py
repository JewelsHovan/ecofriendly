import pandas as pd

def load_and_preprocess_unit_data(unit_path):
    # Load the dataset
    unit_df = pd.read_csv(unit_path)
    
    # Output the column names to ensure we reference them correctly
    print(f"Unit columns: {unit_df.columns}")
    
    # Correct the column names based on the actual columns
    # Replace 'Methane.emissions', 'Nitrous.Oxide.emissions', and 'CO2.emissions.non.biogenic.'
    # with the actual column names from your CSV file
    emissions_columns = ['Methane.emissions', 'Nitrous.Oxide.emissions', 'CO2.emissions.non.biogenic.']  # example column names
    
    # Handle missing values by replacing them with zeros
    for col in emissions_columns:
        unit_df[col] = unit_df[col].fillna(0)
    
    # Define GWP values for standardizing emissions
    gwp_values = {'CO2': 1, 'CH4': 25, 'N2O': 298}

    # Calculate the CO2 equivalent emissions using GWP values
    unit_df['CO2_eq_emissions'] = (unit_df['CO2.emissions.non.biogenic.'] +
                                   unit_df['Methane.emissions'] * gwp_values['CH4'] +
                                   unit_df['Nitrous.Oxide.emissions'] * gwp_values['N2O'])
    
    # Add total emissions for each gas type
    unit_df['CO2_emissions'] = unit_df['CO2.emissions.non.biogenic.']
    unit_df['CH4_emissions'] = unit_df['Methane.emissions']
    unit_df['N2O_emissions'] = unit_df['Nitrous.Oxide.emissions']

    
    # Assuming 'Max.Heat' is the proxy for output, calculate the Eco Score
    # Replace zeros in 'Max.Heat' to avoid division by zero
    unit_df['Max.Heat'].replace(0, 1e-10, inplace=True)
    unit_df['Eco_Score'] = unit_df['CO2_eq_emissions'] / unit_df['Max.Heat']
    
    # Replace infinite and NaN values that result from division by zero with a large number
    unit_df['Eco_Score'].replace([float('inf'), float('-inf')], 1e10, inplace=True)
    unit_df['Eco_Score'].fillna(1e10, inplace=True)
    
    # Return the processed DataFrame
    return unit_df

# Path to the Unit.csv file
unit_path = 'Unit.csv'  # Update the path if necessary

# Process the unit data
unit_df_processed = load_and_preprocess_unit_data(unit_path)

# Save the processed data to a new CSV file for quick loading in the future
unit_df_processed.to_csv('Processed_Unit.csv', index=False)

print("Unit data has been processed and saved to a new CSV file.")