"""Hello Analytics Reporting API V4."""

import argparse

from apiclient.discovery import build
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
DISCOVERY_URI = ('https://analyticsreporting.googleapis.com/$discovery/rest')
CLIENT_SECRETS_PATH = 'client_secrets.json' # Path to client_secrets.json file.
VIEW_ID = '183991785'


def initialize_analyticsreporting():
  """Initializes the analyticsreporting service object.

  Returns:
    analytics an authorized analyticsreporting service object.
  """
  # Parse command-line arguments.
  parser = argparse.ArgumentParser(
      formatter_class=argparse.RawDescriptionHelpFormatter,
      parents=[tools.argparser])
  flags = parser.parse_args([])

  # Set up a Flow object to be used if we need to authenticate.
  flow = client.flow_from_clientsecrets(
      CLIENT_SECRETS_PATH, scope=SCOPES,
      message=tools.message_if_missing(CLIENT_SECRETS_PATH))

  # Prepare credentials, and authorize HTTP object with them.
  # If the credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # credentials will get written back to a file.
  storage = file.Storage('analyticsreporting.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(flow, storage, flags)
  http = credentials.authorize(http=httplib2.Http())

  # Build the service object.
  analytics = build('analytics', 'v4', http=http, discoveryServiceUrl=DISCOVERY_URI)

  return analytics

def get_report(analytics):
  # Use the Analytics Service Object to query the Analytics Reporting API V4.
  return analytics.reports().batchGet(
      body={
        'reportRequests': [
        {
          'viewId': VIEW_ID,
          'dateRanges': [{'startDate': '2019-01-01', 'endDate': 'today'}],
          'metrics': [{'expression': 'ga:sessions'}],
          'dimensions':[{'name': 'ga:latitude'},{'name': 'ga:longitude'}]  
        }]
      }
  ).execute()



def print_response(response):
    """Parses and prints the Analytics Reporting API V4 response"""


    for report in response.get('reports', []):
        columnHeader = report.get('columnHeader', {})
        dimensionHeaders = columnHeader.get('dimensions', [])
        metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])
        rows = report.get('data', {}).get('rows', [])
        #     create empty list to later append dictionaries into. 
        df_list = []
        for row in rows:
            dimensions = row.get('dimensions', [])
            dateRangeValues = row.get('metrics', [])
    #         Create empty dictionary which will contain key,value pairs for relevant metrics
            mt_dict = dict({})
            for header, dimension in zip(dimensionHeaders, dimensions):
                print (header + ': ' + dimension)
    #             Create an entry in the dictionary with the Dimension as the Key (splitting for formatting) and the dimension value as the value
                mt_dict[header.split(":")[-1]] = dimension
            for i, values in enumerate(dateRangeValues):
                print ('Date range (' + str(i) + ')')
                for metricHeader, value in zip(metricHeaders, values.get('values')):
                    print (metricHeader.get('name') + ': ' + value)
    #                 Create an entry in the dictionary with the Metric as the key and the metric value as the value
                    mt_dict[metricHeader.get('name').split(":")[-1]] = value

    # Append dictionary for each iteration into list
            df_list.append(mt_dict)

    # Return a DataFrame object that is created from the above list
    return pd.DataFrame(df_list)



def main():

    analytics = initialize_analyticsreporting()
    response = get_report(analytics)
    df = print_response(response)
    return df

# Include below if using this in a .py File
if __name__ == '__main__':
  main()


df = main()
