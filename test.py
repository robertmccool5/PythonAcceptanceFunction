import json

import json

# Example of the raw JSON payload as a string (replace with your actual JSON)
raw_body = '''{
    "SChatMessage": {
        "Type": "string",
        "String": "accepted, pending bed availability. Please confirm patient would like a bed with us "
    },
    "SReferralID": {
        "Type": "string",
        "String": "80704058"
    },
    "SAllscriptsFacility": {
        "Type": "string",
        "String": "Eldercrest Nursing Center"
    },
    "SCRMid": {
        "Type": "string",
        "String": "crm id"
    },
    "SFacilityPCCName": {
        "Type": "string",
        "String": "pcc name"
    },
    "SAcceptingUser": {
        "Type": "string",
        "String": " accepting user name"
    },
    "SRPAStatus": {
        "Type": "string",
        "String": ""
    },
    "SReferredTo": {
        "Type": "string",
        "String": "referred to"
    },
    "SRoute": {
        "Type": "string",
        "String": "Careport"
    },
    "SOrganization": {
        "Type": "string",
        "String": "GUA0001"
    },
    "Status": {
        "Type": "string",
        "String": "Acceptance processing"
    },
    "SPatient": {
        "Type": "string",
        "String": ""
    }
}'''

try:
    parsed_json = json.loads(raw_body)
    print("Parsed successfully:", parsed_json)
except json.JSONDecodeError as e:
    print("Failed to parse JSON:", e)
