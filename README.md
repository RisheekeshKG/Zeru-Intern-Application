# DeFi Credit Scoring — Aave V2 Transactions Data (Zeru Intern)

##  Introduction

This project is about building a credit scoring system for wallets based on their behavior on the Aave V2 protocol.

By using 100K+ raw transaction records in JSON format. I assigned each wallet a **credit score between 0 and 1000**

by using my own heuristic function logic to train a model which can predict further new data.

## Method Chosen

Since no labeled data or real-world credit scores were provided, I chose a **hybrid approach** combining multiple techniques to simulate realistic scoring and train a predictive model.

---

### 1. Rule-Based Scoring (For Generating Training Labels)

I manually designed a scoring system based on domain knowledge and behavioral assumptions commonly used in lending/credit scoring. Each wallet was evaluated based on:

- **Repayment behavior** (positive impact)  
- **Liquidation events** (negative impact)  
- **Deposit-to-borrow ratio** (positive impact)  
- **Active time and frequency** (positive impact)  
- **Overall transaction volume** (positive impact)  

Each of these features contributed proportionally to a score between 0 and 1000.

> Further insights and graphs regarding this scoring logic are documented in `analysis.md` and core logic in `utils/score_applier.py`.

This rule-based approach ensures interpretability and transparency — anyone can understand and trace how the score is computed.

---

### 2. Feature Extraction: JSON ➝ CSV

The original raw data was provided in nested **JSON** format. I built a robust parser under `utils/extraction.py` to:

- Flatten and aggregate per-wallet transaction records  
- Derive features like action frequency, usd value, deposit/borrow ratios, etc.  
- Output a clean **wallet-level CSV** file suitable for training and inference  

This feature pipeline is used both during training and live scoring.

---

### 3. ML Model (XGBoost Regression)

To generalize and fine-tune the scoring process, I trained an **XGBoost regression model** using the pseudo-labels generated from the rule-based system.

Benefits of using XGBoost:

- Learns non-linear relationships between features  
- Handles feature interactions better  
- Robust to noisy or missing data  
- Provides feature importance metrics  

> It outperformed other models like RandomForest in both RMSE and score stability (see `/notebooks/model.ipynb` for comparison results).

The model was trained on the output of the feature extractor and score applier saved in `features_with_score.csv`.

---

### 4. One-Step Wallet Scoring Script

All the logic is packaged into a single Python script that:

- Reads the raw JSON transaction file  
- Extracts and processes features  
- Applies the trained XGBoost model  
- Outputs credit scores in CSV format  

Script :

```bash
python main.py --input data/testing/test.json --output output/output.csv
```

###  Processing Flow 

1. **Read Input JSON**
   - Loads user-level raw transaction data using `json.load`.

2. **Feature Engineering**
   - Calls `extract_features(raw_data)` from `utils/extraction.py`
   - Returns a DataFrame where each row is a wallet and each column is a feature.

3. **Preprocess for Inference**
   - Drops non-feature columns like `userWallet`, `datetime_min`, and `datetime_max`.

4. **Load XGBoost Model**
   - Intializing `XGBRegressor()` and loads weights from `.json` file (which i already trained and saved as `models/xgboost.json`).

5. **Predict Scores**
   - Performs inference, clips scores to the [0, 1000] range.
   - Applies `round(2)` to format nicely.

6. **Save Output**
   - Saves result as `output_file.csv` with columns:
     - `userWallet`
     - `creditScore`

7. **CLI Arguments**
   - `--input`: Path to the JSON input
   - `--output`: Output CSV file (default: `output/scored_wallets.csv`)
   - `--model`: Optional model path (default: `models/xgboost_model.json`)

---

###  Output

- CSV file with wallet addresses and predicted credit scores:
```csv
userWallet,creditScore
0xabc123...,732.65
0xdef456...,589.21
...
```

---

## File structure 

```

├── 📁 data/
│   ├── 📁 assets/                     # Contains images for analysis.md
│   │   └── image1.png ... image8.png
│   ├── 📁 testing/                    # Test files for model evaluation
│   │   ├── test.json
│   │   └── predicted_scores.csv
│   ├── features_with_score.csv         # Pseudo-labeled data used for model training
│   ├── features.csv                    # Extracted features without score
│   └── user-wallet-transactions.json   # Original raw JSON file
│
├── 📁 models/
│   └── xgboost_model.json              # Trained XGBoost model (JSON format)
│
├── 📁 notebooks/
│   ├── EDA_and_Graphs.ipynb            # Exploratory Data Analysis and visualizations
│   └── model.ipynb                     # Model training, comparison, tuning
│
├── 📁 output/
│   └── output.csv                      # Final output with wallet-wise predicted credit scores
│
├── 📁 utils/
│   ├── extraction.py                   # JSON → Feature extraction logic
│   └── score_applier.py                # Applies rule-based scoring logic (only for training)
│
├── 📄 main.py                          # One-step script to run the prediction pipeline
├── 📄 README.md                        # Full project overview and instructions
└── 📄 analysis.md                      # Score distribution, behavioral insights, feature impact

```

### System Architecture

![alt text](data\assets\image9.png)


### My opinions or changes i would like to bring :

#### Incorporate Explainable AI (XAI):
We can enhance transparency and trust in the OCCR Score by using deep learning models (e.g., neural networks or transformer-based models) alongside Explainable AI techniques like SHAP or LIME. This would help users and developers understand which specific features or behaviors contributed to a wallet's high or low score, making the system more interpretable.

#### Benchmark Against Industry Scoring Models:
Instead of relying solely on self-designed heuristics, we can study and compare our OCCR logic with existing DeFi credit scoring models. This will allow us to adopt proven patterns and improve the realism and robustness of our own scoring logic.

#### Dynamic Feature Weighting:
Introduce adaptive scoring rules where the importance of features (e.g., repayment ratio, liquidation frequency) changes depending on market conditions or protocol-specific behaviors. This would help make the score more resilient to volatility and protocol-specific quirks.

