
import pandas as pd

def run_audit_checks(transactions, employees):

    df = transactions.copy()
    emp = employees.copy()

    df["transaction_date"] = pd.to_datetime(df["transaction_date"])

    # Join employee approval limits
    approval_limits = emp.set_index("employee_id")["approval_limit"]

    df["approver_limit"] = df["approved_by"].map(approval_limits)

    findings = []

    for _, row in df.iterrows():

        transaction_id = row["transaction_id"]

        # Rule 1: Duplicate invoice/payment
        duplicate = (
            df["invoice_id"].eq(row["invoice_id"])
            & df["vendor_id"].eq(row["vendor_id"])
        ).sum() > 1

        if duplicate:
            findings.append({
                "transaction_id": transaction_id,
                "rule": "Duplicate Payment",
                "description": "Invoice and vendor combination appears more than once.",
                "points": 40
            })

        # Rule 2: Missing approval for high-value payments
        if row["amount"] > 50000 and pd.isna(row["approved_by"]):
            findings.append({
                "transaction_id": transaction_id,
                "rule": "Missing Approval",
                "description": "Payment above ₹50,000 has no recorded approver.",
                "points": 35
            })

        # Rule 3: Approval limit violation
        if (
            pd.notna(row["approved_by"])
            and pd.notna(row["approver_limit"])
            and row["amount"] > row["approver_limit"]
        ):
            findings.append({
                "transaction_id": transaction_id,
                "rule": "Approval Limit Violation",
                "description": "Payment exceeds the approver's authorization limit.",
                "points": 35
            })

        # Rule 4: Missing invoice documentation
        if not bool(row["invoice_attached"]):
            findings.append({
                "transaction_id": transaction_id,
                "rule": "Missing Documentation",
                "description": "Supporting invoice document is missing.",
                "points": 15
            })

        # Rule 5: Segregation of duties
        if (
            pd.notna(row["approved_by"])
            and row["created_by"] == row["approved_by"]
        ):
            findings.append({
                "transaction_id": transaction_id,
                "rule": "Segregation of Duties Violation",
                "description": "The same employee created and approved the payment.",
                "points": 35
            })

    findings_df = pd.DataFrame(findings)

    if findings_df.empty:
        return findings_df

    return findings_df.drop_duplicates(
        subset=["transaction_id", "rule"]
    ).reset_index(drop=True)


def calculate_risk_scores(transactions, findings):

    scores = (
        findings.groupby("transaction_id")["points"]
        .sum()
        .rename("risk_score")
    )

    result = transactions.copy()
    result = result.merge(
        scores,
        on="transaction_id",
        how="left"
    )

    result["risk_score"] = result["risk_score"].fillna(0).clip(upper=100)

    result["risk_level"] = pd.cut(
        result["risk_score"],
        bins=[-1, 19, 39, 69, 100],
        labels=["Low", "Medium", "High", "Critical"]
    ).astype(str)

    return result
