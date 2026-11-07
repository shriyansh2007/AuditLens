
import pandas as pd
import numpy as np
from pathlib import Path

def generate_data(output_dir="data", n=1000, seed=42):

    np.random.seed(seed)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    employees = []

    roles = {
        "Analyst": 0,
        "Supervisor": 50000,
        "Manager": 200000,
        "Director": 1000000
    }

    for i in range(1, 26):
        role = np.random.choice(
            list(roles.keys()),
            p=[0.40, 0.28, 0.24, 0.08]
        )

        employees.append({
            "employee_id": f"E{i:03}",
            "role": role,
            "approval_limit": roles[role]
        })

    employees_df = pd.DataFrame(employees)

    employee_ids = employees_df["employee_id"].tolist()

    vendors = [f"V{i:03}" for i in range(1, 101)]

    transactions = []

    for i in range(1, n + 1):

        creator = np.random.choice(employee_ids)
        approver = np.random.choice(employee_ids)

        amount = round(np.random.uniform(1000, 250000), 2)

        transactions.append({
            "transaction_id": f"TX{i:05}",
            "invoice_id": f"INV{i:05}",
            "vendor_id": np.random.choice(vendors),
            "transaction_date": pd.Timestamp("2026-01-01")
                + pd.Timedelta(days=int(np.random.randint(0, 300))),
            "amount": amount,
            "created_by": creator,
            "approved_by": approver,
            "invoice_attached": np.random.choice([True, False], p=[0.95, 0.05]),
            "payment_reference": f"PAY{i:05}"
        })

    df = pd.DataFrame(transactions)

    # Inject duplicate payments
    for i in [100, 250, 400, 600, 800]:
        df.loc[i, "invoice_id"] = df.loc[i-1, "invoice_id"]
        df.loc[i, "vendor_id"] = df.loc[i-1, "vendor_id"]
        df.loc[i, "amount"] = df.loc[i-1, "amount"]

    # Inject missing approvals for high-value payments
    for i in [120, 300, 500, 700]:
        df.loc[i, "amount"] = 150000
        df.loc[i, "approved_by"] = None

    # Inject missing invoices
    for i in [150, 350, 550, 750]:
        df.loc[i, "invoice_attached"] = False

    # Inject segregation-of-duties violations
    for i in [180, 380, 580, 780]:
        df.loc[i, "approved_by"] = df.loc[i, "created_by"]

    # Inject approval limit violations
    for i in [200, 450, 650, 850]:
        low_authority = employees_df[
            employees_df["role"] == "Supervisor"
        ]["employee_id"].iloc[0]

        df.loc[i, "amount"] = 180000
        df.loc[i, "approved_by"] = low_authority

    df.to_csv(f"{output_dir}/transactions.csv", index=False)
    employees_df.to_csv(f"{output_dir}/employees.csv", index=False)

    print("Synthetic data generated successfully!")
    print("Transactions:", len(df))
    print("Employees:", len(employees_df))

    return df, employees_df


if __name__ == "__main__":
    generate_data()
