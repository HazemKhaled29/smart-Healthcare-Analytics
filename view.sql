CREATE VIEW vw_patient_health_profile AS
SELECT
-- Patient Info
p.Patient_ID,p.Gender,p.Age,p.Age_Group,p.Height,p.Weight,p.Weight_Category,p.BMI,p.BMI_Category,p.Is_Obese,p.Blood_Type,p.Nationality,p.marital_Status,

-- Average Vitals
AVG(v.HeartRate) AS Avg_HeartRate,
AVG(v.Temperature) AS Avg_Temperature,
AVG(v.SystolicBP) AS Avg_SystolicBP,
AVG(v.DiastolicBP) AS Avg_DiastolicBP,
AVG(v.RespRate) AS Avg_RespRate,
AVG(v.O2Sat) AS Avg_O2Sat,
AVG(v.MAP) AS Avg_MAP,
AVG(v.SystolicBP - v.DiastolicBP)AS Avg_Pulse_Pressure, 
MAX(v.HeartRate) - MIN(v.HeartRate) AS Vitals_Delta_HR,

-- Maximum Risk Indicators
MAX(v.SystolicBP) AS Max_SystolicBP,
MAX(v.HeartRate) AS Max_HeartRate,
MAX(v.Temperature) AS Max_Temperature,
AVG(CAST(v.Has_Fever AS FLOAT)) AS Fever_Frequency,
AVG(CASE WHEN TestName='Glucose (mg/dl)' THEN TestValue END) AS Avg_Glucose , 
MAX(CASE WHEN TestName='Glucose (mg/dl)'THEN TestValue END) AS Max_Glucose,
MAX( CASE WHEN TestName='Glucose (mg/dl)' AND TestValue >= 126 THEN 1 ELSE 0 END) AS Glucose_Flag,
MAX( CASE WHEN TestName = 'TotalCholesterol (mg/dl)' AND TestValue >= 240 THEN 1 ELSE 0 END) AS HighCholesterol_Flag,
AVG(CAST(v.Is_Tachycardia AS FLOAT)) AS Tachycardia_Frequency,    

-- Encounter Summary
COUNT(DISTINCT e.Encounter_ID) AS Total_Encounters,
AVG(e.total_stay_days) AS Avg_Stay_Days,

-- Chronic Diseases
MAX(pc.Chronic_Disease_Count) AS Chronic_Disease_Count
FROM Patients p

LEFT JOIN encounter e
ON p.Patient_ID = e.Patient_ID

LEFT JOIN vitals v
ON e.Encounter_ID = v.Encounter_ID

LEFT JOIN patient_chronic pc
ON p.Patient_ID = pc.Patient_ID

LEFT JOIN Lab_tests l 
ON p.Patient_ID = l.Patient_ID

GROUP BY

p.Patient_ID,
p.Gender,
p.Age,
p.Age_Group,
p.Height,
p.Weight,
p.BMI,
p.BMI_Category,
p.Is_Obese,
p.Blood_Type,
p.Nationality,
p.Weight_Category,
p.marital_Status;

SELECT * FROM vw_patient_health_profile


------------------------------------------------------------

ALTER TABLE Disease
ADD Disease_Class VARCHAR(50);

UPDATE Disease
SET Disease_Class = 'Diabetes'
WHERE Admission_Diagnosis IN (
    'Type 1 Diabetes Mellitus',
    'Type 2 Diabetes Mellitus' , 
    'Insulin Resistance'
);

UPDATE Disease
SET Disease_Class = 'Heart Disease'
WHERE Admission_Diagnosis IN (
    'Coronary Artery Disease',
    'Heart Disease(Other Types)',
    'Arrhythmias',
    'Atrial Fibrillation',
    'Heart Failure',
    'Cardiomyopathy',
    'Congenital Heart Disease',
    'Peripheral Artery Disease',
    'Peripheral Artery Disease (PAD)'
);

UPDATE Disease
SET Disease_Class = 'Hypertension'
WHERE Admission_Diagnosis IN (
    'Hypertension(Secondary)' , 
    'Pulmonary Hypertension' , 
    'Hypertension(Primary)'
);

UPDATE Disease
SET Disease_Class = 'Other'
WHERE Disease_Class IS NULL 

SELECT * FROM Disease

SELECT
    Disease_Class,
    COUNT(DISTINCT Patient_ID)
FROM AI_Training_Dataset
GROUP BY Disease_Class;
------------------------------------------------------------



CREATE VIEW AI_Training_Dataset AS 
SELECT  
Gender,Age,Height,Weight,BMI,Blood_Type,Nationality,marital_Status,Avg_HeartRate,Avg_Temperature,Avg_SystolicBP,Avg_DiastolicBP,
Avg_RespRate,Avg_O2Sat,Avg_MAP,Avg_Pulse_Pressure, Vitals_Delta_HR,Max_SystolicBP,Max_HeartRate,
Max_Temperature,Fever_Frequency,Avg_Glucose , Max_Glucose,Glucose_Flag,Patient_Severity_Score,
 HighCholesterol_Flag,Tachycardia_Frequency, Total_Encounters,Avg_Stay_Days,Chronic_Disease_Count , Disease_Class
FROM Master_dataset M
JOIN Encounter  E 
ON E.Patient_ID = M.Patient_ID
JOIN Disease D 
ON D.Disease_ID = E.Disease_ID

------------------------------------------------------------------------------------------------------------


SELECT * FROM AI_Training_Dataset


SELECT *
FROM AI_Training_Dataset
WHERE Disease_Class IN (
    'Diabetes',
    'Hypertension',
    'Heart Disease'
);



