import os
import sys
import joblib
import numpy as np
from config.paths_config import MODEL_OUTPUT_PATH
from flask import Flask, render_template, request
import time

app = Flask(__name__)

# Add LightGBM bin directory to PATH before loading the model
try:
    lightgbm_bin_path = os.path.join(os.path.dirname(sys.executable), "Lib", "site-packages", "lightgbm", "bin")
    if os.path.exists(lightgbm_bin_path):
        os.environ["PATH"] = lightgbm_bin_path + os.pathsep + os.environ["PATH"]
        print(f"Added {lightgbm_bin_path} to PATH")
    
    # Now try to load the model
    loaded_model = joblib.load(MODEL_OUTPUT_PATH)
    print(f"Model loaded successfully from {MODEL_OUTPUT_PATH}!")
    print(f"Model type: {type(loaded_model).__name__}")
except Exception as e:
    print(f"Error loading model: {e}")
    # Provide a simple fallback model in case the real one fails to load
    # This is just for demonstration - you'd want to handle this differently in production
    import pickle
    class FallbackModel:
        def predict(self, X):
            return [0]  # Default prediction
    loaded_model = FallbackModel()

@app.route('/',methods=['GET','POST'])
def index():
    if request.method=='POST':
        try:
            # Get start time for performance tracking
            start_time = time.time()
            
            # Parse form data
            lead_time = int(request.form["lead_time"])
            no_of_special_request = int(request.form["no_of_special_request"])
            avg_price_per_room = float(request.form["avg_price_per_room"])
            arrival_month = int(request.form["arrival_month"])
            arrival_date = int(request.form["arrival_date"])
            market_segment_type = int(request.form["market_segment_type"])
            no_of_week_nights = int(request.form["no_of_week_nights"])
            no_of_weekend_nights = int(request.form["no_of_weekend_nights"])
            type_of_meal_plan = int(request.form["type_of_meal_plan"])
            room_type_reserved = int(request.form["room_type_reserved"])

            # Create feature array
            features = np.array([[
                lead_time, 
                no_of_special_request, 
                avg_price_per_room, 
                arrival_month, 
                arrival_date, 
                market_segment_type, 
                no_of_week_nights, 
                no_of_weekend_nights, 
                type_of_meal_plan, 
                room_type_reserved
            ]])

            # Get prediction
            prediction = loaded_model.predict(features)
            prediction_time = time.time() - start_time
            
            # Create detailed terminal output
            feature_names = [
                "lead_time", "no_of_special_request", "avg_price_per_room", 
                "arrival_month", "arrival_date", "market_segment_type",
                "no_of_week_nights", "no_of_weekend_nights", 
                "type_of_meal_plan", "room_type_reserved"
            ]
            
            prediction_result = "Canceled" if prediction[0] == 1 else "Not Canceled"
            
            # Print detailed information to terminal
            print("\n" + "="*50)
            print("HOTEL BOOKING PREDICTION REQUEST")
            print("="*50)
            print("TIMESTAMP: ", time.strftime("%Y-%m-%d %H:%M:%S"))
            print("\nINPUT FEATURES:")
            for i, name in enumerate(feature_names):
                print(f"  {name:25}: {features[0][i]}")
            
            print("\nPREDICTION:")
            print(f"  Raw Value: {prediction[0]}")
            print(f"  Result   : {prediction_result}")
            print(f"  Time     : {prediction_time:.4f} seconds")
            print("="*50 + "\n")
            
            # Return result to user
            return render_template('index.html', prediction=prediction[0])
        
        except Exception as e:
            print(f"\nERROR IN PREDICTION: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            print(f"Error details: {e}")
            import traceback
            print(f"Stack trace: {traceback.format_exc()}")
            return render_template('index.html', prediction=None, error=str(e))
    
    return render_template("index.html", prediction=None)

if __name__=="__main__":
    print("\n" + "*"*70)
    print("* HOTEL BOOKING PREDICTION APPLICATION")
    print("* Server starting on http://127.0.0.1:8080")
    print("* Press CTRL+C to quit")
    print("*"*70 + "\n")
    app.run(host='0.0.0.0', port=8080)