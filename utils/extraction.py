import pandas as pd

def extract_features(json_data):
    df = pd.DataFrame(json_data)

    
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')

    
    df['amount'] = pd.to_numeric(df['actionData'].apply(lambda x: x.get('amount', 0)), errors='coerce')
    df['usd_price'] = pd.to_numeric(df['actionData'].apply(lambda x: x.get('assetPriceUSD', 0)), errors='coerce')

    
    df['usd_value'] = df['amount'] * df['usd_price']

    
    action_dummies = pd.get_dummies(df['action'], prefix='action')
    df = pd.concat([df, action_dummies], axis=1)

    
    expected_actions = [
        'action_deposit',
        'action_borrow',
        'action_repay',
        'action_redeemunderlying',
        'action_liquidationcall'
    ]
    for col in expected_actions:
        if col not in df.columns:
            df[col] = 0

   
    features = df.groupby('userWallet').agg({
        'amount': ['count', 'sum', 'mean', 'max'],
        'usd_value': ['sum', 'mean'],
        'datetime': ['min', 'max'],
        'action_deposit': 'sum',
        'action_borrow': 'sum',
        'action_repay': 'sum',
        'action_redeemunderlying': 'sum',
        'action_liquidationcall': 'sum'
    })

    
    features.columns = ['_'.join(col).strip() for col in features.columns.values]

    
    features['active_days'] = (features['datetime_max'] - features['datetime_min']).dt.days + 1

    
    features['deposit_borrow_ratio'] = features['action_deposit_sum'] / (features['action_borrow_sum'] + 1)

    
    features = features.fillna(0).reset_index()

    return features
