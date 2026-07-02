"""
Simple interface for predicting patient condition (Healthy / Hypertension / Diabetes / Heart Disease)
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import joblib
import os

# ============================================================
# 1) Load saved models
# ============================================================
MODELS_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_resource
def load_models():
    model_binary = joblib.load(os.path.join(MODELS_DIR, "model_binary_other_vs_disease.pkl"))
    model_disease = joblib.load(os.path.join(MODELS_DIR, "model_disease_type.pkl"))
    le_disease = joblib.load(os.path.join(MODELS_DIR, "label_encoder_disease.pkl"))
    model_severity = joblib.load(os.path.join(MODELS_DIR, "model_severity_score.pkl"))
    return model_binary, model_disease, le_disease, model_severity

try:
    model_binary, model_disease, le_disease, model_severity = load_models()
    models_loaded = True
except FileNotFoundError as e:
    models_loaded = False
    missing_file = str(e)

# ============================================================
# 2) Exact column order expected by the model (same order as X)
# ============================================================
FEATURE_COLUMNS = [
    'Gender', 'Age', 'Height', 'Weight', 'BMI', 'Avg_HeartRate',
    'Avg_Temperature', 'Avg_SystolicBP', 'Avg_DiastolicBP', 'Avg_RespRate',
    'Avg_O2Sat', 'Avg_MAP', 'Avg_Pulse_Pressure', 'Vitals_Delta_HR',
    'Max_SystolicBP', 'Max_HeartRate', 'Max_Temperature', 'Fever_Frequency',
    'Avg_Glucose', 'Max_Glucose', 'Glucose_Flag', 'HighCholesterol_Flag',
    'Tachycardia_Frequency', 'Total_Encounters', 'Avg_Stay_Days',
    'Chronic_Disease_Count', 'Blood_Type_A-', 'Blood_Type_AB+',
    'Blood_Type_AB-', 'Blood_Type_B+', 'Blood_Type_B-', 'Blood_Type_O+',
    'Blood_Type_O-', 'marital_Status_Married', 'marital_Status_Single',
    'marital_Status_Widowed'
]

DISEASE_NAMES_DISPLAY = {
    "Diabetes": "Diabetes",
    "Heart Disease": "Heart Disease",
    "Hypertension": "Hypertension",
}

# ============================================================
# 3) User interface
# ============================================================
st.set_page_config(page_title="Patient Risk Prediction System", layout="centered")
st.title("🩺 Patient Risk Prediction System")
st.caption("An educational tool to predict the likelihood of Hypertension, Diabetes, or Heart Disease — not a final medical diagnosis.")

if not models_loaded:
    st.error(
        "Model files (.pkl) not found. "
        "Make sure these four files are in the same folder as this file:\n"
        "- model_binary_other_vs_disease.pkl\n"
        "- model_disease_type.pkl\n"
        "- label_encoder_disease.pkl\n"
        "- model_severity_score.pkl"
    )
    st.stop()

st.subheader("1. Basic Information")
col1, col2 = st.columns(2)
with col1:
    age = st.number_input("Age", min_value=0, max_value=120, value=40)
    gender = st.selectbox("Gender", ["Male", "Female"])
    height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0)
with col2:
    weight = st.number_input("Weight (kg)", min_value=10.0, max_value=300.0, value=75.0)
    blood_type = st.selectbox("Blood Type", ["A+", "A-", "AB+", "AB-", "B+", "B-", "O+", "O-"])
    marital_status = st.selectbox("Marital Status", ["Single", "Married", "Widowed", "Divorced"])

bmi = round(weight / ((height / 100) ** 2), 1)
st.info(f"Automatically calculated BMI: **{bmi}**")

st.subheader("2. Vitals")
col3, col4 = st.columns(2)
with col3:
    avg_systolic = st.number_input("Average Systolic BP", 60, 250, 120)
    max_systolic = st.number_input("Max Systolic BP recorded", 60, 280, avg_systolic + 10)
    avg_diastolic = st.number_input("Average Diastolic BP", 30, 150, 80)
    avg_heart_rate = st.number_input("Average Heart Rate", 30, 220, 75)
    max_heart_rate = st.number_input("Max Heart Rate recorded", 30, 250, avg_heart_rate + 15)
with col4:
    avg_temp = st.number_input("Average Temperature (°C)", 34.0, 42.0, 37.0)
    max_temp = st.number_input("Max Temperature recorded", 34.0, 43.0, avg_temp + 0.3)
    avg_resp = st.number_input("Average Respiratory Rate", 5, 60, 16)
    avg_o2sat = st.number_input("Average O2 Saturation (%)", 50, 100, 97)

st.subheader("3. Glucose & Cholesterol")
col5, col6 = st.columns(2)
with col5:
    avg_glucose = st.number_input("Average Glucose", 40.0, 500.0, 90.0)
    max_glucose = st.number_input("Max Glucose recorded", 40.0, 600.0, avg_glucose + 5)
with col6:
    glucose_flag = st.checkbox("Notably high glucose? (Glucose Flag)")
    high_chol_flag = st.checkbox("High Cholesterol?")

st.subheader("4. General Medical History")
col7, col8 = st.columns(2)
with col7:
    fever_freq = st.number_input("Number of recorded fever episodes", 0, 50, 0)
    tachy_freq = st.number_input("Number of recorded tachycardia episodes", 0, 50, 0)
with col8:
    total_encounters = st.number_input("Total number of medical visits", 0, 200, 1)
    avg_stay_days = st.number_input("Average hospital stay (days)", 0.0, 60.0, 1.0)
chronic_count = st.slider("Number of recorded chronic conditions", 0, 10, 0)

# ============================================================
# 4) Build the feature row in exactly the same shape and order as X
# ============================================================
def build_feature_row():
    row = {col: 0 for col in FEATURE_COLUMNS}

    row['Gender'] = 0 if gender == "Male" else 1
    row['Age'] = age
    row['Height'] = height
    row['Weight'] = weight
    row['BMI'] = bmi
    row['Avg_HeartRate'] = avg_heart_rate
    row['Avg_Temperature'] = avg_temp
    row['Avg_SystolicBP'] = avg_systolic
    row['Avg_DiastolicBP'] = avg_diastolic
    row['Avg_RespRate'] = avg_resp
    row['Avg_O2Sat'] = avg_o2sat
    row['Avg_MAP'] = round((avg_systolic + 2 * avg_diastolic) / 3, 1)
    row['Avg_Pulse_Pressure'] = avg_systolic - avg_diastolic
    row['Vitals_Delta_HR'] = max_heart_rate - avg_heart_rate
    row['Max_SystolicBP'] = max_systolic
    row['Max_HeartRate'] = max_heart_rate
    row['Max_Temperature'] = max_temp
    row['Fever_Frequency'] = fever_freq
    row['Avg_Glucose'] = avg_glucose
    row['Max_Glucose'] = max_glucose
    row['Glucose_Flag'] = int(glucose_flag)
    row['HighCholesterol_Flag'] = int(high_chol_flag)
    row['Tachycardia_Frequency'] = tachy_freq
    row['Total_Encounters'] = total_encounters
    row['Avg_Stay_Days'] = avg_stay_days
    row['Chronic_Disease_Count'] = chronic_count

    # Blood type one-hot (A+ is the reference category dropped by drop_first)
    bt_col = f"Blood_Type_{blood_type}"
    if bt_col in row:
        row[bt_col] = 1

    # Marital status one-hot (Divorced is the reference category dropped by drop_first)
    ms_col = f"marital_Status_{marital_status}"
    if ms_col in row:
        row[ms_col] = 1

    return pd.DataFrame([row], columns=FEATURE_COLUMNS)


# ============================================================
# 5) Prediction step
# ============================================================
# Confidence thresholds for the "uncertain" zone.
# If the binary model's probability of disease falls between these two
# values, we treat the case as inconclusive instead of forcing model_disease
# (which was never trained on healthy patients and will always pick one of
# the 3 diseases with artificially high confidence).
#
# LOW_THRESHOLD = 0.33 was chosen using a Precision-Recall curve analysis on
# the test set: at this threshold, model_binary achieves ~90% Recall (it
# misses only ~10% of real disease cases), at the cost of dropping Precision
# to ~34% (more healthy patients get flagged as "needs checkup"/"uncertain").
# This trade-off was chosen deliberately: in a medical context, missing a
# real patient (false negative) is considered worse than over-flagging a
# healthy one (false positive).
#
# HIGH_THRESHOLD = 0.80 was chosen separately to avoid running model_disease
# (which always confidently picks one of the 3 diseases, since it was never
# trained on healthy patients) unless model_binary itself is quite confident.
LOW_THRESHOLD = 0.33
HIGH_THRESHOLD = 0.80


def predict_patient(patient_df):
    has_disease_proba = model_binary.predict_proba(patient_df)[0][1]

    if has_disease_proba < LOW_THRESHOLD:
        return {
            "status": "Healthy",
            "confidence": 1 - has_disease_proba,
            "disease_type": None,
            "disease_confidence": None,
        }
    elif has_disease_proba <= HIGH_THRESHOLD:
        return {
            "status": "Uncertain",
            "confidence": has_disease_proba,
            "disease_type": None,
            "disease_confidence": None,
        }
    else:
        disease_pred = model_disease.predict(patient_df)[0]
        disease_proba = model_disease.predict_proba(patient_df)[0]
        disease_name_en = le_disease.inverse_transform([disease_pred])[0]
        disease_name = DISEASE_NAMES_DISPLAY.get(disease_name_en, disease_name_en)
        confidence = disease_proba[disease_pred]
        return {
            "status": "Needs further checkup",
            "confidence": has_disease_proba,
            "disease_type": disease_name,
            "disease_confidence": confidence,
        }


st.divider()
if st.button("🔍 Analyze Patient", type="primary", use_container_width=True):
    patient_df = build_feature_row()
    result = predict_patient(patient_df)
    severity_score = model_severity.predict(patient_df)[0]

    if result["status"] == "Healthy":
        st.success(f"✅ Status: **Healthy** (Model confidence: {result['confidence']*100:.1f}%)")
    elif result["status"] == "Uncertain":
        st.info(
            f"🤔 Status: **Uncertain / borderline** "
            f"(Probability of an underlying condition: {result['confidence']*100:.1f}%)\n\n"
            "The vitals don't clearly match either a healthy profile or a specific "
            "disease pattern. A medical checkup is recommended rather than relying on "
            "this model's classification, since picking a disease type here would not "
            "be reliable."
        )
    else:
        st.warning(f"⚠️ Status: **Needs further checkup** (Model confidence: {result['confidence']*100:.1f}%)")
        st.error(
            f"Most likely condition: **{result['disease_type']}** "
            f"(Classification confidence: {result['disease_confidence']*100:.1f}%)"
        )

    st.metric(
        label="Estimated Patient Severity Score (0-100)",
        value=f"{severity_score:.1f}",
    )
    st.caption(
        "ℹ️ This score is a separate regression estimate (average prediction error "
        "on test data ≈ ±15 points), not a precise measurement — use it as a rough "
        "indicator of overall severity, alongside the classification above."
    )

    st.caption(
        "⚠️ This result is indicative only and is not a medical diagnosis. "
        "Please consult a specialist physician to confirm any condition."
    )

    with st.expander("View the input data sent to the model (for verification)"):
        st.dataframe(patient_df.T, use_container_width=True)
