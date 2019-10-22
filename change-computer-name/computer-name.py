import sys
import os
import argparse
import warnings
import deepsecurity as api
from deepsecurity.rest import ApiException

if not sys.warnoptions:
    warnings.simplefilter('ignore')


class Ds:
    def __init__(self):
        try:
            print('Obtaining DS API key')
            ds_api_key = os.environ['DS_KEY']
            self.api_version = os.environ.get('DS_API_VERSION', 'v1')
            print(f'Set API version to {self.api_version}')

        except KeyError:
            sys.exit('"DS_KEY" environment variables are not set. Please set them and try again.')

        dsm_address = os.environ.get('DS_API_ADDRESS', 'https://app.deepsecurity.trendmicro.com/api')
        print(f'Obtained DS API address: {dsm_address}')

        print('Initiating DS connection')
        config = api.Configuration()
        config.host = dsm_address
        config.api_key['api-secret-key'] = ds_api_key

        self.api_client = api.ApiClient(config)

    def _find_exact_match(self, search_field, search_string, object_api):
        search_criteria = api.SearchCriteria()
        search_criteria.field_name = search_field
        search_criteria.string_test = 'equal'
        search_criteria.string_value = search_string

        search_filter = api.SearchFilter(None, [search_criteria])
        search_filter.max_items = 1

        try:
            result = object_api(self.api_version, search_filter=search_filter)

            return result

        except ApiException as e:
            print(str(e))
            sys.exit(1)

    def get_computer_id(self, hostname):
        print(f'Searching for "{hostname}" IDs...')

        search_field = 'hostName'
        search_computers_api = api.ComputersApi(self.api_client).search_computers
        computer = self._find_exact_match(search_field, hostname, search_computers_api)

        computer_id = computer.computers[0].id

        print(f'"{hostname}" - Computer ID: {computer_id}')

        return computer_id

    def change_computer_name(self, current_name, new_name):
        computer_id = self.get_computer_id(current_name)

        computers_api = api.ComputersApi(self.api_client)
        computer = api.Computer()
        computer.host_name = new_name

        try:
            computers_api.modify_computer(computer_id, computer, self.api_version, overrides=False)
            print(f'Successfully changed computer name from "{current_name}" to "{new_name}"')

        except ApiException as e:
            print(str(e))
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--current-name', required=True)
    parser.add_argument('--new-name', required=True)
    args = parser.parse_args()

    ds = Ds()
    ds.change_computer_name(args.current_name, args.new_name)


if __name__ == '__main__':
    main()
