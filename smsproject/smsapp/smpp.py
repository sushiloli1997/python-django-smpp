import logging
import smpplib.gsm
import smpplib.client
import smpplib.consts
import time

logging.basicConfig(level=logging.INFO)

import smpplib.client
import smpplib.consts
import smpplib.gsm
import logging
import time


def send_sms(SMPP_HOST, SMPP_PORT, SYSTEM_ID, PASSWORD, SOURCE_ADDR, DESTINATION_ADDR, message):
    """
    Send SMS using SMPP and capture responses.
    """
    try:
        # Split the message into parts if necessary
        parts, encoding_flag, msg_type_flag = smpplib.gsm.make_parts(message)
    except Exception as e:
        logging.error(f"Failed to split the message into parts: {e}")
        return

    # Initialize the SMPP client
    client = smpplib.client.Client(SMPP_HOST, SMPP_PORT)
    responses = []

    # Handler to capture submit_sm_resp PDUs
    def handle_submit_sm_resp(pdu):
        response = {
            'sequence_number': pdu.sequence,
            'message_id': getattr(pdu, 'message_id', None),
            'status_code': pdu.status  # Capture the command status
        }
        responses.append(response)
        logging.info(f"SubmitSMResp received: seqno={pdu.sequence}, msgid={response['message_id']}, status={response['status_code']}")

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
            try:
                # Send the SMS part
                response = client.send_message(
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

                # Log the response (if immediate response is returned)
                if response:
                    logging.info(f"Response: {response}")
                    message_id = getattr(response, 'message_id', None)
                    logging.info(f"Message ID: {message_id if message_id else 'Not available'}")
                else:
                    logging.warning("No immediate response received for the sent message.")

            except Exception as e:
                logging.error(f"Failed to send message part: {e}")

            # Pause between parts to avoid overloading the SMPP server
            time.sleep(0.5)

    except Exception as e:
        logging.error(f"Failed to connect or bind to the SMPP server: {e}")

    finally:
        # Unbind and disconnect
        try:
            client.unbind()
            client.disconnect()
        except Exception as e:
            logging.warning(f"Error while disconnecting: {e}")

    # Final logging of all responses
    if responses:
        logging.info(f"All responses captured: {responses}")
    else:
        logging.warning("No responses were captured from the SMPP server.")



# def send_sms(SMPP_HOST, SMPP_PORT, SYSTEM_ID, PASSWORD, SOURCE_ADDR, DESTINATION_ADDR, message):
#     """
#     Send SMS using SMPP and capture responses.
#     """
#     parts, encoding_flag, msg_type_flag = smpplib.gsm.make_parts(message)
#     client = smpplib.client.Client(SMPP_HOST, SMPP_PORT)
#     responses = []

#     # Message sent handler to capture submit_sm_resp
#     def handle_submit_sm_resp(pdu):
#         response = {
#             'sequence_number': pdu.sequence,
#             'message_id': getattr(pdu, 'message_id', None),
#             'status_code': pdu.status  # Correctly capture the command status
#         }
#         responses.append(response)
#         logging.info(f"submit_sm_resp seqno: {pdu.sequence}, msgid: {response['message_id']}, status: {response['status_code']}")

#     # Attach the handler
#     client.set_message_sent_handler(handle_submit_sm_resp)

#     try:
#         # Connect and bind to the SMPP server
#         logging.info(f"Connecting to SMPP server at {SMPP_HOST}:{SMPP_PORT}...")
#         client.connect()
#         client.bind_transceiver(system_id=SYSTEM_ID, password=PASSWORD)

#         # Send each part of the message
#         for part in parts:
#             logging.info(f"Sending message part: {part}")
#             responses = []
#             responses=client.send_message(
#                 source_addr_ton=smpplib.consts.SMPP_TON_ALNUM,
#                 source_addr_npi=smpplib.consts.SMPP_NPI_UNK,
#                 source_addr=SOURCE_ADDR,
#                 dest_addr_ton=smpplib.consts.SMPP_TON_INTL,
#                 dest_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
#                 destination_addr=DESTINATION_ADDR,
#                 short_message=part,
#                 data_coding=encoding_flag,
#                 esm_class=msg_type_flag,
#                 registered_delivery=True,
#             )
#             for response in responses:
#                 logging.info(f"Response: {response}")
#             time.sleep(0.5)
#             print(f"No responses captured. Check if the handler was triggered.{['message_id']}")

#         # Verify the responses were captured
#         if not responses:
#             logging.warning("No responses captured. Check if the handler was triggered.")

#     except Exception as e:
#         logging.error(f"Error sending SMS: {e}")
#         raise e

#     finally:
#         client.unbind()
#         client.disconnect()

#     return responses
