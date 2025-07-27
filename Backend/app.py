from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import ta # Import the 'ta' library
import os # Import os module for path manipulation

# Determine the absolute path to the directory where app.py is located (e.g., E:\my_python_envs\scripts\Backend)
basedir = os.path.abspath(os.path.dirname(__file__))

# Construct the path to the Frontend folder
# Assuming 'Frontend' is a sibling directory to 'Backend' (e.g., both inside 'scripts')
# So, from 'Backend', we go up one level (..) and then into 'Frontend'
frontend_folder = os.path.join(os.path.dirname(basedir), 'Frontend')

# Initialize Flask app, specifying the template_folder and static_folder
# Flask will look for HTML files (templates) in template_folder
# and static assets (like CSS, JS, images) in static_folder
app = Flask(__name__,
            template_folder=frontend_folder,
            static_folder=frontend_folder) # Point static_folder to frontend as well for simplicity

CORS(app)

# Load your trained ROC prediction model
try:
    model = joblib.load(os.path.join(basedir, "roc_model.pkl")) # Ensure model path is correct relative to app.py
    print("Model 'roc_model.pkl' loaded successfully.")
except FileNotFoundError:
    print("Error: 'roc_model.pkl' not found. Make sure the model file is in the same directory as app.py.")
    model = None
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Define ALL 18 required features - MUST match exactly what your model was trained on.
required_features = [
    'close_t-1', 'volume_t-1', 'sma_10', 'sma_50', 'rsi', 'macd',
    'macd_signal', 'bollinger_high', 'bollinger_low', 'day_of_week', 'month',
    'close_t-2', 'volume_t-2', 'close_t-3', 'volume_t-3', 'ema_10', 'atr', 'obv'
]

# --- Routes to serve frontend files from the 'Frontend' folder ---

# Route for the main page (index.html)
@app.route('/')
def serve_index():
    # Flask will automatically serve index.html from the configured template_folder
    return send_from_directory(app.template_folder, 'index.html')

# Route for the mainpage.html (if used for other projects)
@app.route('/mainpage.html')
def serve_mainpage():
    return send_from_directory(app.template_folder, 'mainpage.html')

# Routes for other static files (CSS, JS)
# Since static_folder is set to frontend_folder, these can be accessed directly by their names
# if they are at the root of the frontend_folder.
@app.route('/style.css')
def serve_css():
    return send_from_directory(app.static_folder, 'style.css')

@app.route('/script.js')
def serve_js():
    return send_from_directory(app.static_folder, 'script.js')

# If you have images in the Frontend folder that your CSS or HTML references,
# you'll need a route for them too, or ensure your CSS references them relative to style.css
# For example, if you have 'image.png' in Frontend:
# @app.route('/image.png')
# def serve_image():
#     return send_from_directory(app.static_folder, 'image.png')


# Utility: Generate features for a given stock and date
def prepare_features(symbol, date_str):
    """
    Fetches historical stock data, calculates technical indicators,
    and prepares features for prediction for a given symbol and date.
    """
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        # Fetch enough historical data to calculate all indicators (e.g., 60 days for SMA_50, ATR)
        # A period of 250 days should be sufficient for most indicators and lagged features.
        start_date = date - timedelta(days=250) # Increased lookback to 250 days
        end_date_str = (date + timedelta(days=1)).strftime("%Y-%m-%d") # Fetch up to the day AFTER the target date for 'yfinance'

        # Adjust symbol for yfinance for Indian stocks (e.g., RELIANCE.NS)
        if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
            yfinance_symbol = f"{symbol}.NS"
        else:
            yfinance_symbol = symbol

        df = yf.download(yfinance_symbol, start=start_date.strftime("%Y-%m-%d"), end=end_date_str)

        # --- DEBUGGING PRINTS (Initial df state) ---
        print(f"\n--- Debugging yfinance.download() for {yfinance_symbol} from {start_date.strftime('%Y-%m-%d')} to {end_date_str} ---")
        print("DataFrame Head (Raw):")
        print(df.head())
        print("DataFrame Columns (Before Flattening/Lowercasing):")
        print(df.columns)
        print("DataFrame Shape (Raw):", df.shape)
        print("----------------------------------------------------------------------------------------------------")
        # --- END DEBUGGING PRINTS ---

        if df.empty:
            print(f"No data found for {yfinance_symbol} from {start_date.strftime('%Y-%m-%d')} to {end_date_str}.")
            return None

        # FIX: Handle MultiIndex columns returned by yfinance and flatten them
        if isinstance(df.columns, pd.MultiIndex):
            # Take the first level of the MultiIndex (e.g., 'Close' from ('Close', 'RELIANCE.NS'))
            df.columns = [col[0].lower() if isinstance(col, tuple) else str(col).lower() for col in df.columns.values]
        else:
            # If not MultiIndex, just convert to lowercase strings
            df.columns = [str(col).lower() for col in df.columns]

        # --- DEBUGGING PRINTS (After column flattening) ---
        print("DataFrame Columns (After Flattening/Lowercasing):")
        print(df.columns)
        print("DataFrame dtypes (After Flattening/Lowercasing):")
        print(df.dtypes) # Check dtypes here
        print("----------------------------------------------------------------------------------------------------")
        # --- END DEBUGGING PRINTS ---


        # Ensure 'close', 'high', 'low', 'open', and 'volume' columns exist before proceeding
        # These are fundamental for all other calculations
        if not all(col in df.columns for col in ['close', 'high', 'low', 'open', 'volume']):
            print(f"Missing fundamental OHLCV columns in fetched data for {yfinance_symbol}. Columns found: {list(df.columns)}")
            return None

        # Ensure fundamental OHLCV columns are numeric
        for col in ['close', 'high', 'low', 'open', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df.dropna(subset=['close', 'high', 'low', 'open', 'volume'], inplace=True)

        if df.empty:
            print(f"DataFrame became empty after ensuring OHLCV are numeric and dropping NaNs.")
            return None

        # Calculate Lag Features (up to t-3 as per required_features)
        df['close_t-1'] = df['close'].shift(1)
        df['close_t-2'] = df['close'].shift(2)
        df['close_t-3'] = df['close'].shift(3)
        df['volume_t-1'] = df['volume'].shift(1)
        df['volume_t-2'] = df['volume'].shift(2)
        df['volume_t-3'] = df['volume'].shift(3)

        print("DataFrame Columns (After Lag Features):")
        print(df.columns)
        print("DataFrame Tail (After Lag Features):")
        print(df.tail())
        print("----------------------------------------------------------------------------------------------------")

        # Technical Indicators (using 'ta' library logic from notebook)
        # Check if there's enough data for indicator calculation (e.g., for SMA_50, Bollinger, ATR)
        # If not enough data, these will produce NaNs, which will be handled by dropna() later.
        if len(df) < 50: # SMA_50 needs at least 50 data points, ATR/Bollinger need ~20
            print(f"Warning: Raw data length ({len(df)} rows) might be insufficient for all indicators for {yfinance_symbol}.")

        df['sma_10'] = ta.trend.sma_indicator(df['close'], window=10)
        df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50)
        df['rsi'] = ta.momentum.rsi(df['close'], window=14)
        df['macd'] = ta.trend.macd(df['close'])
        df['macd_signal'] = ta.trend.macd_signal(df['close'])
        
        bollinger = ta.volatility.BollingerBands(close=df['close'], window=20, window_dev=2)
        df['bollinger_high'] = bollinger.bollinger_hband()
        df['bollinger_low'] = bollinger.bollinger_lband()

        df['obv'] = ta.volume.on_balance_volume(df['close'], df['volume'])
        df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=14)
        df['ema_10'] = ta.trend.ema_indicator(df['close'], window=10)


        print("DataFrame Columns (After Technical Indicators):")
        print(df.columns)
        print("DataFrame Tail (After Technical Indicators):")
        print(df.tail())
        print("----------------------------------------------------------------------------------------------------")

        # Date Features
        df['day_of_week'] = df.index.dayofweek # index is datetime
        df['month'] = df.index.month

        print("DataFrame Columns (After Date Features):")
        print(df.columns)
        print("DataFrame Tail (After Date Features):")
        print(df.tail())
        print("----------------------------------------------------------------------------------------------------")

        # Select the row for the prediction date
        target_date_dt = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # Crucially, we now drop NaNs *after* feature calculation, and only for the required features
        # This will create a DataFrame with only the required columns and no NaNs in them.
        df_with_features = df[required_features].dropna()

        print("DataFrame Head (df_with_features after dropna()):")
        print(df_with_features.head())
        print("DataFrame Columns (df_with_features after dropna()):")
        print(df_with_features.columns)
        print("DataFrame Shape (df_with_features after dropna()):", df_with_features.shape)
        print("----------------------------------------------------------------------------------------------------")

        # Filter for dates <= target_date_dt and get the latest valid row
        df_filtered_for_target = df_with_features[df_with_features.index.date <= target_date_dt].sort_index(ascending=False)

        if df_filtered_for_target.empty:
            print(f"No sufficient data with all required features to prepare for {symbol} on {date_str}.")
            print(f"Columns in df_with_features before date filter: {list(df_with_features.columns)}")
            print(f"Last few rows of df_with_features before date filter:\n{df_with_features.tail()}")
            return None

        features_row = df_filtered_for_target.iloc[0]

        missing_features = [f for f in required_features if f not in features_row.index]
        if missing_features:
            print(f"Error: Missing required features in prepared data: {missing_features}. This should not happen after dropna(). Available: {list(features_row.index)}")
            return None

        prepared_features = pd.DataFrame([features_row[required_features].values], columns=required_features)

        if prepared_features.isnull().values.any():
            print(f"Critical Warning: NaN values still found in prepared features for {symbol} on {date_str} after dropna().")
            return None

        return prepared_features

    except Exception as e:
        print(f"Error in prepare_features for {symbol} on {date_str}: {e}")
        import traceback
        traceback.print_exc() # Print full traceback for prepare_features errors
        return None

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model not loaded. Check server logs for details.'}), 500

    try:
        data = request.get_json()
        company_symbol = data['companySymbol'].strip().upper()
        prediction_date_str = data['predictionDate']

        features = prepare_features(company_symbol, prediction_date_str)

        if features is None:
            return jsonify({'error': f'Could not prepare features for {company_symbol} on {prediction_date_str}. '
                                     'This could be due to invalid symbol, date, or insufficient historical data.'}), 400

        if list(features.columns) != required_features:
            print(f"Feature mismatch! Expected: {required_features}, Got: {list(features.columns)}")
            return jsonify({'error': 'Feature mismatch. Server configuration error.'}), 500

        prediction = model.predict(features)[0]

        if not company_symbol.endswith('.NS') and not company_symbol.endswith('.BO'):
            yfinance_symbol = f"{company_symbol}.NS"
        else:
            yfinance_symbol = company_symbol

        fetch_start_date = datetime.strptime(prediction_date_str, "%Y-%m-%d") - timedelta(days=10)
        fetch_end_date = datetime.strptime(prediction_date_str, "%Y-%m-%d")
        
        prev_day_data = yf.download(yfinance_symbol, start=fetch_start_date.strftime("%Y-%m-%d"), end=fetch_end_date.strftime("%Y-%m-%d"))

        if prev_day_data.empty:
            return jsonify({'error': f'Could not retrieve previous day\'s closing price for {company_symbol}. Insufficient data for price conversion.'}), 400

        # Get the last available closing price before the prediction date
        # Filter for dates strictly before the prediction date, then get the last one
        prev_day_close_price_series = prev_day_data[prev_day_data.index.date < datetime.strptime(prediction_date_str, "%Y-%m-%d").date()]['Close']
        
        if prev_day_close_price_series.empty:
            # If no data strictly before, take the last available close up to the prediction date
            prev_day_close_price = prev_day_data['Close'].iloc[-1]
            print(f"Warning: No close price strictly before {prediction_date_str}. Using last available close on or before it: {prev_day_close_price}")
        else:
            prev_day_close_price = prev_day_close_price_series.iloc[-1]

        # Ensure prev_day_close_price is a scalar float before calculation
        if isinstance(prev_day_close_price, pd.Series):
            prev_day_close_price = prev_day_close_price.item() # Extract scalar from Series

        estimated_price = float(prev_day_close_price) * (1 + prediction / 100) # Ensure it's float for calculation

        return jsonify({'companySymbol': company_symbol, 'predictionDate': prediction_date_str, 'estimatedPrice': estimated_price})

    except Exception as e:
        print(f"An error occurred during prediction: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error predicting stock price: {e}. Check server logs for details.'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

