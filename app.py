from sys import stderr
from flask import Flask, render_template, request, redirect
import pickle
import numpy as np
import pandas as pd
import mysql.connector

# Establish a connection to MySQL
db = mysql.connector.connect(
    host='localhost',
    port='3306',
    user='root',
    password='',
    database='houseprice'
)

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template("index.html")

@app.route('/display_dataset')
def display_dataset():
    # Retrieve the dataset
    df = pd.read_csv('C:/Users/Rajalakshmi/Desktop/TCS Internship/dataset.csv')

    # Pass the dataset to the template
    return render_template('dataset.html', dataset=df.to_html(index=False))

@app.route('/predict', methods=['POST'])
def index():
    df = pd.read_csv('C:/Users/Rajalakshmi/Desktop/TCS Internship/dataset.csv')
    if request.method == 'POST':
        # Get the form data
        feature1 = request.form['LotFrontage']
        feature2 = request.form['LotArea']
        feature3 = request.form['TotalBsmtSF']
        feature4 = request.form['GarageArea']
        feature5 = request.form['MSZoning']
        feature6 = request.form['BldgType']

        # Convert form input values to appropriate data types
        feature1 = float(feature1)
        feature2 = float(feature2)
        feature3 = float(feature3)
        feature4 = float(feature4)

        # Print data types after conversion
        print("Data Types after Conversion:")
        print("Form Input Data Types:")
        print("LotFrontage:", type(feature1))
        print("LotArea:", type(feature2))
        print("TotalBsmtSF:", type(feature3))
        print("GarageArea:", type(feature4))
        print("MSZoning:", type(feature5))
        print("BldgType:", type(feature6))


        print("DataFrame Column Data Types:")
        print("LotFrontage:", df['LotFrontage'].dtype)
        print("LotArea:", df['LotArea'].dtype)
        print("TotalBsmtSF:", df['TotalBsmtSF'].dtype)
        print("GarageArea:", df['GarageArea'].dtype)
        print("MSZoning:", df['MSZoning'].dtype)
        print("BldgType:", df['BldgType'].dtype)


        # Modify the condition to relax or remove conditions
        condition = (feature2 == df['LotArea']) & (feature5 == df['MSZoning']) & (feature6 == df['BldgType'])


        # Filter the DataFrame based on the modified condition
        filtered_df = df.loc[condition, 'SalePrice']

        # Assign a default value to prediction
        prediction = None

        if not filtered_df.empty:
            prediction = filtered_df.values[0]  # Assuming there's only one matching row

            # Save the input values and predicted price to MySQL
            cursor = db.cursor()
            sql = "INSERT INTO predictions (lot_frontage, lot_area, total_bsmt_sf, garage_area, ms_zoning, bldg_type, predicted_price) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            values = (feature1, feature2, feature3, feature4, feature5, feature6, prediction)
            cursor.execute(sql, values)
            db.commit()

        # Debugging statement to print the value of the prediction variable
        print("Debugging: Prediction value =", prediction, file=stderr)

        # Pass the prediction to the template
        return render_template('index.html', prediction=prediction)

    return render_template('index.html')

# ADMIN LOGIN
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Perform admin login authentication
        if username == 'admin' and password == 'admin123':
            # Redirect to the admin page
            return redirect('/admin/dashboard')
        else:
            # Handle incorrect login credentials
            return render_template('admin_login.html', error=True)

    return render_template('admin_login.html', error=False)

# ADMIN DASHBOARD
@app.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    # Check if admin is logged in, otherwise redirect to the admin login page
    # Add your authentication logic here

    # Fetch the prediction data from the database
    cursor = db.cursor()
    cursor.execute('SELECT * FROM predictions')
    prediction_data = cursor.fetchall()

    return render_template('admin_dashboard.html', prediction_data=prediction_data)


@app.route('/admin/update/<int:prediction_id>', methods=['POST'])
def admin_update(id):
    # Check if admin is logged in, otherwise redirect to the admin login page
    # Add your authentication logic here

    # Get the form data
    predicted_price = request.form['predicted_price']

    # Update the sale price in the database
    cursor = db.cursor()
    query = 'UPDATE predictions SET predicted_price = %s WHERE id = %s'
    values = (predicted_price, id)
    cursor.execute(query, values)
    db.commit()

    return redirect('/admin/dashboard')


@app.route('/admin/delete/<int:prediction_id>', methods=['POST'])
def admin_delete(id):
    # Check if admin is logged in, otherwise redirect to the admin login page
    # Add your authentication logic here

    # Delete the prediction data from the database
    cursor = db.cursor()
    query = 'DELETE FROM predictions WHERE id = %s'
    values = (id,)
    cursor.execute(query, values)
    db.commit()

    return redirect('/admin/dashboard')


if __name__ == '__main__':
    app.run(debug=True)
