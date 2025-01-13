from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging

from .smpp import send_sms  # Assuming the send_sms function is in utils.py

logging.basicConfig(level=logging.INFO)

class SendSMSAPIView(APIView):
    """
    API endpoint to send SMS using SMPP.
    """
    def post(self, request, *args, **kwargs):
        try:
            # Extract parameters from the request
            SMPP_HOST = request.data.get('SMPP_HOST', '10.26.140.160')
            SMPP_PORT = int(request.data.get('SMPP_PORT', 5016))
            SYSTEM_ID = request.data.get('SYSTEM_ID', 'NKaruna')
            PASSWORD = request.data.get('PASSWORD', 'ktpl1220')
            SOURCE_ADDR = request.data.get('SOURCE_ADDR', 'KRT_Alert')
            DESTINATION_ADDR = request.data.get('DESTINATION_ADDR')
            message = request.data.get('message', 'Hello World €$£')

            # Validate mandatory fields
            if not DESTINATION_ADDR:
                return Response({'error': "The 'DESTINATION_ADDR' field is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Call the send_sms function
            logging.info("Sending SMS...")
            responses = send_sms(SMPP_HOST, SMPP_PORT, SYSTEM_ID, PASSWORD, SOURCE_ADDR, DESTINATION_ADDR, message)

            return Response({'status': 'SMS sent successfully!', 'responses': responses}, status=status.HTTP_200_OK)

        except Exception as e:
            logging.error(f"Error in SendSMSAPIView: {e}")
            return Response({'error': 'Failed to send SMS', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

