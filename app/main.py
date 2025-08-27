from flask import Flask, request, jsonify
import joblib
import pandas as pd
import datetime

# Initialize the Flask application
app = Flask(__name__)

# --- Load the trained model when the application starts ---
# The model is loaded only once, making predictions faster.
try:
    model = joblib.load('demand_predictor_model.joblib')
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# --- Define the pricing logic ---
# This function applies a multiplier based on the predicted demand.
BASE_PRICE = 10.0 # Example base price in USD

def get_price_multiplier(predicted_demand):
    """Calculates a price multiplier based on the predicted demand."""
    if predicted_demand < 50:
        return 0.9  # 10% discount for low demand
    elif 50 <= predicted_demand < 150:
        return 1.0  # Standard price
    elif 150 <= predicted_demand < 300:
        return 1.2  # 20% surge for medium demand
    else: # predicted_demand >= 300
        return 1.5  # 50% surge for high demand

# --- Define the API endpoint ---
@app.route('/predict', methods=['POST'])
def predict():
    # Ensure the model was loaded correctly
    if model is None:
        return jsonify({'error': 'Model is not available'}), 500

    try:
        # Get JSON data from the request body
        data = request.get_json(force=True)
        
        # --- Data Validation and Feature Creation ---
        # The API expects a location_id. Timestamp is optional.
        if 'location_id' not in data:
            return jsonify({'error': 'Missing `location_id` in request'}), 400
            
        location_id = data['location_id']
        # If timestamp is not provided, default to the current time
        timestamp_str = data.get('timestamp', datetime.datetime.now().isoformat())
        
        # Convert timestamp to a datetime object and create time-based features
        dt_object = datetime.datetime.fromisoformat(timestamp_str)
        hour = dt_object.hour
        day_of_week = dt_object.weekday()
        day_of_month = dt_object.day
        month = dt_object.month
        
        # Create a pandas DataFrame that matches the model's expected input format
        input_df = pd.DataFrame([{
            'PULocationID': location_id,
            'hour': hour,
            'day_of_week': day_of_week,
            'day_of_month': day_of_month,
            'month': month
        }])
        
        # --- Prediction and Pricing ---
        # Use the model to predict demand
        predicted_demand = model.predict(input_df)[0]
        
        # Apply the pricing logic
        multiplier = get_price_multiplier(predicted_demand)
        final_price = BASE_PRICE * multiplier
        
        # --- Format and Return the Response ---
        # Return the results as a JSON object
        return jsonify({
            'location_id': location_id,
            'timestamp': timestamp_str,
            'predicted_demand': round(float(predicted_demand), 2),
            'price_multiplier': multiplier,
            'recommended_price_usd': round(final_price, 2)
        })

    except Exception as e:
        # Handle any other errors gracefully
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

# This allows you to run the app locally for testing
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)