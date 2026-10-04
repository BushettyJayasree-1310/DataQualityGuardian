# 🛡️ Data Quality Guardian

### AI-Powered Data Quality Analysis and Cleaning Assistant

Data Quality Guardian is a Python-based web application that helps users identify, analyze, and improve the quality of structured datasets. It combines automated data quality checks with **Google Gemini AI** to generate quality reports, recommend cleaning actions, and answer questions about uploaded data.

The application is designed for data analysts, business teams, students, and researchers who want to prepare reliable data for analysis and decision-making.

## 🚀 Live Demo

**Try the application:** https://dataqualityguardian-yegdgtdztvge6mk56p3wts.streamlit.app/

## 🎯 Problem Statement

Poor-quality data can lead to inaccurate analysis, unreliable reports, and incorrect business decisions. Common issues include missing values, duplicate records, invalid email addresses, inconsistent whitespace, and unusual data patterns.

Manually identifying these problems can be time-consuming. Data Quality Guardian simplifies this process through automated data profiling, interactive visualizations, data cleaning, anomaly detection, and AI-assisted insights.

## ✨ Key Features

* **Dataset Upload:** Upload CSV and Excel files for analysis.
* **Automated Data Quality Checks:** Identify missing values, duplicate rows, invalid email formats, and extra whitespace.
* **Data Quality Dashboard:** View data quality metrics and interactive visualizations.
* **AI Quality Report:** Generate an understandable report using Google Gemini AI.
* **AI Cleaning Recommendations:** Receive suggestions for improving dataset quality.
* **Ask Your Data:** Ask questions about your dataset and receive AI-generated explanations based on the available data summary.
* **Data Cleaning:** Apply supported cleaning operations to improve data consistency.
* **Anomaly Detection:** Use the Isolation Forest algorithm to identify potentially unusual records.
* **Download Cleaned Data:** Export processed datasets in CSV and Excel formats.

## 🛠️ Technology Stack

| Technology        | Purpose                                                      |
| ----------------- | ------------------------------------------------------------ |
| Python            | Core application logic and data processing                   |
| Streamlit         | Interactive web application interface                        |
| Pandas            | Data manipulation and quality analysis                       |
| Plotly            | Interactive charts and visualizations                        |
| Scikit-learn      | Anomaly detection using Isolation Forest                     |
| OpenPyXL          | Excel file processing                                        |
| Google Gemini API | AI-generated quality reports, recommendations, and responses |

## ⚙️ How It Works

1. **Upload Dataset:** The user uploads a CSV or Excel file.
2. **Analyze Data:** Python and Pandas inspect the dataset and calculate data quality metrics.
3. **Identify Issues:** The application detects supported data quality problems.
4. **Visualize Results:** Metrics, summaries, and charts present the findings.
5. **Generate AI Insights:** Gemini interprets the computed summary and provides explanations and recommendations.
6. **Clean and Export:** The user applies supported cleaning operations and downloads the processed dataset.

## 🏗️ Application Architecture

```text
User
  |
  v
Streamlit Web Interface
  |
  v
Dataset Upload (CSV / Excel)
  |
  v
Python Data Processing (Pandas)
  |
  v
Data Quality Checks and Metrics
  |
  +----------------------+
  |                      |
  v                      v
Visual Dashboard     Anomaly Detection
  |                  (Isolation Forest)
  |
  v
Computed Summary
  |
  v
Google Gemini API
  |
  v
AI Report / Recommendations / Q&A
  |
  v
Data Cleaning and Export
```

## 💻 Run Locally

### Prerequisites

* Python 3.10 or later, compatible with the installed dependencies
* Git
* A Google Gemini API key for AI-powered features

### 1. Clone the repository

```bash
git clone https://github.com/BushettyJayasree-1310/DataQualityGuardian.git
cd DataQualityGuardian
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Create a file named `.streamlit/secrets.toml` in the project directory. Add your API key:

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

Replace the placeholder with your actual key. Never commit this file or publish your API key.

### 5. Run the application

```bash
python -m streamlit run app.py
```

The application will open in your browser at the local URL shown in the terminal.

## 📂 Project Structure

```text
DataQualityGuardian/
├── .streamlit/
│   └── secrets.toml       # Local API key; do not commit
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── sample_business_data.csv
├── dirty_cafe_sales.csv
├── .gitignore
└── README.md
```

## 🔐 Security

* Store API keys in Streamlit secrets or environment variables.
* Keep `.streamlit/secrets.toml` and `.env` out of version control.
* Do not publish API keys, passwords, or sensitive datasets.
* Review uploaded data before sharing it with external AI services.
* Use anonymized or synthetic datasets for public demonstrations.

## ⚠️ Limitations

* AI-generated explanations depend on the quality and completeness of the information provided to the model.
* Anomaly detection identifies potentially unusual records; these are not necessarily errors.
* Cleaning operations should be reviewed before the processed data is used for important decisions.
* AI-powered features require valid API credentials, network connectivity, and model availability.
* The application focuses on structured CSV and Excel data and the quality checks implemented in the current version.

## 🔮 Future Enhancements

* Add user authentication and role-based access.
* Store analysis history and reports in a database.
* Support larger datasets and additional file formats.
* Introduce customizable data quality rules and thresholds.
* Add more advanced data validation and anomaly detection methods.
* Provide data quality score comparisons across multiple datasets.
* Enable scheduled data quality monitoring and alerts.

## 🎓 Project Objective

The objective of Data Quality Guardian is to make data quality assessment more accessible by combining automated data profiling, interactive visualization, machine learning, and generative AI in a single web application.

## 👩‍💻 Author

**Jayasree Bushetty**

GitHub: [BushettyJayasree-1310](https://github.com/BushettyJayasree-1310)

