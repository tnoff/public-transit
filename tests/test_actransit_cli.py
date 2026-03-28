from click.testing import CliRunner

from transit.cli.actransit import cli, main

FAKE_KEY = 'testkey'


def test_service_notices(mocker):
    mocker.patch('transit.cli.actransit.client.service_notices', return_value={'notices': []})
    result = CliRunner().invoke(cli, ['-k', FAKE_KEY, 'service-notices'], obj={})
    assert result.exit_code == 0


def test_route_list(mocker):
    mocker.patch('transit.cli.actransit.client.route_list', return_value=[])
    result = CliRunner().invoke(cli, ['-k', FAKE_KEY, 'route-list'], obj={})
    assert result.exit_code == 0


def test_route_directions(mocker):
    mocker.patch('transit.cli.actransit.client.route_directions', return_value={'directions': []})
    result = CliRunner().invoke(cli, ['-k', FAKE_KEY, 'route-directions', '51A'], obj={})
    assert result.exit_code == 0


def test_route_trips(mocker):
    mocker.patch('transit.cli.actransit.client.route_trips', return_value={'trips': []})
    result = CliRunner().invoke(
        cli, ['-k', FAKE_KEY, 'route-trips', '51A', 'To Rockridge BART'], obj={}
    )
    assert result.exit_code == 0


def test_route_stops(mocker):
    mocker.patch('transit.cli.actransit.client.route_stops', return_value={'stops': []})
    result = CliRunner().invoke(cli, ['-k', FAKE_KEY, 'route-stops', '51A', '12345'], obj={})
    assert result.exit_code == 0


def test_stop_predictions(mocker):
    mocker.patch(
        'transit.cli.actransit.client.stop_predictions',
        return_value={'bustime-response': {'prd': []}},
    )
    result = CliRunner().invoke(cli, ['-k', FAKE_KEY, 'stop-predictions', '55511'], obj={})
    assert result.exit_code == 0

def test_main(mocker):
    mock_cli = mocker.patch('transit.cli.actransit.cli')
    main()
    mock_cli.assert_called_once_with(obj={})
