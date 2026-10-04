
import io
import re

import pandas as pd
import plotly.express as px
import streamlit as st
import numpy as np
from sklearn.ensemble import IsolationForest
from google import genai

# -------------------- PAGE CONFIGURATION --------------------
st.set_page_config(
    page_title="Data Quality Guardian",
    page_icon="🔎",
    layout="wide"
)


st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    div[data-testid="stMetric"] {
        background: #1e293b;
        color: #ffffff;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #334155;
    }

    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🔎 Data Quality Guardian")
st.caption(
    "Intelligent Enterprise Data Quality Analysis and Cleaning System"
)
st.write(
    "Upload a business dataset to identify data-quality issues, "
    "review recommended corrections, and export cleaned data."
)


# -------------------- HELPER FUNCTIONS --------------------
def read_uploaded_file(file):
    """Read CSV or Excel data safely."""
    if file.name.lower().endswith(".csv"):
        try:
            file.seek(0)
            return pd.read_csv(file)
        except UnicodeDecodeError:
            file.seek(0)
            return pd.read_csv(file, encoding="latin-1")
    file.seek(0)
    return pd.read_excel(file)


def is_valid_email(value):
    """Basic format check, not proof that an email exists."""
    if pd.isna(value):
        return False
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return bool(re.match(pattern, str(value).strip()))


def analyze_data(df):
    """Create a row-level report of detected issues."""
    issues = []
    email_columns = [
        col for col in df.columns
        if "email" in str(col).lower()
    ]

    for col in df.columns:
        missing_rows = df.index[df[col].isna()].tolist()
        for idx in missing_rows:
            issues.append({
                "Row": int(idx) + 2,
                "Column": str(col),
                "Issue": "Missing value",
                "Details": "This cell is empty."
            })

    duplicate_mask = df.duplicated(keep=False)
    for idx in df.index[duplicate_mask]:
        issues.append({
            "Row": int(idx) + 2,
            "Column": "Entire row",
            "Issue": "Duplicate record",
            "Details": "This row matches another record."
        })

    for col in email_columns:
        for idx, value in df[col].items():
            if pd.notna(value) and not is_valid_email(value):
                issues.append({
                    "Row": int(idx) + 2,
                    "Column": str(col),
                    "Issue": "Invalid email format",
                    "Details": f"Value '{value}' does not match a basic email format."
                })

    for col in df.select_dtypes(include=["object", "string"]).columns:
        for idx, value in df[col].items():
            if isinstance(value, str) and value != value.strip():
                issues.append({
                    "Row": int(idx) + 2,
                    "Column": str(col),
                    "Issue": "Extra whitespace",
                    "Details": "Text has leading or trailing spaces."
                })

    return pd.DataFrame(
        issues,
        columns=["Row", "Column", "Issue", "Details"]
    )


# -------------------- FILE UPLOAD --------------------
uploaded_file = st.file_uploader(
    "Upload your business dataset",
    type=["csv", "xlsx"],
    help="Supported formats: CSV and Excel (.xlsx)"
)

if uploaded_file is None:
    st.info("👆 Upload a file to begin your data-quality analysis.")

    st.subheader("What this application checks")
    c1, c2 = st.columns(2)
    c1.markdown(
        "- Missing values\n"
        "- Duplicate records\n"
        "- Invalid email formats"
    )
    c2.markdown(
        "- Extra spaces in text\n"
        "- Data completeness\n"
        "- Cleaned-data export"
    )

    st.caption(
        "Tip: Try a small CSV or Excel file containing sample business data."
    )
    st.stop()


# -------------------- LOAD DATA --------------------
try:
    original_df = read_uploaded_file(uploaded_file)
except Exception as error:
    st.error(f"Could not read the uploaded file: {error}")
    st.stop()

if original_df.empty:
    st.warning("The uploaded file contains no data rows.")
    st.stop()

if len(original_df.columns) == 0:
    st.error("No columns were found in the uploaded file.")
    st.stop()

if original_df.columns.duplicated().any():
    st.error(
        "Some column names are repeated. Please rename the duplicate "
        "columns in your file and upload it again."
    )
    st.stop()

# Use a fresh, consistent row index for reporting.
original_df = original_df.reset_index(drop=True)
original_df.columns = [
    str(col).strip() if str(col).strip() else f"Unnamed_{i + 1}"
    for i, col in enumerate(original_df.columns)
]

# -------------------- ANALYZE ORIGINAL DATA --------------------
issue_report = analyze_data(original_df)

missing_count = int(original_df.isna().sum().sum())
duplicate_count = int(original_df.duplicated().sum())
total_cells = int(original_df.size)

email_columns = [
    col for col in original_df.columns
    if "email" in str(col).lower()
]
invalid_email_count = 0

for col in email_columns:
    invalid_email_count += int(
        (
            original_df[col].notna()
            & ~original_df[col].apply(is_valid_email)
        ).sum()
    )

completeness = (
    100 * (total_cells - missing_count) / total_cells
    if total_cells else 100.0
)

# -------------------- SUMMARY DASHBOARD --------------------
st.divider()
st.subheader("📊 Data Quality Dashboard")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Records", f"{len(original_df):,}")
m2.metric("Total Columns", f"{len(original_df.columns):,}")
m3.metric("Missing Cells", f"{missing_count:,}")
m4.metric("Duplicate Rows", f"{duplicate_count:,}")

m5, m6 = st.columns(2)
m5.metric("Data Completeness", f"{completeness:.1f}%")
m6.metric("Invalid Email Entries", f"{invalid_email_count:,}")

st.caption(
    "Completeness measures the percentage of cells that are not missing. "
    "Email validation checks format only, not whether an address exists."
)


# -------------------- AI ANOMALY DETECTION --------------------
st.divider()
st.subheader("🤖 AI-Powered Anomaly Detection")

st.write(
    "Isolation Forest uses machine learning to identify unusual "
    "patterns in numerical data. Flagged records should be reviewed."
)

numeric_df = original_df.select_dtypes(include="number")

if len(original_df) < 5:
    st.info("Upload at least 5 records for anomaly detection.")

elif numeric_df.empty:
    st.info("No numerical columns were found in this dataset.")

else:
    # Fill missing numerical cells with each column's median.
    model_data = numeric_df.fillna(numeric_df.median())

    # Ignore columns that have the same value in every row.
    model_data = model_data.loc[
        :, model_data.nunique() > 1
    ]

    if model_data.shape[1] == 0:
        st.info(
            "No varying numerical columns are available "
            "for anomaly detection."
        )
    else:
        model = IsolationForest(
            n_estimators=100,
            contamination="auto",
            random_state=42
        )

        predictions = model.fit_predict(model_data)
        anomaly_mask = predictions == -1

        anomaly_results = original_df.copy()
        anomaly_results["Anomaly Status"] = np.where(
            anomaly_mask,
            "Potential Anomaly - Review",
            "No Anomaly Flagged"
        )

        col1, col2 = st.columns(2)
        col1.metric("Records Analysed", len(original_df))
        col2.metric(
            "Potential Anomalies",
            int(anomaly_mask.sum())
        )

        if anomaly_mask.any():
            st.warning(
                "The following records differ from patterns "
                "learned by the model. They are not necessarily errors."
            )
            st.dataframe(
                anomaly_results.loc[anomaly_mask],
                use_container_width=True
            )
        else:
            st.success(
                "No records were flagged as potential anomalies."
            )

        with st.expander("View all anomaly detection results"):
            st.dataframe(
                anomaly_results,
                use_container_width=True
            )

        anomaly_csv = anomaly_results.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            "⬇️ Download Anomaly Results",
            data=anomaly_csv,
            file_name="anomaly_detection_results.csv",
            mime="text/csv"
        )
        
# -------------------- DATA PREVIEW --------------------
st.subheader("📄 Original Dataset")
st.dataframe(original_df, use_container_width=True, height=300)

with st.expander("View column-level statistics"):
    summary = pd.DataFrame({
        "Data Type": original_df.dtypes.astype(str),
        "Missing Values": original_df.isna().sum(),
        "Unique Values": original_df.nunique(dropna=True)
    })
    st.dataframe(summary, use_container_width=True)

# -------------------- VISUALIZATIONS --------------------
st.subheader("📈 Quality Insights")

left, right = st.columns(2)

with left:
    missing_by_column = original_df.isna().sum()
    missing_by_column = missing_by_column[missing_by_column > 0]

    if not missing_by_column.empty:
        chart_df = missing_by_column.rename_axis("Column").reset_index(
            name="Missing Values"
        )
        fig = px.bar(
            chart_df,
            x="Column",
            y="Missing Values",
            title="Missing Values by Column"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("No missing values detected.")

with right:
    issue_counts = issue_report["Issue"].value_counts()

    if not issue_counts.empty:
        chart_df = issue_counts.rename_axis("Issue").reset_index(
            name="Count"
        )
        fig = px.pie(
            chart_df,
            names="Issue",
            values="Count",
            title="Distribution of Detected Issues"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("No issues detected by the available checks.")

# -------------------- ISSUE REPORT --------------------
st.subheader("🚩 Detected Issues")

if issue_report.empty:
    st.success("No issues were detected by the available checks.")
else:
    st.write(f"Found **{len(issue_report):,} issue entries**.")
    st.dataframe(issue_report, use_container_width=True, height=260)

    issue_csv = issue_report.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Download Issue Report",
        data=issue_csv,
        file_name="data_quality_issue_report.csv",
        mime="text/csv"
    )

# -------------------- GENERATIVE AI FEATURES --------------------
st.divider()
st.subheader("✨ Generative AI Assistant")
st.write(
    "Use Gemini to explain the quality findings, suggest review steps, "
    "or ask questions about the dataset summary."
)
st.warning(
    "Privacy notice: when you click an AI button, the app sends the dataset's "
    "column names and aggregate quality statistics to Google Gemini. Do not use "
    "this feature with confidential or personally identifiable data unless you "
    "have permission to share that information with the API provider."
)


def ask_gemini(prompt):
    """Send a bounded prompt to Gemini without exposing the API key in the UI."""
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key or api_key == "PASTE_NEW_PRIVATE_KEY_HERE":
        return None, (
            "Gemini API key is not configured. Add your private key to "
            ".streamlit/secrets.toml as GEMINI_API_KEY."
        )
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
        )
        answer = getattr(response, "text", None)
        if not answer:
            return None, "Gemini returned an empty response. Please try again."
        return answer, None
    
    except Exception as exc:
        print(f"Gemini error: {type(exc).__name__}: {exc}")
        return None, (
            f"Gemini error: {type(exc).__name__}: {exc}"
        )

quality_context = {
    "record_count": int(len(original_df)),
    "column_count": int(len(original_df.columns)),
    "columns": [str(c) for c in original_df.columns],
    "data_types": {str(c): str(original_df[c].dtype) for c in original_df.columns},
    "missing_values_by_column": {
        str(c): int(n) for c, n in original_df.isna().sum().items() if int(n) > 0
    },
    "duplicate_rows": int(duplicate_count),
    "invalid_email_entries": int(invalid_email_count),
    "completeness_percent": round(float(completeness), 2),
    "issue_counts": {
        str(k): int(v) for k, v in issue_report["Issue"].value_counts().items()
    } if not issue_report.empty else {},
}

ai_report_tab, ai_recommend_tab, ask_data_tab = st.tabs([
    "AI Quality Report", "Cleaning Recommendations", "Ask Your Data"
])

with ai_report_tab:
    st.markdown("**Generate a plain-language explanation of this dataset's quality.**")
    if st.button("Generate AI Quality Report", key="generate_quality_report"):
        prompt = (
            "You are a careful data-quality analyst. Explain the following "
            "computed dataset-quality summary for a beginner. Use headings for "
            "Overall assessment, Main findings, Risks, and Next steps. Base all "
            "numeric statements only on the supplied summary. Do not invent "
            "facts or claim to have inspected individual records. Explain that "
            "anomalies or formatting checks can require human review.\n\n"
            f"Computed summary: {quality_context}"
        )
        with st.spinner("Gemini is preparing the report..."):
            answer, error = ask_gemini(prompt)
        if error:
            st.error(error)
        else:
            st.session_state["gemini_quality_report"] = answer
    if st.session_state.get("gemini_quality_report"):
        st.markdown(st.session_state["gemini_quality_report"])

with ai_recommend_tab:
    st.markdown("**Get practical cleaning suggestions based on detected issues.**")
    if st.button("Suggest Cleaning Steps", key="generate_cleaning_recommendations"):
        prompt = (
            "You are a cautious data-quality analyst. Recommend cleaning steps "
            "based only on this computed summary. For each recommendation, state "
            "the issue, suggested action, and a risk or validation check. Do not "
            "modify data, assume business rules, or recommend deleting records "
            "without review. Clearly distinguish safe formatting fixes from "
            "decisions requiring domain knowledge.\n\n"
            f"Computed summary: {quality_context}"
        )
        with st.spinner("Gemini is preparing recommendations..."):
            answer, error = ask_gemini(prompt)
        if error:
            st.error(error)
        else:
            st.session_state["gemini_cleaning_recommendations"] = answer
    if st.session_state.get("gemini_cleaning_recommendations"):
        st.markdown(st.session_state["gemini_cleaning_recommendations"])

with ask_data_tab:
    st.markdown("**Ask a question about the dataset's structure and computed quality summary.**")
    user_question = st.text_input(
        "Your question",
        placeholder="Example: Which columns need the most attention?",
        key="gemini_dataset_question",
    )
    if st.button("Ask Gemini", key="ask_gemini_about_data"):
        if not user_question.strip():
            st.info("Enter a question first.")
        else:
            prompt = (
                "You are a data-quality assistant. Answer the user's question "
                "using only the supplied dataset schema and computed summary. "
                "If the summary does not contain enough information, say so "
                "instead of guessing. Do not claim to know individual cell "
                "values or records. Keep the answer clear and concise.\n\n"
                f"Computed summary: {quality_context}\n\n"
                f"User question: {user_question.strip()[:1000]}"
            )
            with st.spinner("Gemini is answering..."):
                answer, error = ask_gemini(prompt)
            if error:
                st.error(error)
            else:
                st.session_state["gemini_dataset_answer"] = answer
                st.session_state["gemini_dataset_answer_question"] = user_question.strip()
    if st.session_state.get("gemini_dataset_answer"):
        st.markdown("**Answer**")
        st.markdown(st.session_state["gemini_dataset_answer"])


# -------------------- DATA CLEANING --------------------
st.divider()
st.subheader("🧹 Clean Your Dataset")
st.write(
    "Choose the cleaning operations you want to apply. "
    "Your uploaded original data remains unchanged."
)

with st.form("cleaning_options"):
    remove_duplicates = st.checkbox(
        "Remove duplicate rows",
        value=True
    )
    trim_spaces = st.checkbox(
        "Remove leading and trailing spaces from text",
        value=True
    )
    missing_strategy = st.selectbox(
        "How should missing values be handled?",
        [
            "Keep missing values",
            "Fill numeric values with column median and text with 'Not provided'",
            "Remove rows containing missing values"
        ]
    )

    clean_clicked = st.form_submit_button(
        "Apply Cleaning Operations"
    )

if clean_clicked:
    cleaned_df = original_df.copy()

    if trim_spaces:
        for col in cleaned_df.select_dtypes(
            include=["object", "string"]
        ).columns:
            cleaned_df[col] = cleaned_df[col].apply(
                lambda value: value.strip()
                if isinstance(value, str) else value
            )

    if remove_duplicates:
        cleaned_df = cleaned_df.drop_duplicates().reset_index(drop=True)

    if missing_strategy.startswith("Fill numeric"):
        for col in cleaned_df.columns:
            if pd.api.types.is_numeric_dtype(cleaned_df[col]):
                median_value = cleaned_df[col].median()
                if pd.notna(median_value):
                    cleaned_df[col] = cleaned_df[col].fillna(median_value)
            else:
                cleaned_df[col] = cleaned_df[col].fillna("Not provided")

    elif missing_strategy.startswith("Remove rows"):
        cleaned_df = cleaned_df.dropna().reset_index(drop=True)

    st.session_state["cleaned_data"] = cleaned_df
    st.session_state["cleaning_done"] = True

if st.session_state.get("cleaning_done", False):
    cleaned_df = st.session_state["cleaned_data"]

    st.success("Cleaning operations completed. Review the results below.")

    a, b, c = st.columns(3)
    a.metric("Original Rows", len(original_df))
    b.metric("Cleaned Rows", len(cleaned_df))
    c.metric("Rows Removed", len(original_df) - len(cleaned_df))

    st.dataframe(cleaned_df, use_container_width=True, height=300)

    csv_data = cleaned_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Download Cleaned CSV",
        data=csv_data,
        file_name="cleaned_business_data.csv",
        mime="text/csv"
    )

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        cleaned_df.to_excel(
            writer, index=False, sheet_name="Cleaned Data"
        )

    st.download_button(
        "⬇️ Download Cleaned Excel",
        data=excel_buffer.getvalue(),
        file_name="cleaned_business_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.divider()
st.caption(
    "Data Quality Guardian | Academic Project | "
    "Python • Pandas • Streamlit • Plotly"
)