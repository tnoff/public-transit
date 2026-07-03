import pytest
from unittest.mock import MagicMock
from click.testing import CliRunner

from trip_planner.cli.planner_script import cli, main, format_seconds

FAKE_LEG = {
    'agency': 'bart',
    'stop_id': 'woak',
    'stop_title': 'West Oakland',
    'stop_tag': None,
    'includes': [],
}
FAKE_TRIP = {'id': 1, 'name': 'test', 'legs': [1]}


@pytest.fixture
def planner_client(mocker):
    mock = MagicMock()
    mock.leg_list.return_value = [FAKE_LEG]
    mock.leg_create.return_value = FAKE_LEG
    mock.leg_show.return_value = ('bart', [])
    mock.leg_delete.return_value = True
    mock.trip_create.return_value = FAKE_TRIP
    mock.trip_list.return_value = [FAKE_TRIP]
    mock.trip_show.return_value = {'bart': {}, 'actransit': {}}
    mock.trip_delete.return_value = True
    mocker.patch('trip_planner.cli.planner_script.TripPlanner', return_value=mock)
    return mock


def test_leg_list(planner_client):
    result = CliRunner().invoke(cli, ['leg-list'], obj={})
    assert result.exit_code == 0


def test_leg_create(planner_client):
    result = CliRunner().invoke(cli, ['leg-create', 'bart', 'woak'], obj={})
    assert result.exit_code == 0


def test_leg_create_with_destinations(planner_client):
    result = CliRunner().invoke(
        cli, ['leg-create', 'bart', 'woak', '-d', 'antc', '-d', 'frmt'], obj={}
    )
    assert result.exit_code == 0


def test_leg_show(planner_client):
    result = CliRunner().invoke(cli, ['leg-show', '1'], obj={})
    assert result.exit_code == 0


def test_leg_delete(planner_client):
    result = CliRunner().invoke(cli, ['leg-delete', '1'], obj={})
    assert result.exit_code == 0


def test_trip_create(planner_client):
    result = CliRunner().invoke(cli, ['trip-create', 'mytrip', '1', '2'], obj={})
    assert result.exit_code == 0


def test_trip_list(planner_client):
    result = CliRunner().invoke(cli, ['trip-list'], obj={})
    assert result.exit_code == 0


def test_trip_show_empty(planner_client):
    result = CliRunner().invoke(cli, ['trip-show', '1'], obj={})
    assert result.exit_code == 0


def test_trip_show_with_data(planner_client):
    planner_client.trip_show.return_value = {
        'bart': {'West Oakland': {'Antioch': [45, 420, 5450]}},
        'actransit': {},
    }
    result = CliRunner().invoke(cli, ['trip-show', '1'], obj={})
    assert result.exit_code == 0
    assert 'West Oakland' in result.output
    assert '45, 7:00, 1:30:50' in result.output


def test_format_seconds():
    assert format_seconds(45) == '45'          # under a minute
    assert format_seconds(420) == '7:00'       # minutes:seconds
    assert format_seconds(650) == '10:50'
    assert format_seconds(5450) == '1:30:50'   # hours:minutes:seconds


def test_trip_delete(planner_client):
    result = CliRunner().invoke(cli, ['trip-delete', '1'], obj={})
    assert result.exit_code == 0

def test_main(mocker):
    mock_cli = mocker.patch('trip_planner.cli.planner_script.cli')
    main()
    mock_cli.assert_called_once_with(obj={})
