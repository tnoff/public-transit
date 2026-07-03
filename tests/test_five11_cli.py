from click.testing import CliRunner

from transit.cli.five11 import cli, main

FAKE_KEY = 'testkey'


def test_operators(mocker):
    mocker.patch('transit.cli.five11.client.operators', return_value=[])
    result = CliRunner().invoke(cli, ['-k', FAKE_KEY, 'operators'], obj={})
    assert result.exit_code == 0


def test_lines(mocker):
    mocker.patch('transit.cli.five11.client.lines', return_value=[])
    result = CliRunner().invoke(cli, ['-k', FAKE_KEY, 'lines', 'SC'], obj={})
    assert result.exit_code == 0


def test_stops(mocker):
    mocker.patch('transit.cli.five11.client.stops', return_value={})
    result = CliRunner().invoke(cli, ['-k', FAKE_KEY, 'stops', 'SC'], obj={})
    assert result.exit_code == 0


def test_stops_line_filter(mocker):
    stops = mocker.patch('transit.cli.five11.client.stops', return_value={})
    result = CliRunner().invoke(cli, ['-k', FAKE_KEY, 'stops', 'SC', '-l', '22'], obj={})
    assert result.exit_code == 0
    stops.assert_called_once_with(FAKE_KEY, 'SC', line_id='22')


def test_stop_monitoring(mocker):
    mocker.patch('transit.cli.five11.client.stop_monitoring', return_value={})
    result = CliRunner().invoke(
        cli, ['-k', FAKE_KEY, 'stop-monitoring', 'SC', '70021'], obj={}
    )
    assert result.exit_code == 0


def test_stop_monitoring_no_stop(mocker):
    # operator only, no stop code
    mocker.patch('transit.cli.five11.client.stop_monitoring', return_value={})
    result = CliRunner().invoke(cli, ['-k', FAKE_KEY, 'stop-monitoring', 'SC'], obj={})
    assert result.exit_code == 0


def test_main(mocker):
    mock_cli = mocker.patch('transit.cli.five11.cli')
    main()
    mock_cli.assert_called_once_with(obj={})
