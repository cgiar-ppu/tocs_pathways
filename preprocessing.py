import pandas as pd
import os
from pathlib import Path

def process_excel_files(sheet_name, output_filename):
    # Define input and output directories
    input_dir = Path('ToCsApril2025')
    output_dir = Path('processed_files')
    output_dir.mkdir(exist_ok=True)
    
    # Get all Excel files in the input directory
    excel_files = [f for f in os.listdir(input_dir) if f.endswith(('.xlsx', '.xls'))]
    
    if not excel_files:
        print("No Excel files found in the ToCsApril2025 directory!")
        return
    
    # Initialize an empty list to store all dataframes
    all_data = []
    
    # Process each Excel file
    for excel_file in excel_files:
        try:
            # Read the specified sheet
            file_path = input_dir / excel_file
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # Add source file column
            df['Source_File'] = excel_file
            
            # Append to our list of dataframes
            all_data.append(df)
            print(f"Successfully processed {excel_file}")
            
        except Exception as e:
            print(f"Error processing {excel_file}: {str(e)}")
    
    if not all_data:
        print("No data was successfully processed!")
        return
    
    # Combine all dataframes
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Save to output file
    output_file = output_dir / output_filename
    combined_df.to_excel(output_file, index=False)
    print(f"\nProcessing complete! Output saved to: {output_file}")

if __name__ == "__main__":
    # Process Research Questions tab
    print("\nProcessing Research Questions tab...")
    process_excel_files("Research Questions", "combined_research_questions.xlsx")
    
    # Process Result Framework tab (note: without 's')
    print("\nProcessing Result Framework tab...")
    process_excel_files("Result Framework", "combined_result_framework.xlsx") 