# Import required libraries
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

def load_data(ticker, period='2y'):
    """Fetch stock data from Yahoo Finance"""
    data = yf.Ticker(ticker).history(period=period)
    return data

def create_features(data):
    """Create technical indicators and features"""
    df = data.copy()

    df['Price_Change'] = df['Close'].pct_change()

    df['MA_5'] = df['Close'].rolling(window=5).mean()
    df['MA_20'] = df['Close'].rolling(window=20).mean()

    df['Volatility'] = df['Close'].rolling(window=20).std()

    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    
    return df.dropna()

def prepare_data(df):
    """Prepare features and target variable"""
    features = ['Price_Change', 'MA_5', 'MA_20', 'Volatility', 'RSI']
    X = df[features]
    y = df['Target']
    return X, y

def train_model(X, y):
    """Train Random Forest classifier"""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=False
    )
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    

    y_pred = model.predict(X_test)

    print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    return model, X_test, y_test


if __name__ == "__main__":

    ticker = "AAPL"  
    data = load_data(ticker)

    df = create_features(data)
    

    X, y = prepare_data(df)
    
  
    model, X_test, y_test = train_model(X, y)
  
    feature_importance = pd.Series(model.feature_importances_, index=X.columns)
    print("\nFeature Importance:")
    print(feature_importance.sort_values(ascending=False))