
import streamlit as st
import pandas as pd
import plotly.express as px

from src.database import load_data, update_investigation

st.set_page_config(
    page_title="AuditLens",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 AuditLens")
st.caption("Internal Audit & Financial Control Testing Dashboard")

st.info(
    "Demonstration project using synthetic financial transactions. "
    "Flagged transactions are exceptions for investigation, not proof of fraud."
)

# Load data
try:
    transactions = load_data("""
        SELECT
            t.*,
            i.status,
            i.notes
        FROM transactions t
        LEFT JOIN investigations i
        ON t.transaction_id = i.transaction_id
    """)

    findings = load_data("SELECT * FROM findings")

except Exception as e:
    st.error(f"Could not load database: {e}")
    st.stop()

if transactions.empty:
    st.warning("No transaction data found. Generate and save the data first.")
    st.stop()

transactions["status"] = transactions["status"].fillna("Open")
transactions["notes"] = transactions["notes"].fillna("")

# Sidebar
st.sidebar.header("Filters")

risk_options = ["Low", "Medium", "High", "Critical"]

selected_risks = st.sidebar.multiselect(
    "Risk level",
    risk_options,
    default=risk_options
)

selected_status = st.sidebar.multiselect(
    "Investigation status",
    ["Open", "Under Review", "Resolved"],
    default=["Open", "Under Review", "Resolved"]
)

search = st.sidebar.text_input("Search transaction or vendor")

filtered = transactions[
    transactions["risk_level"].isin(selected_risks)
    & transactions["status"].isin(selected_status)
].copy()

if search:
    filtered = filtered[
        filtered["transaction_id"].str.contains(search, case=False, na=False)
        | filtered["vendor_id"].str.contains(search, case=False, na=False)
        | filtered["invoice_id"].str.contains(search, case=False, na=False)
    ]

# Metrics
total = len(transactions)
exceptions = int((transactions["risk_score"] > 0).sum())
critical = int((transactions["risk_level"] == "Critical").sum())
open_cases = int((transactions["status"] == "Open").sum())

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Transactions", f"{total:,}")
c2.metric("Transactions with Findings", f"{exceptions:,}")
c3.metric("Critical Risk", f"{critical:,}")
c4.metric("Open Investigations", f"{open_cases:,}")

st.divider()

# Charts
left, right = st.columns(2)

with left:
    risk_counts = (
        transactions["risk_level"]
        .value_counts()
        .reindex(risk_options, fill_value=0)
        .reset_index()
    )
    risk_counts.columns = ["Risk Level", "Transactions"]

    fig = px.bar(
        risk_counts,
        x="Risk Level",
        y="Transactions",
        title="Transaction Risk Distribution",
        color="Risk Level"
    )

    st.plotly_chart(fig, use_container_width=True)

with right:
    rule_counts = (
        findings["rule"]
        .value_counts()
        .reset_index()
    )
    rule_counts.columns = ["Audit Rule", "Count"]

    fig = px.bar(
        rule_counts,
        x="Count",
        y="Audit Rule",
        orientation="h",
        title="Audit Findings by Rule"
    )

    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Transaction table
st.subheader("Transaction Audit Register")

display_columns = [
    "transaction_id",
    "invoice_id",
    "vendor_id",
    "amount",
    "risk_score",
    "risk_level",
    "status"
]

st.dataframe(
    filtered[display_columns],
    use_container_width=True,
    hide_index=True
)

# Export
csv_data = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download filtered transactions CSV",
    data=csv_data,
    file_name="auditlens_transactions.csv",
    mime="text/csv"
)

st.divider()

# Investigation section
st.subheader("Investigation Workspace")

transaction_ids = filtered[
    filtered["risk_score"] > 0
]["transaction_id"].tolist()

if transaction_ids:

    selected_id = st.selectbox(
        "Select transaction",
        transaction_ids
    )

    selected_row = transactions[
        transactions["transaction_id"] == selected_id
    ].iloc[0]

    st.write("**Transaction details**")

    st.json({
        "Transaction ID": selected_row["transaction_id"],
        "Invoice ID": selected_row["invoice_id"],
        "Vendor ID": selected_row["vendor_id"],
        "Amount": float(selected_row["amount"]),
        "Risk Score": float(selected_row["risk_score"]),
        "Risk Level": selected_row["risk_level"]
    })

    transaction_findings = findings[
        findings["transaction_id"] == selected_id
    ]

    st.write("**Audit exceptions identified**")

    if not transaction_findings.empty:
        st.dataframe(
            transaction_findings[
                ["rule", "description", "points"]
            ],
            use_container_width=True,
            hide_index=True
        )

    with st.form("investigation_form"):

        current_status = selected_row["status"]

        status_options = [
            "Open",
            "Under Review",
            "Resolved"
        ]

        default_index = (
            status_options.index(current_status)
            if current_status in status_options
            else 0
        )

        new_status = st.selectbox(
            "Investigation status",
            status_options,
            index=default_index
        )

        notes = st.text_area(
            "Investigation notes",
            value=selected_row["notes"]
        )

        submitted = st.form_submit_button("Save Investigation")

        if submitted:
            update_investigation(
                selected_id,
                new_status,
                notes
            )

            st.success("Investigation updated successfully!")
            st.rerun()

else:
    st.info("No flagged transactions match the selected filters.")

st.divider()

st.caption(
    "AuditLens | Educational Internal Audit Analytics Prototype | "
    "Synthetic Dataset"
)
