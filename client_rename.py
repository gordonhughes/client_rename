#!/usr/bin/python3.6

READ_ME = '''
=== PREREQUISITES ===
Run in Python 3.6+

Install the Meraki Python library:
pip[3] install --upgrade meraki

Have input CSV file with client name and MAC address specified.

=== DESCRIPTION ===
This script renames clients in a dashboard network using an input CSV file.

=== USAGE ===
python[3] provision_clients.py -f <input_file> -k <api_key> -n <net_id>
    [-m <mode>]
Mode defaults to "simulate" unless "commit" is specified.

'''


import csv
import getopt
import sys

import meraki


# Prints READ_ME help message for user to read
def print_help():
    lines = READ_ME.split('\n')
    for line in lines:
        print('# {0}'.format(line))


def main(argv):
    # Set default values for command line arguments
    arg_file = api_key = org_id = arg_mode = None

    # Get command line arguments
    try:
        opts, args = getopt.getopt(argv, 'hf:k:n:m:')
    except getopt.GetoptError:
        print_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        elif opt == '-f':
            arg_file = arg
        elif opt == '-k':
            api_key = arg
        elif opt == '-n':
            net_id = arg
        elif opt == '-m':
            arg_mode = arg

    # Check if all required parameters have been input
    if arg_file == None or api_key == None or net_id == None:
        print_help()
        sys.exit(2)

    # Assign default mode to "simulate" unless "commit" specified
    if arg_mode != 'commit':
        arg_mode = 'simulate'

    # Read and process input file
    mappings = []
    with open(arg_file, newline='\n') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        next(csv_reader, None)
        for row in csv_reader:
            client = row[0]
            mac = row[1]
            mappings.append([client, mac])
    print(f'Read {len(mappings)} rows from input CSV\n')

    # Dashboard API library class
    m = meraki.DashboardAPI(api_key=api_key, log_file_prefix=__file__[:-3], simulate=(arg_mode=='simulate'))

    # Iterate through input list of clients
    for [client, mac] in mappings:
        try:
            policy = m.clients.getNetworkClientPolicy(net_id, mac)
            policy_id = policy['groupPolicyId'] if 'groupPolicyId' in policy else None
            result = m.clients.provisionNetworkClients(net_id,
                                                       mac=mac,
                                                       name=client,
                                                       devicePolicy=policy['type'],
                                                       groupPolicyId=policy_id)
            print(f'{result}\n')
        except meraki.APIError as e:
            print(f'Meraki API error: {e}')
            continue
        except Exception as e:
            print(f'some other error: {e}')
            continue


if __name__ == '__main__':
    main(sys.argv[1:])
