from google.oauth2 import service_account
import googleapiclient.discovery

SCOPES = ['https://www.googleapis.com/auth/homegraph']
#SERVICE_ACCOUNT_FILE = 'keys/domoticae-67184-4671fd684532.json' #PRO
SERVICE_ACCOUNT_FILE = '/home/pi/desarrollo/python/flask/google_assistant/ReportState/keys/domoticaepre-5926-c2d8823e0048.json' #PRE

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

homegraph = googleapiclient.discovery.build('homegraph', 'v1', credentials=credentials)
device = homegraph.devices()
#body = RequestSyncDevices({"agentUserId": "Manolo"","async": false})
accion=device.requestSync(body={"agentUserId": "pepe","async": False})
#accion.body='{"agentUserId": "Manolo","async": false}'
resp=accion.execute()

print(resp)