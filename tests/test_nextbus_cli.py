from click.testing import CliRunner

from transit.cli.nextbus import cli, main


def test_agency_list(mocker):
    mocker.patch('transit.cli.nextbus.client.agency_list', return_value={'agency': []})
    result = CliRunner().invoke(cli, ['agency-list'])
    assert result.exit_code == 0


def test_route_list(mocker):
    mocker.patch('transit.cli.nextbus.client.route_list', return_value={'route': []})
    result = CliRunner().invoke(cli, ['route-list', 'sf-muni'])
    assert result.exit_code == 0


def test_route_show(mocker):
    mocker.patch('transit.cli.nextbus.client.route_show', return_value={'route': {}})
    result = CliRunner().invoke(cli, ['route-show', 'sf-muni', '38'])
    assert result.exit_code == 0


def test_route_messages(mocker):
    mocker.patch('transit.cli.nextbus.client.route_messages', return_value={'message': []})
    result = CliRunner().invoke(cli, ['route-messages', 'sf-muni', '38'])
    assert result.exit_code == 0


def test_stop_prediction(mocker):
    mocker.patch('transit.cli.nextbus.client.stop_prediction', return_value={'predictions': []})
    result = CliRunner().invoke(cli, ['stop-prediction', 'sf-muni', '15684'])
    assert result.exit_code == 0

def test_main(mocker):
    mock_cli = mocker.patch('transit.cli.nextbus.cli')
    main()
    mock_cli.assert_called_once_with()
