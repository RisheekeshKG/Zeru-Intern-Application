import pandas as pd
import xgboost as xgb
import json
import argparse
from utils.extraction import extract_features

def predict_scores(json_input_file, output_file, model_file="models/xgboost_model.json"):

    with open(json_input_file, 'r') as f:
        raw_data = json.load(f)

    features = extract_features(raw_data)
    wallets = features['userWallet']

    X = features.drop(columns=['userWallet', 'datetime_min', 'datetime_max'], errors='ignore')


    model = xgb.XGBRegressor()
    model.load_model(model_file)

    scores = model.predict(X).clip(0, 1000)

    result_df = pd.DataFrame({
        'userWallet': wallets,
        'creditScore': scores.round(2)
    })


    result_df.to_csv(output_file, index=False)
    print(f"Credit scores saved to: {output_file}")

parser = argparse.ArgumentParser(description="Generate credit scores for wallets.")
parser.add_argument("--input", type=str, required=True, help="Path to input JSON file")
parser.add_argument("--output", type=str, default="output/scored_wallets.csv", help="Path to save output CSV")
parser.add_argument("--model", type=str, default="models/xgboost_model.json", help="Path to trained XGBoost model")
args = parser.parse_args()

predict_scores(args.input, args.output, args.model)
