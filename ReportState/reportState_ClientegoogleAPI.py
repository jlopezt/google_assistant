from google.oauth2 import service_account
import googleapiclient.discovery

SCOPES = ['https://www.googleapis.com/auth/homegraph']
SERVICE_ACCOUNT_FILE = 'keys/domoticae-67184-4671fd684532.json'

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

homegraph = googleapiclient.discovery.build('homegraph', 'v1', credentials=credentials)
device = homegraph.devices()

body={ 
  "requestId": "11223344",
  "agentUserId": "pepe",
  #"eventId": "Actuador apagado",  
  "payload": {
    "devices": {
      "states": {
        "actuador": {
          "on": True,
          "online": True,
          "currentToggleSettings": {
              "secuenciador": True
          },
          "currentModeSettings": {
              "modo": "Automatico"
          }          
        }
      },
    },
  },
}

accion=device.reportStateAndNotification(body=body)

resp=accion.execute()

print(resp)

"""
{ # Request type for the [`ReportStateAndNotification`](#google.home.graph.v1.HomeGraphApiService.ReportStateAndNotification) call. It may include states, notifications, or both. States and notifications are defined per `device_id` (for example, "123" and "456" in the following example). Example: ```json { "requestId": "ff36a3cc-ec34-11e6-b1a0-64510650abcf", "agentUserId": "1234", "payload": { "devices": { "states": { "123": { "on": true }, "456": { "on": true, "brightness": 10 } }, } } } ```
  "requestId": "11223344",
  "agentUserId": "pepe", 
  "eventId": "Actuador apagado",
  "payload": {
    "devices": {
      "states": { # States of devices to update. See the **Device STATES** section of the individual trait [reference guides](https://developers.home.google.com/cloud-to-cloud/traits).
        "actuador": {
          "on": true, # Properties of the object.
        }
      },
    },
  },
}
"""
"""
{
  "requestId": "123ABC",
  "agentUserId": "user-123",
  "payload": {
    "devices": {
      "states": {
        "light-123": {
          "on": true
        }
      }
    }
  }
}
{ # Request type for the [`ReportStateAndNotification`](#google.home.graph.v1.HomeGraphApiService.ReportStateAndNotification) call. It may include states, notifications, or both. States and notifications are defined per `device_id` (for example, "123" and "456" in the following example). Example: ```json { "requestId": "ff36a3cc-ec34-11e6-b1a0-64510650abcf", "agentUserId": "1234", "payload": { "devices": { "states": { "123": { "on": true }, "456": { "on": true, "brightness": 10 } }, } } } ```
  "agentUserId": "pepe", # Required. Third-party user ID.
  "eventId": "Actuador apagado", # Unique identifier per event (for example, a doorbell press).
  #"followUpToken": "A String", # Deprecated.
  "payload": { # Payload containing the state and notification information for devices. # Required. State of devices to update and notification metadata for devices.
    "devices": { # The states and notifications specific to a device. # The devices for updating state and sending notifications.
      "notifications": { # Notifications metadata for devices. See the **Device NOTIFICATIONS** section of the individual trait [reference guides](https://developers.home.google.com/cloud-to-cloud/traits).
        "a_key": "", # Properties of the object.
      },
      "states": { # States of devices to update. See the **Device STATES** section of the individual trait [reference guides](https://developers.home.google.com/cloud-to-cloud/traits).
        "a_key": "", # Properties of the object.
      },
    },
  },
  "requestId": "A String", # Request ID used for debugging.
}
"""