#
# This script is intended to run once to add new providers to the datastore from a csv file.
# An attempt is made to create a new record for each of the entries in the input file 'new-providers.csv'.
# If the provider's key already exists then the provider record is updated with the values from the input file
# but the code value is not changed so that the provider's link remains valid. In all cases the results
# and the links for the providers are appended to the input file.
# The script will try to use the credentials of a locally configured service account so it
# is important to provide the key file as an environment variable e.g.
#
#           $ export GOOGLE_APPLICATION_CREDENTIALS="ppe-inventory-dev.json"
#
# Pass the PRODUCTION, TEST or DEV base url as a commandline argument as required e.g.
#
#           $ python3 new-providers.py https://********************.cloudfunctions.net
#

from google.cloud import datastore
import csv
import uuid
import sys
import logging
from notifications_python_client.notifications import NotificationsAPIClient
import os

baseUrl = ''
if len(sys.argv) > 1:
    baseUrl = sys.argv[1]
else:
    print('No link base url was provided so no action taken')
    sys.exit(1)

logfile = "new-providers.log"
logging.basicConfig(level=logging.INFO, filename=logfile)

print(f'logging to {logfile} ...')
logging.info(f'Link base url is {baseUrl}')

notifications_client = NotificationsAPIClient(os.getenv('EMAIL_API_KEY'))

response = notifications_client.get_template(
    'a9b20e19-efe9-4e6a-b081-67b549e596dc'  # required string - template ID
)

print(response)

response = notifications_client.send_email_notification(
    email_address='frank@notbinary.co.uk',  # required string
    template_id='a9b20e19-efe9-4e6a-b081-67b549e596dc',  # required UUID string
)

print(response)

# Instantiates a client
datastore_client = datastore.Client()

f = open("new-providers-output.csv", "w+")

# Read input from csv file
logging.info('Reading records from input csv file...')

with open('new-providers.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    next(reader, None)
    for row in reader:
        # Read input values and do some tidying up
        provider = row[0].strip()
        borough = row[1]
        contact_name = row[2]
        contact_email = row[3]
        telephone = row[4]
        service_type = row[5]
        location = row[6]
        postcode = row[7]
        # Check if record exists so can use existing code otherwise generate new code value
        existing_provider = datastore_client.get(datastore_client.key('Site', provider))
        if existing_provider:
            comment = 'EXISTING'
            code = existing_provider['code']
        else:
            comment = 'NEW     '
            code = str(uuid.uuid4())

        # Prepare to create or update the entity
        provider_key = datastore_client.key('Site', provider)
        entity = datastore.Entity(key=provider_key)
        entity['provider'] = provider
        entity['borough'] = borough
        entity['contact_name'] = contact_name
        entity['contact_email'] = contact_email
        entity['telephone'] = telephone
        entity['service_type'] = service_type
        entity['location'] = location
        entity['postcode'] = postcode.upper()
        entity['code'] = code
        # Saves the entity
        datastore_client.put(entity)

        link = baseUrl + '/register?site=' + provider + '&code=' + code
        link = '{0: <200}'.format(link)
        line = f'{comment}, {link} \n'
        logging.info(line)
        f.write(line)

f.close()