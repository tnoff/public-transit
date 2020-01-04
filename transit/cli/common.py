import argparse
import datetime
import json
import re

from prettytable import PrettyTable

from transit.exceptions import CLIException

DEFAULT_DATETIME_FORMAT = '%Y-%m-%d %H-%M-%S'

DATETIME_FORMAT_NO_DATE = '%H:%M:%S'

DATETIME_FORMAT_JUST_DATE = '%Y-%m-%d'

def seconds_to_datetime(seconds):
    minutes = int(seconds / 60)
    if minutes > 0:
        seconds = seconds % 60

    hours = int(minutes / 60)
    if hours > 0:
        minutes = minutes % 60

    date = datetime.datetime(1900, 1, 1, hours, minutes, seconds)
    if hours > 0:
        return date.strftime('%H:%M:%S')
    return date.strftime('%M:%S')

class CommonArgparse(argparse.ArgumentParser):
    def error(self, message):
        raise CLIException(message)

def regex_checker(stringy, pattern):
    matcher = re.compile(pattern)
    if not matcher.match(stringy):
        raise argparse.ArgumentTypeError("String:%s does not match regex:%s" % (stringy, pattern))
    return stringy

class CommonCLI():
    def __init__(self, **kwargs):
        self.command = kwargs.pop('command').replace("-", "_")
        self.subcommand = kwargs.pop('subcommand').replace("-", "_")
        self.kwargs = kwargs

    def run_command(self):
        function = getattr(self, '%s_%s' % (self.command, self.subcommand))
        function(**self.kwargs)

    def _print_json(self, data, datetime_format=DEFAULT_DATETIME_FORMAT): #pylint:disable=no-self-use
        # Input data can be list, but not always
        if not isinstance(data, list):
            data = [data]
        # Now iterate through list
        for item in data:
            if isinstance(item, dict):
                # Check for any values that are datetimes
                for key, value in item.items():
                    if isinstance(value, datetime.datetime):
                        item[key] = value.strftime(datetime_format)
        # If only one item, turn back into single
        if len(data) == 1:
            data = data[0]
        print(json.dumps(data, indent=4, sort_keys=True))

    def _print_table(self, data, key_order=None, datetime_format=DEFAULT_DATETIME_FORMAT): #pylint:disable=no-self-use
        # If keys given, just use key order
        if key_order is not None:
            keys = key_order
        else:
            # Assume all keys are uniform
            # So take keys from first item
            keys = sorted(list(data[0].keys()))

        # Make sure keys are capitalized
        capital_keys = []
        for key in keys:
            split_key = key.split('_')
            capital_keys.append(' '.join(part.capitalize() for part in split_key))

        table = PrettyTable(capital_keys)
        for item in data:
            item_data = []
            for key in keys:
                if isinstance(item[key], datetime.datetime):
                    item_data.append(item[key].strftime(datetime_format))
                else:
                    item_data.append(item[key])
            table.add_row(item_data)
        return str(table)
