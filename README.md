 Duka Sales Exploration & Mobile Money Agent Data Cleanup

This repository contains the completed workflows for **Engagement 1 (Duka Electronics Sales Exploration)** and **Engagement 2 (Mobile Money Agent Network Data Cleaning & Governance)**, built in Python (`pandas`) on Google Colab with spreadsheet verification and privacy controls aligned with the **Kenya Data Protection Act, 2019**.
 Notebooks & Repository Structure
Data Exploration Notebook (`duka_sales_exploration.ipynb`):** [Open in Google Colab](https://colab.research.google.com/drive/1_ff9Zfzr6plMdrnH7WFtFQF7DRJA6drM?usp=sharing)
  Agent Cleanup Notebook (`agent_cleanup.ipynb`):** [Open in Google Colab](https://colab.research.google.com/drive/1drvsEVQfL1CFzoLGQDYD8BvVnnKimWVv?usp=sharing)

plp-da-a3-duka-sales-and-agent-cleanup/
├── .gitignore
├── README.md
├── generate_data.py
├── cleaning_pipeline.py
├── duka_sales_exploration.ipynb
├── agent_cleanup.ipynb
├── requirements.txt
├── excel/
│   └── duka_branch_summary.xlsx
└── outputs/
    ├── premium_online_coast_capital.csv
    └── agent_transactions_clean.csv
Summary of Both Engagements
Engagement 1: Duka Electronics Sales Exploration
Explored synthetic retail order data for Duka Electronics across branches, channels, products, dates, and months, pairing pandas analysis with a spreadsheet workbook (excel/duka_branch_summary.xlsx) containing SUMIFS branch totals, an XLOOKUP regional lookup, and a branch × channel revenue PivotTable, plus a filtered export (outputs/premium_online_coast_capital.csv).

Engagement 2: Mobile Money Agent Network Cleanup
Audited, cleaned, and enriched synthetic mobile-money agent transaction records against the agent register (agents.csv) using a modular clean_agent_data(txns, agents) function in cleaning_pipeline.py. The workflow handles deduplication on txn_id, txn_type standardisation, numeric and ISO YYYY-MM-DD date parsing, median-by-type amount imputation with an amount_imputed audit flag, IQR outlier flagging (is_outlier) with investigation of KES 250,000 spikes, a left join on agent_id (labelling unknown agents such as AG099 as "Unknown"), county/weekly summaries, a data quality report, and privacy safeguards under the Kenya Data Protection Act, 2019.

## Executive Summary

* Across the 1,000 orders analyzed from January to June 2026, Duka Electronics generated KES 71,792,500 in total revenue[cite: 1].
* Nairobi leads all branches with [Nairobi revenue] in revenue across [Nairobi orders] orders, while [lowest branch] recorded the lowest revenue at [lowest branch revenue].
* [Top revenue product] leads total sales revenue at [top product revenue], whereas [top volume product] ranks highest by units sold with [top product units] units.
* Weekend orders generated [weekend revenue] across [weekend orders] transactions compared to [weekday revenue] across [weekday orders] weekday orders.
* [Best month] delivered the highest monthly revenue at [best month revenue] versus [worst month] at [worst month revenue] ([percentage difference]% difference), while Premium online orders from Nairobi and Mombasa totaled [filtered count] orders and [filtered revenue].

* Agent Data Before-and-After Row CountMetricCountNotesRaw transactions (agent_transactions.csv)612Generated with generate_data.py (seed 44)Duplicate txn_id rows removed12Removed keeping first occurrence (keep="first")Cleaned transactions (outputs/agent_transactions_clean.csv)600All unique transactions retained (with amount_imputed, is_outlier, and county flags/fields)How to Regenerate Data & Run Each NotebookClone the repository and install dependencies:Bashgit clone [https://github.com/AnnNjeriWangui/plp-da-a3-duka-sales-and-agent-cleanup.git](https://github.com/AnnNjeriWangui/plp-da-a3-duka-sales-and-agent-cleanup.git)
cd plp-da-a3-duka-sales-and-agent-cleanup
pip install -r requirements.txt
(If running in Google Colab, open the notebook links above, upload generate_data.py and requirements.txt if needed, and run !pip install -r requirements.txt.)Regenerate the synthetic datasets:Bashpython generate_data.py
This reproduces the synthetic Duka sales dataset (seed 2026) and the mobile-money agent dataset (agents.csv and agent_transactions.csv, seed 44).Run Engagement 1 (duka_sales_exploration.ipynb):Open duka_sales_exploration.ipynb (or click the Colab link above) and run all cells from top to bottom (Runtime -> Run all in Colab).Verify that outputs/premium_online_coast_capital.csv is generated and matches excel/duka_branch_summary.xlsx.Run Engagement 2 (agent_cleanup.ipynb):Ensure cleaning_pipeline.py is in the same working directory as agent_cleanup.ipynb.Run all cells from top to bottom (Runtime -> Run all in Colab) to audit, clean, flag outliers, merge with agents.csv, generate county/weekly summaries, and write outputs/agent_transactions_clean.csv.
