import logging
import azure.functions as func
import json
import psycopg2
from psycopg2 import sql
import os
import requests


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')


    raw_body = req.get_body().decode('utf-8')
    logging.info(f"Raw request body: {raw_body}")
    

    sanitized_body = raw_body.replace('\n', '')

    try:
        req_body = json.loads(sanitized_body)
        logging.info(f"Parsed JSON body: {req_body}")
    except json.JSONDecodeError as json_error:
        logging.error(f"JSON decoding failed: {json_error}")
        trigger_power_automate(error_message="Invalid JSON payload", raw_body=raw_body, req_body=None)
        return func.HttpResponse(
            "Invalid JSON payload sent to Power Automate.",
            status_code=400
        )

    try:
        s_chat_message = req_body.get("sChatMessage", {}).get("String", "Missing SChatMessage")
        s_referral_id = req_body.get("sReferralID", {}).get("String", "Missing SReferralID")
        s_allscripts_facility = req_body.get("sAllscriptsFacility", {}).get("String", "Missing SAllscriptsFacility")
        s_crmid = req_body.get("sCRMid", {}).get("String", "Missing SCRMid")
        s_facility_pcc_name = req_body.get("sFacilityPCCName", {}).get("String", "Missing SFacilityPCCName")
        s_accepting_user = req_body.get("sAcceptingUser", {}).get("String", "Missing SAcceptingUser")
        s_rpa_status = req_body.get("sRPAStatus", {}).get("String", "Missing SRPAStatus")
        s_referred_to = req_body.get("sReferredTo", {}).get("String", "Missing SReferredTo")
        s_route = req_body.get("sRoute", {}).get("String", "Missing SRoute")
        s_organization = req_body.get("sOrganization", {}).get("String", "Missing SOrganization")
        s_patient = req_body.get("sPatient", {}).get("String", "Name not sent")
        
        
        logging.info(f"Direct access sChatMessage: {req_body['sChatMessage']['String'] if 'sChatMessage' in req_body else 'Key not found'}")
        logging.info(f"Direct access sReferralID: {req_body['sReferralID']['String'] if 'sReferralID' in req_body else 'Key not found'}")
        logging.info(f"Direct access sAllscriptsFacility: {req_body['sAllscriptsFacility']['String'] if 'sAllscriptsFacility' in req_body else 'Key not found'}")
        logging.info(f"Direct access sCRMid: {req_body['sCRMid']['String'] if 'sCRMid' in req_body else 'Key not found'}")



        logging.info(f"SChatMessage: {s_chat_message}")
        logging.info(f"SReferralID: {s_referral_id}")
        logging.info(f"SAllscriptsFacility: {s_allscripts_facility}")
        logging.info(f"SCRMid: {s_crmid}")
        logging.info(f"SFacilityPCCName: {s_facility_pcc_name}")
        logging.info(f"SAcceptingUser: {s_accepting_user}")
        logging.info(f"SRPAStatus: {s_rpa_status}")
        logging.info(f"SReferredTo: {s_referred_to}")
        logging.info(f"SRoute: {s_route}")
        logging.info(f"SOrganization: {s_organization}")
        logging.info(f"SPatient: {s_patient}")


        db_host = os.getenv("DB_HOST")
        db_name = os.getenv("DB_NAME")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_port = os.getenv("DB_PORT", "5432")

        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        cursor = conn.cursor()

        spatient_value = s_patient if s_patient else None
        insert_query = sql.SQL("""
            INSERT INTO acceptance_requests (
                schatmessage, sreferralid, sallscriptsfacility, scrmid,
                sfacilitypccname, sacceptinguser, srpastatus, sreferredto,
                sroute, spatient, sorganization
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """)
        values = (
            s_chat_message, s_referral_id, s_allscripts_facility, s_crmid,
            s_facility_pcc_name, s_accepting_user, s_rpa_status, s_referred_to,
            s_route, spatient_value, s_organization, 
        )

        cursor.execute(insert_query, values)
        conn.commit()

        cursor.close()
        conn.close()
        return func.HttpResponse(
            "Request processed successfully.",
            status_code=200
        )

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        trigger_power_automate(error_message=str(e), raw_body=raw_body, req_body=req_body)
        return func.HttpResponse(
            "Internal Server Error",
            status_code=500
        )

def trigger_power_automate(error_message, raw_body=None, req_body=None):
    logging.info("Triggering Power Automate")

    error_data = {
        "RawBody": raw_body,  
        "ParsedData": req_body if req_body else "Not parsed - invalid JSON",
        "sFunction": "Acceptance",
        "Error": error_message
    }

    logging.info(f"Error data being sent to Power Automate: {json.dumps(error_data)}")

    try:
        response = requests.post(
            "https://prod-164.westus.logic.azure.com:443/workflows/56474121bed5447dbbca850ca5c836af/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=_fpN7sVdPTSJTry1clO4pFF12joCt379bNGvc8bs7cE",
            json=error_data
        )
        logging.info(f"Power Automate response status: {response.status_code}")
        logging.info(f"Power Automate response text: {response.text}")
        response.raise_for_status()
    except requests.RequestException as post_error:
        logging.error(f"Failed to send error data to Power Automate: {post_error}")
