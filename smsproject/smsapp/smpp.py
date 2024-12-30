import logging
import smpplib.gsm
import smpplib.client
import smpplib.consts
import time

logging.basicConfig(level=logging.INFO)

def send_sms(SMPP_HOST, SMPP_PORT, SYSTEM_ID, PASSWORD, SOURCE_ADDR, DESTINATION_ADDR, message):
    """
    Send SMS using SMPP and capture responses.
    """
    parts, encoding_flag, msg_type_flag = smpplib.gsm.make_parts(message)
    client = smpplib.client.Client(SMPP_HOST, SMPP_PORT)
    responses = []

    # Message sent handler to capture submit_sm_resp
    def handle_submit_sm_resp(pdu):
        response = {
            'sequence_number': pdu.sequence,
            'message_id': getattr(pdu, 'message_id', None),
            'status_code': pdu.status  # Correctly capture the command status
        }
        responses.append(response)
        logging.info(f"submit_sm_resp seqno: {pdu.sequence}, msgid: {response['message_id']}, status: {response['status_code']}")

    # Attach the handler
    client.set_message_sent_handler(handle_submit_sm_resp)

    try:
        # Connect and bind to the SMPP server
        logging.info(f"Connecting to SMPP server at {SMPP_HOST}:{SMPP_PORT}...")
        client.connect()
        client.bind_transceiver(system_id=SYSTEM_ID, password=PASSWORD)

        # Send each part of the message
        for part in parts:
            logging.info(f"Sending message part: {part}")
            client.send_message(
                source_addr_ton=smpplib.consts.SMPP_TON_ALNUM,
                source_addr_npi=smpplib.consts.SMPP_NPI_UNK,
                source_addr=SOURCE_ADDR,
                dest_addr_ton=smpplib.consts.SMPP_TON_INTL,
                dest_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
                destination_addr=DESTINATION_ADDR,
                short_message=part,
                data_coding=encoding_flag,
                esm_class=msg_type_flag,
                registered_delivery=True,
            )
            time.sleep(0.5)

        # Verify the responses were captured
        if not responses:
            logging.warning("No responses captured. Check if the handler was triggered.")

    except Exception as e:
        logging.error(f"Error sending SMS: {e}")
        raise e

    finally:
        client.unbind()
        client.disconnect()

    return responses
