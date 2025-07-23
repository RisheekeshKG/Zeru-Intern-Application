import pandas as pd
import json
from extraction import extract_features 


def compute_credit_score(row):
    score = 500
    score += min(row["usd_value_sum"] / 1000, 200)
    score += min(row["action_repay_sum"] * 10, 150)
    score -= row["action_liquidationcall_sum"] * 100
    score -= min(row["action_borrow_sum"] * 5, 150)
    score += min(row["active_days"], 100)
    score += min(row["amount_count"], 50)
    score += min(row["deposit_borrow_ratio"] * 10, 100)
    return max(0, min(1000, score))

if __name__ == "__main__":
    input_json_path = "data/test.json"
    output_csv_path = "data/scored_from_json.csv"

    with open(input_json_path, 'r') as f:
        raw_data = json.load(f)

   
    features_df = extract_features(raw_data)
    features_df["score"] = features_df.apply(compute_credit_score, axis=1)

    features_df.to_csv(output_csv_path, index=False)
    print(features_df[["userWallet", "score"]].head())
