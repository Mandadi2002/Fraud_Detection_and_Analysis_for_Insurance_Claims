import streamlit as st
import pandas as pd
import hashlib
import sqlite3

# Security
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# DB Management
conn = sqlite3.connect('data.db', check_same_thread=False)
c = conn.cursor()

# DB Functions
def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')

def add_userdata(username, password):
    c.execute('INSERT INTO userstable(username,password) VALUES (?,?)', (username, password))
    conn.commit()

def login_user(username, password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?', (username, password))
    return c.fetchall()

def view_all_users():
    c.execute('SELECT * FROM userstable')
    return c.fetchall()

def main():
    st.title("Simple Login App")

    menu = ["Home", "Login", "SignUp"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Home")

    elif choice == "Login":
        st.subheader("Login Section")

        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password", type='password')

        if st.sidebar.checkbox("Login"):
            create_usertable()
            hashed_pswd = make_hashes(password)
            result = login_user(username, hashed_pswd)

            if result:
                st.success(f"Logged In as {username}")
                st.write("Welcome to the dashboard!")
            else:
                st.warning("Incorrect Username/Password")

    elif choice == "SignUp":
        st.subheader("Create New Account")

        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type='password')

        if st.button("Signup"):
            create_usertable()
            add_userdata(new_user, make_hashes(new_password))
            st.success("Account Created Successfully")
            st.info("Go to Login Menu to login")

if __name__ == '__main__':
    main()




import streamlit as st
import pandas as pd
import pickle

# ------------------------------------------------
# Page Config
# ------------------------------------------------
st.set_page_config(
    page_title="Insurance Fraud Detection",
    page_icon="🚗",
    layout="centered"
)

st.title("🚗 Insurance Claim Fraud Detection")
st.write("Predict whether an insurance claim is **Fraudulent or Legitimate**.")

# ------------------------------------------------
# Load Models
# ------------------------------------------------
model_option = st.selectbox(
    "Select Model",
    ["SVC", "KNN", "RandomForest", "DecisionTree"]
)

model_paths = {
    "SVC": "/content/drive/MyDrive/Final Insurance Project/pkl files/svc_model(1).pkl",
    "KNN": "/content/drive/MyDrive/Final Insurance Project/pkl files/knn_model(1).pkl",
    "RandomForest": "/content/drive/MyDrive/Final Insurance Project/pkl files/rf_model(1).pkl",
    "DecisionTree": "/content/drive/MyDrive/Final Insurance Project/pkl files/dt_model(1).pkl"
}

model = pickle.load(open(model_paths[model_option], "rb"))

# Load training columns
model_columns = pickle.load(open("/content/drive/MyDrive/Final Insurance Project/pkl files/model_columns.pkl", "rb"))

# ------------------------------------------------
# Customer Details
# ------------------------------------------------
st.header("👤 Customer Details")

col1, col2 = st.columns(2)

with col1:
    months_as_customer = st.number_input("Months as Customer",0,500,100)
    age = st.number_input("Age",18,100,35)
    policy_deductable = st.number_input("Policy Deductible",0,5000,1000)

with col2:
    policy_annual_premium = st.number_input("Policy Annual Premium",0.0,5000.0,1200.0)
    umbrella_limit = st.number_input("Umbrella Limit",0,10000000,0)
    auto_year = st.number_input("Vehicle Year",1990,2024,2015)

# ------------------------------------------------
# Claim Details
# ------------------------------------------------
st.header("💰 Claim Details")

col3, col4 = st.columns(2)

with col3:
    total_claim_amount = st.number_input("Total Claim Amount",0,100000,20000)
    injury_claim = st.number_input("Injury Claim",0,50000,5000)

with col4:
    property_claim = st.number_input("Property Claim",0,60000,5000)
    vehicle_claim = st.number_input("Vehicle Claim",0,60000,10000)

# ------------------------------------------------
# Incident Details
# ------------------------------------------------
st.header("🚗 Incident Details")

incident_hour_of_the_day = st.slider("Incident Hour",0,23,12)
number_of_vehicles_involved = st.slider("Vehicles Involved",1,10,1)
bodily_injuries = st.slider("Bodily Injuries",0,5,0)
witnesses = st.slider("Witnesses",0,10,0)

property_damage = st.selectbox("Property Damage",["NO","YES"])
police_report_available = st.selectbox("Police Report Available",["NO","YES"])

# Encoding
property_damage = 1 if property_damage=="YES" else 0
police_report_available = 1 if police_report_available=="YES" else 0

# ------------------------------------------------
# Prediction
# ------------------------------------------------
if st.button("🔍 Predict Fraud"):

    input_dict = {
        "months_as_customer": months_as_customer,
        "age": age,
        "policy_deductable": policy_deductable,
        "policy_annual_premium": policy_annual_premium,
        "umbrella_limit": umbrella_limit,
        "auto_year": auto_year,
        "total_claim_amount": total_claim_amount,
        "injury_claim": injury_claim,
        "property_claim": property_claim,
        "vehicle_claim": vehicle_claim,
        "incident_hour_of_the_day": incident_hour_of_the_day,
        "number_of_vehicles_involved": number_of_vehicles_involved,
        "bodily_injuries": bodily_injuries,
        "witnesses": witnesses,
        "property_damage": property_damage,
        "police_report_available": police_report_available
    }

    input_df = pd.DataFrame([input_dict])

    # ------------------------------------------------
    # Match Training Columns
    # ------------------------------------------------
    input_df = pd.get_dummies(input_df)

    input_df = input_df.reindex(columns=model_columns, fill_value=0)

    # ------------------------------------------------
    # Prediction
    # ------------------------------------------------
    prediction = model.predict(input_df)[0]

    if hasattr(model,"predict_proba"):
        probability = model.predict_proba(input_df)[0][1]
    else:
        probability = None

    # ------------------------------------------------
    # Result
    # ------------------------------------------------
    st.subheader("📊 Prediction Result")

    if prediction == 1:
        st.error("🚨 Fraudulent Claim Detected")
    else:
        st.success("✅ Legitimate Claim")

    if probability:
        st.write(f"Fraud Probability: **{probability:.2%}**")