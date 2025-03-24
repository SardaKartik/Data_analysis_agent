# %%
from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai_tools import SerperDevTool
import os
import litellm


# %%
from langchain_core.tools import Tool
from langchain_experimental.utilities import PythonREPL

# %%
# an agent tool from the langchain which is able to gave the environment for python code
python_repl = PythonREPL() 

# %%
import json

# %%
# 2. Configure LiteLLM for Gemini DIRECTLY
litellm.drop_params = True
litellm.set_verbose = True


# %%
from dotenv import load_dotenv
load_dotenv()

# %%
import os 

# %%
API_KEY = os.getenv("Gemini_API_KEY")

# %%
os.environ["GEMINI_API_KEY"] = API_KEY
os.environ["LITELLM_PROVIDER"] = "google"  # Force LiteLLM to use Google

# %%
# 2. Configure Gemini PROPERLY
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
    #max_output_tokens=2048,
    google_api_key= os.getenv("Gemini_API_KEY")  # Explicit key assignment
)


# %%
import os
import pandas as pd
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew, Process
from langchain.tools import BaseTool

# %%
# ------------------------
# Universal Data Tools
# ------------------------

class FileInputSchema(BaseModel):
    filename: str = Field(..., description="Path to CSV file")

class DataLoaderTool(BaseTool):
    name = "data_loader"
    description = "Load and validate any CSV file with dynamic typing"
    
    def _run(self, filename: str) -> pd.DataFrame | str:
        """Load and validate any CSV file with dynamic typing"""
        try:
            # Input validation
            if not os.path.exists(filename):
                return f"File not found: {filename}"
            if not filename.endswith('.csv'):
                return "Only CSV files are supported"

            # Load data with automatic type detection
            df = pd.read_csv(filename)
            
            # Basic validation
            if df.empty:
                return "Empty CSV file"
                
            return df

        except Exception as e:
            return f"Data loading failed: {str(e)}"

class StatisticalAnalyzerTool(BaseTool):
    name = "statistical_analyzer"
    description = "Analyze any CSV file's numerical features including correlation analysis"
    
    def _run(self, filename: str) -> str:
        """Analyze any CSV file's numerical features including correlation analysis"""
        try:
            # Create an instance of the data loader tool
            data_loader_tool = DataLoaderTool()
            
            # Load data
            data = data_loader_tool._run(filename)
            if isinstance(data, str):
                return data  # Return error message
                
            report = [
                f"# Statistical Report for {os.path.basename(filename)}",
                f"**Dataset Shape:** {data.shape[0]} rows, {data.shape[1]} columns"
            ]
            
            # Numerical Analysis
            numeric_cols = data.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                report.append("\n## Numerical Features Analysis")
                for col in numeric_cols:
                    stats = data[col].describe(percentiles=[.25, .75])
                    report.extend([
                        f"\n### {col}",
                        f"- Mean: {stats['mean']:.2f}",
                        f"- Median: {stats['50%']:.2f}",
                        f"- Std Dev: {stats['std']:.2f}",
                        f"- Range: {stats['min']:.2f} to {stats['max']:.2f}",
                        f"- IQR: {stats['75%'] - stats['25%']:.2f}"
                    ])
            
            # Categorical Analysis
            cat_cols = data.select_dtypes(include=['object', 'category']).columns
            if len(cat_cols) > 0:
                report.append("\n## Categorical Features Analysis")
                for col in cat_cols:
                    counts = data[col].value_counts()
                    report.extend([
                        f"\n### {col}",
                        f"- Unique Values: {len(counts)}",
                        f"- Most Common: {counts.idxmax()} ({counts.max()} entries)"
                    ])
            
            # Correlation Analysis
            if len(numeric_cols) > 1:
                report.append("\n## Correlation Analysis")
                # Calculate correlation matrix
                corr_matrix = data[numeric_cols].corr()
                
                # Format correlation matrix as markdown
                report.append("\n### Correlation Matrix")
                report.append(corr_matrix.round(2).to_markdown())
                
                # Find strong correlations (absolute value > 0.5)
                strong_corrs = []
                for i in range(len(numeric_cols)):
                    for j in range(i+1, len(numeric_cols)):
                        col1 = numeric_cols[i]
                        col2 = numeric_cols[j]
                        corr_value = corr_matrix.iloc[i, j]
                        if abs(corr_value) > 0.5:
                            strength = "Strong Positive" if corr_value > 0.7 else "Moderate Positive" if corr_value > 0 else "Strong Negative" if corr_value < -0.7 else "Moderate Negative"
                            strong_corrs.append({
                                'Feature 1': col1,
                                'Feature 2': col2, 
                                'Correlation': f"{corr_value:.2f}",
                                'Strength': strength
                            })
                
                if strong_corrs:
                    report.append("\n### Strong Feature Correlations")
                    report.append("*Correlations with absolute value > 0.5*")
                    report.append(pd.DataFrame(strong_corrs).to_markdown(index=False))
                else:
                    report.append("\n*No strong correlations found between features (threshold: 0.5)*")
            
            return "\n".join(report)
            
        except Exception as e:
            return f"Analysis failed: {str(e)}"
        
        
class AnomalyDetectorTool(BaseTool):
    name = "anomaly_detector"
    description = "Detect anomalies in any CSV dataset"
    
    def _run(self, filename: str) -> str:
        """Detect anomalies in any CSV dataset"""
        try:
            # Create an instance of the data loader tool
            data_loader_tool = DataLoaderTool()
            
            # Load data
            data = data_loader_tool._run(filename)
            if isinstance(data, str):
                return data
                
            report = [
                f"# Anomaly Report for {os.path.basename(filename)}",
                f"**Total Records:** {len(data):,}"
            ]
            
            # Data Quality Checks
            quality = pd.DataFrame({
                'Missing Values': data.isna().sum(),
                'Zero Values': (data == 0).sum(),
                'Unique Values': data.nunique()
            })
            report.append("\n## Data Quality Assessment")
            report.append(quality.to_markdown())
            
            # Numerical Anomalies
            numeric_cols = data.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                report.append("\n## Numerical Anomalies")
                anomalies = []
                for col in numeric_cols:
                    q1 = data[col].quantile(0.25)
                    q3 = data[col].quantile(0.75)
                    iqr = q3 - q1
                    outliers = data[(data[col] < (q1 - 1.5*iqr)) | (data[col] > (q3 + 1.5*iqr))]
                    anomalies.append({
                        'Feature': col,
                        'Outliers': len(outliers),
                        'Min': data[col].min(),
                        'Max': data[col].max()
                    })
                report.append(pd.DataFrame(anomalies).to_markdown(index=False))
            
            return "\n".join(report)
            
        except Exception as e:
            return f"Anomaly detection failed: {str(e)}"
        


class InteractiveVisualizationTool(BaseTool):
    name = "interactive_data_visualizer"
    description = "Create interactive visualizations from CSV data"
    
    def _run(self, 
             file_path: str,  
             chart_type: str,  
             x_axis: str = None,  
             y_axis: str = None,  
             column_name: str = None,  
             title: str = None,  
             output_path: str = None) -> str:  
        """
        Create interactive visualizations from CSV data
        """
        try:
            # Import required libraries
            import pandas as pd
            import plotly.express as px
            import plotly.graph_objects as go
            import os
            
            # First, validate the chart_type
            valid_chart_types = ["scatter", "histogram", "box", "heatmap", "bar", "line"]
            
            # Normalize the chart type
            normalized_chart_type = chart_type.lower().replace("_", "").replace("-", "").replace(" ", "")
            if normalized_chart_type not in valid_chart_types:
                return f"Unsupported chart type: {chart_type}. Supported types: {', '.join(valid_chart_types)}"
            
            # Validate the file exists
            if not os.path.exists(file_path):
                return f"File not found: {file_path}"
            
            # Load data
            try:
                data = pd.read_csv(file_path)
                if data.empty:
                    return "Empty CSV file"
            except Exception as e:
                return f"Failed to load CSV file: {str(e)}"
            
            # Set default output path if not provided
            if not output_path:
                output_dir = os.path.dirname(file_path)
                # Ensure output directory exists
                if not output_dir:
                    output_dir = "."
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                output_path = os.path.join(output_dir, f"{base_name}_{chart_type}_plot.html")
            
            # Column validation
            available_columns = list(data.columns)
            
            # Check column existence
            if column_name and column_name not in available_columns:
                return f"Column '{column_name}' not found in dataset. Available columns: {', '.join(available_columns)}"
            if x_axis and x_axis not in available_columns:
                return f"Column '{x_axis}' not found in dataset. Available columns: {', '.join(available_columns)}"
            if y_axis and y_axis not in available_columns:
                return f"Column '{y_axis}' not found in dataset. Available columns: {', '.join(available_columns)}"
            
            # Create the visualization based on the chart type
            fig = None
            
            if chart_type == "histogram":
                col = column_name if column_name else x_axis
                if not col:
                    return "Histogram requires either column_name or x_axis parameter"
                
                fig = px.histogram(data, x=col, title=title or f"Distribution of {col}")
                
            elif chart_type == "scatter":
                if not x_axis or not y_axis:
                    return "Scatter plot requires both x_axis and y_axis parameters"
                
                fig = px.scatter(data, x=x_axis, y=y_axis, title=title or f"{y_axis} vs {x_axis}")
                
            elif chart_type == "box":
                col = column_name if column_name else y_axis if y_axis else x_axis
                if not col:
                    return "Box plot requires either column_name, x_axis, or y_axis parameter"
                
                fig = px.box(data, y=col, title=title or f"Distribution of {col}")
                
            elif chart_type == "heatmap":
                # For heatmap, use all numeric columns
                numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
                
                if len(numeric_cols) < 2:
                    return "Heatmap requires at least 2 numeric columns in the dataset"
                
                # If x_axis and y_axis are specified, use them
                if x_axis and y_axis:
                    if x_axis in numeric_cols and y_axis in numeric_cols:
                        cols = [x_axis, y_axis]
                    else:
                        return "Both x_axis and y_axis must be numeric columns for heatmap"
                else:
                    cols = numeric_cols
                
                corr_matrix = data[cols].corr().fillna(0)
                fig = go.Figure(data=go.Heatmap(
                    z=corr_matrix.values,
                    x=corr_matrix.columns,
                    y=corr_matrix.index,
                    colorscale='RdBu',
                    zmin=-1, zmax=1
                ))
                fig.update_layout(title=title or "Correlation Heatmap")
                
            elif chart_type == "bar":
                if not x_axis:
                    return "Bar chart requires an x_axis parameter"
                
                if not y_axis:
                    # Simple count bar chart
                    counts = data[x_axis].value_counts().reset_index()
                    counts.columns = [x_axis, 'count']
                    fig = px.bar(counts, x=x_axis, y='count', title=title or f"Frequency of {x_axis}")
                else:
                    # Aggregated bar chart
                    fig = px.bar(data, x=x_axis, y=y_axis, title=title or f"{y_axis} by {x_axis}")
                
            elif chart_type == "line":
                if not x_axis or not y_axis:
                    return "Line chart requires both x_axis and y_axis parameters"
                
                fig = px.line(data, x=x_axis, y=y_axis, title=title or f"{y_axis} vs {x_axis}")
            
            # Save the interactive visualization
            try:
                fig.write_html(output_path)
                return f"Interactive visualization created successfully: {output_path}"
            except Exception as e:
                return f"Failed to save visualization: {str(e)}"
            
        except Exception as e:
            import traceback
            return f"Visualization failed: {str(e)}\nTraceback: {traceback.format_exc()}"

# ------------------------
# Agent and Crew Setup
# ------------------------

# Create tools
data_loader_tool = DataLoaderTool()
statistical_analyzer_tool = StatisticalAnalyzerTool()
anomaly_detector_tool = AnomalyDetectorTool()
visualization_tool = InteractiveVisualizationTool()

# %%
class foldercreationtool(BaseTool):
    name = "folder_creation"
    description = "Create a folder"

    def _run(self, foldername: str) -> str:
        try:
            os.mkdir(foldername)
            return f"Folder created: {foldername}"
        except Exception as e:
            return f"Failed to create folder: {str(e)}"
        

folder_creation_tool = foldercreationtool()

# %%
# too consider for the python environment 
repl_tool = Tool(
    name="python_repl",
    description="A Python shell. Use this to execute python commands. Input should be a valid python command. If you want to see the output of a value, you should print it out with `print(...)`.",
    func=python_repl.run,
)

# %%
data_analyst = Agent(
    role="Data Analyst",
    goal="Analyze CSV data files and provide meaningful insights",
    backstory="""You are an expert data analyst with years of experience working with CSV data.
    Your specialties include data cleaning, exploratory data analysis, and finding patterns in complex datasets.
    You're known for your ability to explain complex data insights in simple terms.""",
    verbose=True,
    allow_delegation=False,
    tools=[
        data_loader_tool,  # Use tool instances, not classes
        statistical_analyzer_tool, 
        anomaly_detector_tool,
    ],
    llm=llm
)

# %%
coding_data_analyst_agent = Agent(
    role = "Data Visualizer",
    goal = "Generate insightful visualizations such as bar charts, pie charts, and other plots based on data requirements.",
    backstory = "You are an expert in data visualization with extensive experience in creating meaningful charts and graphs to uncover key insights from datasets.",
    allow_code_execution = True,
    tools = [visualization_tool, repl_tool,folder_creation_tool],    
    llm = llm
)


# %%

# %%
# Run the crew normally
def call_agent(csv_path, name, folder_name):


    data_validation_task = Task(
        description=f"Validate and load data from '{csv_path}'",
        expected_output="JSON report with data quality metrics",  # Required field
        agent=data_analyst,  # Required field
        tools=[data_loader_tool],
        config={
            'timeout': 300,
            'max_file_size': "500MB"
        }
    )


    statistical_analysis_task = Task(
        description=(
            "Perform a comprehensive statistical analysis of the dataset to uncover key insights, trends, and relationships. "
            "Identify patterns, correlations, and any anomalies that may impact decision-making. "
            "Provide actionable observations along with recommendations for further analysis."
        ),
        expected_output=(
            "A detailed statistical summary highlighting key findings, including trends, correlations, and potential outliers. "
            "Clearly outline observations and suggest additional analyses that could add value for the client."
        ),  
        agent=data_analyst,  
        tools=[statistical_analyzer_tool],  # Uncomment if using specific analysis tools
        context=[data_validation_task],  
        output_file=f"{name}_statistical_analysis_report.md"
    )

    anomaly_detection_task = Task(
        description=(
            "Detect anomalies and quality issues in the dataset using statistical and analytical techniques. "
            "Analyze patterns to identify outliers, inconsistencies, or missing values that may affect data integrity. "
            "Propose effective strategies to resolve these anomalies and enhance overall data quality."
        ),
        expected_output=(
            "A detailed anomaly detection report outlining identified anomalies, their potential impact, and recommended resolution strategies. "
            "Provide a step-by-step approach to handling these anomalies using statistical techniques, ensuring improved data reliability."
        ),  
        agent=data_analyst,  
        tools=[anomaly_detector_tool,statistical_analyzer_tool],  # Uncomment if using specific anomaly detection tools
        context=[data_validation_task],  
        output_file=f"{name}_anomaly_detection_report.md"
    )

    visualization_task = Task(
        description=(
            "Analyze the dataset by generating multiple insightful visualizations to uncover key patterns and trends. "
            "Ensure each visualization is meaningful, properly formatted, and saved in an organized output folder."
        ),
        expected_output=(
            "1. Generate multiple well-structured plots to highlight key trends, relationships, and distributions.\n"
            "2. Save all plots in an output folder named {folder_name}.\n"
            "3. For each plot:\n"
            "   - Provide a detailed explanation of what it represents.\n"
            "   - Highlight the insights it reveals about the dataset.\n"
            "   - Explain how it contributes to data understanding.\n"
            "4. Summarize key takeaways in a structured markdown report."
        ),  
        agent=coding_data_analyst_agent,  
        tools=[visualization_tool, repl_tool, folder_creation_tool],
        context=[data_validation_task],
        config={'plot_type': 'auto', 'figsize': (12, 8)},
        output_file=f"{name}_visualization_report.md"
    )

    data_analysis_crew = Crew(
        agents=[data_analyst,coding_data_analyst_agent],
        tasks=[
            data_validation_task,
            statistical_analysis_task,
            anomaly_detection_task,
            visualization_task,
        ],
        verbose=2
    )


    data_analysis_crew.kickoff()

import streamlit as st
import os
import time
from pathlib import Path
st.title("Streamlit File Downloader")

# User inputs
csv_file = st.file_uploader("Upload a CSV file:", type=["csv"])
user_name = st.text_input("Enter your name:", "")
folder_name = st.text_input("Enter the output folder name:", "")

if st.button("Generate Files"):
    if csv_file and user_name:
        call_agent(csv_file, user_name, folder_name)
        # Generate file paths based on user name using os.getcwd()
        base_dir = os.getcwd()
        base_path = os.path.join(base_dir, user_name)
        st.session_state["output_files"] = {
            "File 1": f"{base_path}_anomaly_detection_report.md",
            "File 2": f"{base_path}_statistical_analysis_report.md",
            "File 3": f"{base_path}_visualization_report.md",
        }
        st.session_state["files_ready"] = True
        st.success(f"Files are ready for {user_name}!")
    else:
        st.warning("Please provide all required inputs before generating files.")

# Display download buttons if files are ready
if st.session_state.get("files_ready", False):
    for file_label, file_path in st.session_state["output_files"].items():
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                st.download_button(
                    label=f"Download {file_label}",
                    data=f,
                    file_name=Path(file_path).name,
                    mime="application/octet-stream"
                )
        else:
            st.warning(f"{file_label} not found at {file_path}")