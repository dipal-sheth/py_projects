import xml.etree.ElementTree as ET
import pandas as pd

# Load the XML file
xml_file = r"udemy_dsa\src\milliman\sample_masked.xml"
output_path = r"udemy_dsa\src\milliman\output_"

# Define namespace to properly parse HL7 CDA elements
ns = {'hl7': 'urn:hl7-org:v3'}

# Parse XML
tree = ET.parse(xml_file)
root = tree.getroot()

# patient Data
record_target = root.find(".//hl7:recordTarget", ns)

target_data = []
patient_id_value = None
if record_target is not None:
    patient_role = record_target.find("hl7:patientRole", ns)
    if patient_role is not None:
        patient_id = patient_role.find("hl7:id", ns)
        patient_id_value = patient_id.get("extension") if patient_id is not None else None

        addresses = []
        for addr in patient_role.findall("hl7:addr", ns):
            street = addr.find("hl7:streetAddressLine", ns).text if addr.find("hl7:streetAddressLine", ns) is not None else None
            city = addr.find("hl7:city", ns).text if addr.find("hl7:city", ns) is not None else None
            state = addr.find("hl7:state", ns).text if addr.find("hl7:state", ns) is not None else None
            postal_code = addr.find("hl7:postalCode", ns).text if addr.find("hl7:postalCode", ns) is not None else None
            country = addr.find("hl7:country", ns).text if addr.find("hl7:country", ns) is not None else None
            use = addr.get("use")  # Address type (Home, Work, etc.)
            addresses.append({"Street": street, "City": city, "State": state, "PostalCode": postal_code, "Country": country, "Type": use})

        telecoms = []
        for telecom in patient_role.findall("hl7:telecom", ns):
            telecoms.append({"Type": telecom.get("use"), "Value": telecom.get("value")})

        patient = patient_role.find("hl7:patient", ns)
        if patient is not None:
            name = patient.find("hl7:name", ns)
            given_names = [g.text for g in name.findall("hl7:given", ns) if g.text] if name is not None else []
            family_name = name.find("hl7:family", ns).text if name is not None and name.find("hl7:family", ns) is not None else None
            full_name = " ".join(given_names) + " " + (family_name if family_name else "")

        target_data.append({
            "PatientID": patient_id_value,
            "Name": full_name,
            "Addresses": addresses,
            "Telecoms": telecoms
        })

# Medications
medications = []
for med in root.findall(".//hl7:substanceAdministration", ns):
    drug = med.find(".//hl7:manufacturedMaterial/hl7:code", ns)
    if drug is not None:
        medications.append({
            "PatientID": patient_id_value,
            "DrugName": drug.get("displayName"),
            "Code": drug.get("code"),
            "CodeSystem": drug.get("codeSystem")
        })

# Problems (Diagnoses)
problems = []
for prob in root.findall(".//hl7:observation", ns):
    diagnosis = prob.find(".//hl7:code", ns)
    if diagnosis is not None:
        problems.append({
            "PatientID": patient_id_value,
            "Diagnosis": diagnosis.get("displayName"),
            "Code": diagnosis.get("code"),
            "CodeSystem": diagnosis.get("codeSystem")
        })

# Convert to DataFrame
df_patients = pd.DataFrame(target_data)
df_medications = pd.DataFrame(medications)
df_problems = pd.DataFrame(problems)

# Save to JSON
df_patients.to_json(f"{output_path}patients.json", orient="records", indent=4)
df_medications.to_json(f"{output_path}medications.json", orient="records", indent=4)
df_problems.to_json(f"{output_path}problems.json", orient="records", indent=4)

# Save to Parquet
df_patients.to_parquet(f"{output_path}patients.parquet", index=False)
df_medications.to_parquet(f"{output_path}medications.parquet", index=False)
df_problems.to_parquet(f"{output_path}problems.parquet", index=False)
