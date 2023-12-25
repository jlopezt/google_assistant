# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Python implementation of the GRPC helloworld.Greeter client."""

from __future__ import print_function
import logging
import grpc

#import sys
#sys.path.append('../')

from google.home.graph.v1 import homegraph_pb2, homegraph_pb2_grpc
from google.protobuf.struct_pb2 import Struct

from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/homegraph']
SERVICE_ACCOUNT_FILE = 'keys/domoticae-67184-4671fd684532.json'


def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    print("Iniciamos la llamada a Google Home ...")

    Xcredentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    with grpc.secure_channel(target = 'https://www.googleapis.com/auth/homegraph', credentials = Xcredentials) as channel:
        stub = homegraph_pb2_grpc.HomeGraphApiServiceStub(channel)
        request_id = "112233445566"
        event_id = "22334455"
        agent_user_id = "joloto"
        #payload
        device_id = "actuador"
        device_type = "switch"

        states = Struct()
        states.FieldsEntry.key='on'
        states.FieldsEntry.value=True        
        
        notifications = Struct()
        notifications.FieldsEntry.key='title'
        notifications.FieldsEntry.value='Conectado'
        notifications.FieldsEntry.key='message'
        notifications.FieldsEntry.value='El actuador esta conectado'
        
        report_state_and_notification_device = homegraph_pb2.ReportStateAndNotificationDevice(
            states=states,
            notifications=notifications
            )

        report_state_and_notification_payload = homegraph_pb2.StateAndNotificationPayload(
            devices=report_state_and_notification_device
        )

        report_state_and_notification_request = homegraph_pb2.ReportStateAndNotificationRequest(
            request_id=request_id, event_id=event_id, agent_user_id=agent_user_id,
            payload=report_state_and_notification_payload
            )
        """{"devices": {
                    "states": {
                        device_id:{
                            "on": True
                            }
                        }
                    }
                }
        """            
        
        response = stub.ReportStateAndNotification(report_state_and_notification_request)

if __name__ == "__main__":
    logging.basicConfig()
    
    run()
