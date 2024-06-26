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

os.environ["BETA_TEST_FLAG"] = "True"

from server import (app, 
                    model_url,
                    model_url_beta,
                    beta_test)

from metrics_init import *


lv = version_util.VersionUtil()
ver = lv.get_version()


@pytest.fixture
def client():
    """
    Fixture for test client
    """
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def reset_prometheus_counters():
    num_pred_requests._value.set(0)
    index_requests._value.set(0)
    errored_requests._value.set(0)
    correct_predictions._value.set(0)
    incorrect_predictions._value.set(0)
    yield


def test_index_route(client):
    """
    Testing index route
    """
    result_tx = ""
    if beta_test:
        result_tx = "This app will test our beta model too"
    with patch('server.render_template') as mock_render:
        mock_render.return_value = "index.html content"
        response = client.get('/index')
        mock_render.assert_called_once_with(
            "index.html",
            inputDisplay="",
            result=result_tx,
            feedback="",
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
    mock_response.json.return_value = {"prediction": [[0.6]]}
    mock_post.return_value = mock_response

    with patch('server.render_template') as mock_render:
        mock_render.return_value = "results.html content"
        url = "http://example.com"
        data = {"url": url}
        response = client.get('/predict', query_string=data)

        mock_post.assert_called_once_with(model_url, json=data, timeout=30)
        mock_render.assert_called_once_with(
            "results.html",
            inputDisplay=url,
            result="The provided input is a phishing URL!",
            version=ver,
        )
        assert response.status_code == 200
        assert response.data == b"results.html content"
        assert num_pred_requests._value.get() == 1


@patch("requests.post")
def test_predict_route_phishing(mock_post, client):
    """
    Testing predict route with phishing
    """
    mock_response = Mock()
    mock_response.json.return_value = {"prediction": [[0.2]]}
    mock_post.return_value = mock_response

    with patch("server.render_template") as mock_render:
        mock_render.return_value = "results.html content"
        url = "http://example.com"
        data = {"url": url}
        response = client.get("/predict", query_string=data)

        mock_post.assert_called_once_with(model_url, json=data, timeout=30)
        mock_render.assert_called_once_with(
            "results.html",
            inputDisplay=url,
            result="The provided input is not a phishing URL!",
            version=ver,
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

        mock_post.assert_called_once_with(model_url, json=data, timeout=30)
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

@patch('requests.post')
def test_feedback_route_correct(mock_post, client):
    """
    Testing feedback route
    """
    correct_predictions._value.set(0)
    incorrect_predictions._value.set(0)
    model_accuracy.set(0)
    fb_data = {"prediction_feedback": "correct"}
    mock_response = Mock()
    mock_response.json.return_value = {"prediction": [[0.6]]}
    mock_post.return_value = mock_response
    feedback_given = "Thank you for your feedback!"

    with patch("server.render_template") as mock_render:
        if beta_test:
            url = "http://example.com"
            data = {"url": url}
            response = client.get('/predict', query_string=data) 
            mock_post.assert_called_once_with(model_url, json=data, timeout=30)
            assert response.status_code == 200
            feedback_given = f'{feedback_given} This will help improve our model.'
        
        response = app.test_client().get('/feedback', query_string=fb_data)
        mock_render.return_value = "index.html content"
        mock_render.assert_called_with(
            "index.html",
            inputDisplay="",
            result="",
            feedback=feedback_given,
            version=ver,
        )
        assert correct_predictions._value.get() == 1
        assert model_accuracy._value.get() == 1.0

@patch('requests.post')
def test_feedback_route_incorrect(mock_post, client):
    """
    Testing feedback route
    """
    correct_predictions._value.set(0)
    incorrect_predictions._value.set(0)
    model_accuracy.set(0)
    data = {"prediction_feedback": "incorrect"}
    mock_response = Mock()
    mock_response.json.return_value = {"prediction": [[0.6]]}
    mock_post.return_value = mock_response
    feedback_given = "Thank you for your feedback!"

    with patch("server.render_template") as mock_render:
        if beta_test:
            url = "http://example.com"
            data = {"url": url}
            response = client.get('/predict', query_string=data) 
            mock_post.assert_called_once_with(model_url, json=data, timeout=30)
            assert response.status_code == 200
            feedback_given = f'{feedback_given} This will help improve our model.'

        response = app.test_client().get('/feedback', query_string=data)
        mock_render.return_value = "index.html content"
        mock_render.assert_called_with(
            "index.html",
            inputDisplay="",
            result="",
            feedback=feedback_given,
            version=ver,
        )
        assert incorrect_predictions._value.get() == 1
        assert model_accuracy._value.get() == 0.0


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
