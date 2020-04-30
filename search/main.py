from flask import render_template
from google.cloud import datastore
import os

LINKS_SEARCH = 'links'
CHILDREN_SEARCH = 'children'


def search(request):
    print(request)

    request_args = request.args
    search_type = 'Invalid search type'
    result_label = 'No results'

    # Instantiates a client
    datastore_client = datastore.Client()
    query = datastore_client.query(kind='Site')
    args = []
    results = []
    if request_args:
        if request_args['search_type'] == LINKS_SEARCH:
            search_type = 'Search for community sites'
            borough = request_args['borough']
            pcn = request_args['pcn']
            service_type = request_args['service_type']
            result_label = f'Sites filtered by:'
            args.append(f'Borough = {borough}')
            args.append(f'PCN = {pcn}')
            args.append(f'Service Type = {service_type}')
            query.add_filter('borough', '=', borough)
            query.add_filter('pcn_network', '=', pcn)
            query.add_filter('service_type', '=', service_type)
            results = list(query.fetch())
        if request_args['search_type'] == CHILDREN_SEARCH:
            search_type = 'Search for child sites'
            parent = request_args['parent']
            result_label = f'Sites filtered by:'
            args.append(f'Parent = {parent}')
            query.add_filter('parent', '=', parent)
            results = list(query.fetch())
    sites = []
    for result in results:
        sites.append({'link': result['link'], 'site': result['site']})

    return str(sites) + "\n" + f'(BUCKET_NAME = {os.getenv("BUCKET_NAME")}'

    # return render_template('results.html',
    #                        sites=sites,
    #                        assets='https://storage.googleapis.com/' + os.getenv('BUCKET_NAME'),
    #                        search_type=search_type,
    #                        args=args,
    #                        result_label=result_label)
