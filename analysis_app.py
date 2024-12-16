import streamlit as st
import pandas as pd
import plotly.express as px

# Streamlit App
st.title("Salary Cap vs Total Points Analysis")
st.write("""
This app allows you to upload multiple Excel files, select sheets to analyze, and compare data across files and sheets interactively.
""")

# File Upload
uploaded_files = st.file_uploader(
    "Upload Excel Files (you can select multiple)",
    type=["xlsx"],
    accept_multiple_files=True
)

if uploaded_files:
    # Load data for all files
    file_data = {}
    sheet_names = ['Jockeys', 'Trainers', 'Sires']

    for uploaded_file in uploaded_files:
        try:
            st.write(f"Loading data from: {uploaded_file.name}...")
            file_data[uploaded_file.name] = {
                sheet: pd.read_excel(uploaded_file, sheet_name=sheet).assign(Source=uploaded_file.name, Sheet=sheet)
                for sheet in sheet_names
            }
        except Exception as e:
            st.error(f"Error loading file {uploaded_file.name}: {e}")

    # Select which files and sheets to analyze
    selected_files = st.multiselect("Select files to include in the analysis:", list(file_data.keys()), default=list(file_data.keys()))
    selected_sheets = st.multiselect("Select sheets to include:", sheet_names, default=sheet_names)

    if selected_files and selected_sheets:
        # Combine selected sheets from selected files
        combined_data = pd.concat(
            [file_data[file][sheet] for file in selected_files for sheet in selected_sheets]
        )

        st.write("### Combined Dataset")
        st.dataframe(combined_data)

        # Allow user to select two sheets for cross-sheet analysis
        sheet_x = st.selectbox("Select Sheet for X-Axis", selected_sheets, index=0)
        sheet_y = st.selectbox("Select Sheet for Y-Axis", selected_sheets, index=1)

        # Filter combined data for the selected sheets
        data_x = combined_data[combined_data['Sheet'] == sheet_x]
        data_y = combined_data[combined_data['Sheet'] == sheet_y]

        # Merge the two datasets for cross-sheet analysis
        merged_data = pd.merge(
            data_x[['Name', 'Final_Salary', 'Total_Points', 'Source']],
            data_y[['Name', 'Final_Salary', 'Total_Points', 'Source']],
            on='Name', suffixes=('_x', '_y')
        )

        st.write(f"### Comparison: {sheet_x} vs {sheet_y}")
        st.dataframe(merged_data)

        # Correlation analysis for merged data
        if not merged_data.empty:
            corr_salary = merged_data[['Final_Salary_x', 'Final_Salary_y']].corr().iloc[0, 1]
            corr_points = merged_data[['Total_Points_x', 'Total_Points_y']].corr().iloc[0, 1]

            st.write(f"Correlation between Final Salaries ({sheet_x} vs {sheet_y}): {corr_salary:.2f}")
            st.write(f"Correlation between Total Points ({sheet_x} vs {sheet_y}): {corr_points:.2f}")

            # Interactive scatter plot for comparison
            scatter_fig = px.scatter(
                merged_data,
                x="Final_Salary_x",
                y="Total_Points_x",
                color="Source",
                title=f"Scatter Plot: {sheet_x} Final Salary vs {sheet_x} Total Points",
                labels={"Final_Salary_x": f"{sheet_x} Final Salary", "Total_Points_x": f"{sheet_x} Total Points"},
                hover_data=["Name"]
            )
            st.plotly_chart(scatter_fig)

            # Interactive scatter plot for Y-axis sheet
            scatter_fig_y = px.scatter(
                merged_data,
                x="Final_Salary_y",
                y="Total_Points_y",
                color="Source",
                title=f"Scatter Plot: {sheet_y} Final Salary vs {sheet_y} Total Points",
                labels={"Final_Salary_y": f"{sheet_y} Final Salary", "Total_Points_y": f"{sheet_y} Total Points"},
                hover_data=["Name"]
            )
            st.plotly_chart(scatter_fig_y)

            # Interactive histogram for comparison
            histogram_fig = px.histogram(
                merged_data,
                x="Final_Salary_x",
                color="Source",
                title=f"Histogram: {sheet_x} Final Salary Distribution",
                labels={"Final_Salary_x": f"{sheet_x} Final Salary"},
                nbins=20,
            )
            st.plotly_chart(histogram_fig)
