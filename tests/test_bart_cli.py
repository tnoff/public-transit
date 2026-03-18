from click.testing import CliRunner

from transit.cli.bart import cli

FAKE_KEY = 'testkey'


def test_service_advisory(mocker):
    mocker.patch('transit.cli.bart.client.service_advisory', return_value={'bsa': []})
    result = CliRunner().invoke(cli, ['-k', FAKE_KEY, 'service-advisory'], obj={})
    assert result.exit_code == 0


def test_train_count(mocker):
    mocker.patch('transit.cli.bart.client.train_count', return_value={'traincount': '10'})
    result = CliRunner().invoke(cli, ['-k', FAKE_KEY, 'train-count'], obj={})
    assert result.exit_code == 0


def test_elevator_status(mocker):
    mocker.patch('transit.cli.bart.client.elevator_status', return_value={'bsa': []})
    result = CliRunner().invoke(cli, ['-k', FAKE_KEY, 'elevator-status'], obj={})
    assert result.exit_code == 0


def test_station_list(mocker):
    mocker.patch('transit.cli.bart.client.station_list', return_value={'stations': []})
    result = CliRunner().invoke(cli, ['-k', FAKE_KEY, 'station-list'], obj={})
    assert result.exit_code == 0


def test_station_departures(mocker):
    mocker.patch('transit.cli.bart.client.station_departures', return_value={'station': []})
    result = CliRunner().invoke(cli, ['-k', FAKE_KEY, 'station-departures', '12th'], obj={})
    assert result.exit_code == 0


def test_station_departures_with_options(mocker):
    mocker.patch('transit.cli.bart.client.station_departures', return_value={'station': []})
    result = CliRunner().invoke(
        cli, ['-k', FAKE_KEY, 'station-departures', '-p', '1', '-d', 'n', '12th'], obj={}
    )
    assert result.exit_code == 0
