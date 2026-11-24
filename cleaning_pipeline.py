import numpy as np
import pandas as pd


def clean_agent_data(txns: pd.DataFrame, agents: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    """
    Clean and validate mobile-money agent transactions and merge with the agent register.

    Steps performed:
    1. Deduplicate exact/repeat transactions on `txn_id` (keep first).
    2. Standardise `txn_type` to 'Deposit' and 'Withdrawal'.
    3. Convert `amount` to numeric (coercing invalid tokens like 'N/A' to NaN) and
       `txn_date` to ISO datetime / string format (`YYYY-MM-DD`).
    4. Flag and impute missing `amount` values using median by `txn_type` so
       transaction counts and volume distributions remain unbiased.
    5. Flag statistical outliers in `amount` using the IQR rule (Q3 + 1.5 * IQR)
       without deleting valid high-value transactions.
    6. Left-join `agents` on `agent_id`, labelling unmatched agents ('AG099') as 'Unknown'.

    Parameters
    ----------
    txns : pd.DataFrame
        Raw transaction extract (`agent_transactions.csv`).
    agents : pd.DataFrame
        Agent register (`agents.csv`).

    Returns
    -------
    tuple[pd.DataFrame, list[dict]]
        (clean_df, log) where `clean_df` is the cleaned, merged DataFrame and `log`
        is a structured list of cleaning actions and row counts for governance review.
    """
    df = txns.copy()
    agents_clean = agents.copy()
    log: list[dict] = []

    raw_rows = len(df)
    log.append({"step": "0_load", "action": "Loaded raw transactions", "rows_affected": raw_rows, "remaining_rows": raw_rows})

    # 1. Uniqueness: remove duplicate txn_id rows
    dup_count = int(df.duplicated(subset=["txn_id"]).sum())
    df = df.drop_duplicates(subset=["txn_id"], keep="first").reset_index(drop=True)
    log.append({
        "step": "1_deduplicate",
        "action": "Dropped duplicate txn_id rows (kept first occurrence)",
        "rows_affected": dup_count,
        "remaining_rows": len(df),
    })

    # 2. Consistency: standardise txn_type
    raw_type = df["txn_type"].astype(str)
    clean_type = raw_type.str.strip().str.title()
    non_standard_count = int((raw_type != clean_type).sum())
    df["txn_type"] = clean_type
    valid_types = {"Deposit", "Withdrawal"}
    invalid_type_count = int((~df["txn_type"].isin(valid_types)).sum())
    log.append({
        "step": "2_standardise_txn_type",
        "action": "Trimmed whitespace and applied title case to txn_type ('Deposit', 'Withdrawal')",
        "rows_affected": non_standard_count,
        "remaining_rows": len(df),
    })
    if invalid_type_count > 0:
        log.append({
            "step": "2b_unexpected_txn_type",
            "action": "Found unexpected txn_type values outside Deposit/Withdrawal",
            "rows_affected": invalid_type_count,
            "remaining_rows": len(df),
        })

    # 3. Validity & types: numeric amount and ISO txn_date
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    raw_date_str = df["txn_date"].astype(str).str.strip()
    slash_dates = int(raw_date_str.str.contains("/", regex=False).sum())
    parsed_dates = pd.to_datetime(raw_date_str, format="mixed", errors="coerce")
    df["txn_date"] = parsed_dates.dt.strftime("%Y-%m-%d")
    log.append({
        "step": "3_parse_types",
        "action": "Converted amount to float64 and normalised mixed txn_date formats to ISO YYYY-MM-DD",
        "rows_affected": slash_dates,
        "remaining_rows": len(df),
    })

    # 4. Completeness: flag and impute missing amounts using median by txn_type
    df["amount_imputed"] = df["amount"].isna()
    imputed_count = int(df["amount_imputed"].sum())
    df["amount"] = df["amount"].fillna(df.groupby("txn_type")["amount"].transform("median"))
    log.append({
        "step": "4_impute_amount",
        "action": "Flagged missing/N/A amounts in amount_imputed and imputed with median per txn_type",
        "rows_affected": imputed_count,
        "remaining_rows": len(df),
    })

    # 5. Outliers: IQR rule on amount (flag, do not drop)
    q1 = df["amount"].quantile(0.25)
    q3 = df["amount"].quantile(0.75)
    iqr = q3 - q1
    upper_bound = q3 + 1.5 * iqr
    lower_bound = q1 - 1.5 * iqr
    df["is_outlier"] = (df["amount"] < lower_bound) | (df["amount"] > upper_bound)
    outlier_count = int(df["is_outlier"].sum())
    log.append({
        "step": "5_flag_outliers",
        "action": f"Flagged IQR outliers in is_outlier (bounds: [{lower_bound:.2f}, {upper_bound:.2f}])",
        "rows_affected": outlier_count,
        "remaining_rows": len(df),
    })

    # 6. Referential integrity: left merge with agents register
    agents_clean["agent_id"] = agents_clean["agent_id"].astype(str).str.strip()
    df["agent_id"] = df["agent_id"].astype(str).str.strip()

    merged = pd.merge(
        df,
        agents_clean[["agent_id", "county", "onboarded"]],
        on="agent_id",
        how="left",
    )
    unknown_agent_count = int(merged["county"].isna().sum())
    merged["county"] = merged["county"].fillna("Unknown")
    log.append({
        "step": "6_merge_agents",
        "action": "Left-merged with agents register; filled unmatched agent counties with 'Unknown'",
        "rows_affected": unknown_agent_count,
        "remaining_rows": len(merged),
    })

    return merged, log
