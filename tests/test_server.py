# pylint: skip-file
# flake8: noqa
"""
Unit testing server.py
"""
import os
import sys
import pytest
import subprocess
import time
import requests
from unittest.mock import patch, Mock
from libversion import version_util

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../src')))

from server import (app,
                    num_pred_requests,
                    index_requests,
                    errored_requests,
                    cpu_usage,
                    memory_usage,
                    model_url)


lv = version_util.VersionUtil()
ver = lv.get_version()


@pytest.fixture
def client():
    """
    Fixture for test client
    """
    with app.test_client() as client:
        yield client


def test_index_route(client):
    """
    Testing index route
    """
    with patch('server.render_template') as mock_render:
        mock_render.return_value = "index.html content"
        response = client.get('/index')
        mock_render.assert_called_once_with(
            "index.html",
            inputDisplay="",
            result="",
            version=ver
        )
        assert response.status_code == 200
        assert response.data == b"index.html content"
        assert index_requests._value.get() == 1


@patch('requests.post')
def test_predict_route_success(mock_post, client):
    """
    Testing predict route with success
    """
    mock_response = Mock()
    mock_response.json.return_value = {'result': 'phishing'}
    mock_post.return_value = mock_response

    with patch('server.render_template') as mock_render:
        mock_render.return_value = "results.html content"
        url = "http://example.com"
        data = {"url": url}
        response = client.get('/predict', query_string=data)

        mock_post.assert_called_once_with(model_url, json=data, timeout=10)
        mock_render.assert_called_once_with(
            "results.html",
            inputDisplay=url,
            result='phishing',
            version=ver
        )
        assert response.status_code == 200
        assert response.data == b"results.html content"
        assert num_pred_requests._value.get() == 1


@patch('requests.post')
def test_predict_route_error(mock_post, client):
    """
    Testing predict route with failure
    """
    mock_post.side_effect = requests.exceptions.RequestException

    with patch('server.render_template') as mock_render:
        mock_render.return_value = "error.html content"
        url = "http://example.com"
        data = {"url": url}
        response = client.get('/predict', query_string=data)

        mock_post.assert_called_once_with(model_url, json=data, timeout=10)
        mock_render.assert_called_once_with(
            "error.html",
            inputDisplay=url,
            version=ver
        )
        assert response.status_code == 200
        assert response.data == b"error.html content"
        assert errored_requests._value.get() == 1


def test_metrics_route():
    """
    Testing metrics route
    """
    with patch('psutil.cpu_percent', return_value=50):
        with patch('psutil.virtual_memory') as mock_virtual_memory:
            mock_virtual_memory.return_value.used = 2048

            response = app.test_client().get('/metrics')
            assert response.status_code == 200
            assert response.mimetype == 'text/plain'
            assert b'cpu_usage' in response.data
            assert b'memory_usage' in response.data
            assert cpu_usage._value.get() == 50
            assert memory_usage._value.get() == 2048

def test_server_startup():
    '''
    Test that the server starts and responds OK to a request to /index
    '''
    process = subprocess.Popen(['python', 'src/server.py'])
    time.sleep(2) 

    try:
        response = requests.get('http://localhost:8080/index')
        assert response.status_code == 200
    finally:
        # Terminate the server
        process.terminate()
        process.wait()