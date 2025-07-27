# **👁️ Stock Sight**

This project is a full-stack web application designed to predict stock prices using a pre-trained machine learning model and provide AI-driven insights. It features a responsive front-end built with HTML, CSS, and JavaScript, communicating with a robust Flask backend that handles data fetching, feature engineering, model inference, and large language model (LLM) integration.

## **✨ Features**

* **Stock Price Prediction:** Predict future stock prices for various companies based on historical data using a LightGBM machine learning model.  
* **Intuitive Web Interface:** A clean and responsive user interface allows users to easily input company symbols and prediction dates.  
* **Flask API Backend:** A powerful Python Flask server serves as the backbone, managing data requests, model predictions, and interactions with external APIs.  
* **Real-time Data Integration:** Utilizes yfinance to fetch real-time and historical stock data.  
* **Technical Analysis (TA) Features:** Incorporates various technical indicators (SMA, RSI, MACD, Bollinger Bands, etc.) as features for enhanced prediction accuracy.  
* **AI Insights & Explanations:** Integrates with a Large Language Model (LLM) to provide insightful analysis and explanations for the stock predictions, enhancing user understanding.  
* **Modern Styling:** Features a visually appealing design with custom CSS, including gradients, animations, and Bootstrap for a consistent look and feel.

## **🚀 Technologies Used**

* **Frontend:**  
  * HTML5  
  * CSS3 (Custom, Bootstrap 5\)  
  * JavaScript (ES6+)  
* **Backend:**  
  * Python 3  
  * Flask (Web Framework)  
  * joblib (Model persistence)  
  * pandas (Data manipulation)  
  * yfinance (Stock data API)  
  * ta (Technical Analysis library)  
  * numpy (Numerical operations)  
  * flask-cors (CORS handling)  
* **Machine Learning:**  
  * LightGBM (Regression Model \- roc\_model3.pkl)  
* **Artificial Intelligence:**  
  * Gemini API (for LLM insights and explanations \- *inferred from script.js*)

## **📦 Project Structure**

.  
├── Backend/              \# Contains Flask application and ML model  
│   ├── app.py            \# Flask backend application  
│   └── roc\_model3.pkl    \# Pre-trained LightGBM machine learning model  
├── Frontend/             \# Contains web interface files  
│   ├── index.html        \# Main frontend HTML file  
│   ├── style.css         \# Custom CSS for the web interface  
│   └── script.js         \# Frontend JavaScript logic  
├── README.md             \# This README file  
├── .gitignore            \# Specifies intentionally untracked files to ignore  
└── LICENSE               \# Project license (e.g., MIT License)

## **⚙️ Setup and Installation**

To get this project up and running on your local machine, follow these steps:

1. **Clone the repository:**  
   git clone https://github.com/your-username/Stock-Sight.git  
   cd Stock-Sight

   *(Remember to replace your-username and Stock-Sight with your actual GitHub username and repository name.)*  
2. **Create a virtual environment (recommended):**  
   python \-m venv venv  
   source venv/bin/activate  \# On Windows: venv\\Scripts\\activate

3. **Install Python dependencies:**  
   pip install Flask Flask-Cors joblib pandas yfinance numpy ta

   *(Ensure roc\_model3.pkl is in the Backend directory.)*  
4. **Run the Flask backend:**  
   * Navigate into the Backend directory:  
     cd Backend

   * Run the Flask app:  
     python app.py

The Flask app will typically run on http://0.0.0.0:5000/ or http://127.0.0.1:5000/.

5. **Open the frontend:**  
   * Once the Flask server is running, open your web browser and go to the Flask server's address:  
     http://127.0.0.1:5000/

This will serve index.html from your Frontend folder.

## **💡 Usage**

1. Once the Flask server is running and the web page is open in your browser, you will see the "Stock Price Predictor" interface.  
2. Select a **Company Symbol** from the dropdown.  
3. Select a **Prediction Date**.  
4. Click the "Predict Stock Price" button to get the estimated price.  
5. Optionally, click "✨ Get Stock Insights" or "✨ Explain Prediction" to receive AI-generated information about the stock or the prediction itself.

Feel free to explore, contribute, or adapt this project for your own needs\!