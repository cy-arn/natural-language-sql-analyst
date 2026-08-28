import streamlit as st
import pandas as pd
import duckdb
import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

# -----------------------------
# Gemini API Configuration
# -----------------------------
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except Exception:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


client = genai.Client(
    api_key=GOOGLE_API_KEY
)
MODEL_NAME = "gemini-3.6-flash"
# -----------------------------
# Convert Pandas type to SQL type --added this for phase 3
# -----------------------------

def get_sql_type(dtype):

    if pd.api.types.is_datetime64_any_dtype(dtype):
        return "DATE"

    elif pd.api.types.is_integer_dtype(dtype):
        return "BIGINT"

    elif pd.api.types.is_float_dtype(dtype):
        return "DOUBLE"

    elif pd.api.types.is_bool_dtype(dtype):
        return "BOOLEAN"

    else:
        return "VARCHAR"


st.title("CSV Data Analyzer")

st.write(
    "Upload a CSV file and analyze it using Pandas and DuckDB."
)


# -----------------------------
# Upload CSV
# -----------------------------

uploaded_file = st.file_uploader(
    "Upload your CSV file",
    type=["csv"]
)


if uploaded_file is not None:

    # -----------------------------
    # Read CSV
    # -----------------------------

    encodings = [
        "utf-8",
        "utf-8-sig",
        "cp1252",
        "latin1"
    ]

    df = None

    for encoding in encodings:

        try:

            uploaded_file.seek(0)

            df = pd.read_csv(
                uploaded_file,
                encoding=encoding
            )

            break

        except UnicodeDecodeError:
            continue


    if df is None:

        st.error(
            "Could not read this CSV file."
        )

        st.stop()


    st.success("CSV uploaded successfully.")

    # -----------------------------
    # Automatic date detection
    # -----------------------------

    for column in df.columns:

        # Check for text/string columns
        if pd.api.types.is_string_dtype(df[column]):

            non_null_values = df[column].dropna()

            if len(non_null_values) == 0:
                continue

            # Try common date formats
            date_formats = [
                "%d-%m-%Y",
                "%d/%m/%Y",
                "%Y-%m-%d",
                "%Y/%m/%d"
            ]

            best_conversion = None
            best_ratio = 0

            for date_format in date_formats:

                converted = pd.to_datetime(
                    non_null_values,
                    format=date_format,
                    errors="coerce"
                )

                valid_ratio = converted.notna().mean()

                if valid_ratio > best_ratio:

                    best_ratio = valid_ratio
                    best_conversion = date_format

            # If at least 80% of values match a date format
            if best_ratio >= 0.8:

                df[column] = pd.to_datetime(
                    df[column],
                    format=best_conversion,
                    errors="coerce"
                )

    # -----------------------------
    # Preview
    # -----------------------------

    st.subheader("Data Preview")

    st.dataframe(
        df.head(),
        use_container_width=True
    )


    # -----------------------------
    # Dataset Information
    # -----------------------------

    st.subheader("Dataset Information")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Rows",
            len(df)
        )

    with col2:
        st.metric(
            "Columns",
            len(df.columns)
        )


    # -----------------------------
    # Data Types
    # -----------------------------

    st.subheader("Column Data Types")

    dtype_df = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str).values
    })

    st.dataframe(
        dtype_df,
        use_container_width=True
    )


    # -----------------------------
    # Missing Values
    # -----------------------------

    st.subheader("Missing Values")

    missing_df = pd.DataFrame({
        "Column": df.columns,
        "Missing Values": df.isnull().sum().values
    })

    st.dataframe(
        missing_df,
        use_container_width=True
    )
    
    # -----------------------------
    # Generate SQL schema--added this for phase 3
    # -----------------------------

    schema_df = pd.DataFrame({
        "Column": df.columns,
        "Pandas Type": [
            str(dtype)
            for dtype in df.dtypes
        ],
        "SQL Type": [
            get_sql_type(dtype)
            for dtype in df.dtypes
        ]
    })


    st.subheader("Detected SQL Schema")

    st.dataframe(
        schema_df,
        use_container_width=True
    )
    # -----------------------------
    # Create LLM schema context
    # -----------------------------

    schema_text = f"Table: uploaded_data\n\nColumns:\n"

    for column in df.columns:
        sql_type = get_sql_type(df[column].dtype)
        schema_text += f"- {column}: {sql_type}\n"

    # -----------------------------
    # DuckDB
    # -----------------------------

    con = duckdb.connect()

    con.register(
        "uploaded_data",
        df
    )


    # -----------------------------
    # SQL validation
    # -----------------------------

    def validate_sql(sql):

        sql = sql.strip().lower()

        if not sql.startswith(("select", "with")):
            return False

        forbidden_keywords = [
            "drop",
            "delete",
            "update",
            "insert",
            "alter",
            "create",
            "truncate",
            "replace"
        ]

        for keyword in forbidden_keywords:

            if f" {keyword} " in f" {sql} ":
                return False

        return True


    # -----------------------------
    # Phase 4: Ask Gemini
    # -----------------------------

    st.subheader("Ask a Question About Your Data")

    user_question = st.text_input(
        "Enter your question:",
        placeholder="Example: What is the average price for each region?"
    )


    if st.button("Generate SQL"):

        if not user_question.strip():

            st.warning("Please enter a question first.")

        else:

            prompt = f"""
    You are a SQL assistant.

    Generate one valid DuckDB SQL SELECT query for the user's question.

    Use only this table and these columns:

    {schema_text}

    User question:

    {user_question}

    Rules:
    - Return SQL only.
    - Use table name uploaded_data.
    - Generate exactly one read-only SELECT query.
    - Do not use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, or multiple statements.
    """

            try:

                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt
                )

                generated_sql = response.text.strip()

                # Remove Markdown fences if Gemini includes them
                generated_sql = generated_sql.replace("`sql", "").replace("`", "").strip()

                st.subheader("Generated SQL")
                st.code(generated_sql,language="sql")

                # Validate SQL
                if not validate_sql(generated_sql):

                    st.error("Invalid or unsafe SQL query.")

                else:

                    # Execute Gemini SQL in DuckDB
                    result = con.execute(
                        generated_sql
                    ).df()

                    st.subheader("SQL Result")

                    st.dataframe(
                        result,
                        use_container_width=True
                    )

            except Exception as error:

                st.error(
                    f"Query could not be executed: {error}"
                )


    con.close()