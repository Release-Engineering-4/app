import os
from prometheus_client import (Counter,
                               Histogram,
                               Summary,
                               Gauge)
beta_test = os.getenv('BETA_TEST_FLAG', "False") == "True"

num_pred_requests = Counter('prediction_requests_total',
                            'Total number of prediction requests')
index_requests = Counter('flask_app_index_requests_total',
                         'Total number of requests to the index page')
errored_requests = Counter('error_requests_total',
                           'Total number of requests that errored out')
correct_predictions = Counter('correct_predictions',
                              'Total number of requests giving \
                                correct prediction')
incorrect_predictions = Counter('incorrect_predictions',
                                'Total number of requests giving \
                                    incorrect prediction')
cpu_usage = Gauge('cpu_usage',
                  'CPU usage of app')
memory_usage = Gauge('memory_usage',
                     'Memory usage of app')
model_accuracy = Gauge('model_accuracy',
                       'Measure of prediction accuracy based on feedback')
request_duration_histogram = Histogram(
    'flask_app_request_duration_seconds',
    'Histogram for request duration in seconds')
request_duration_summary = Summary(
    'flask_app_request_duration_seconds_summary',
    'Summary for request duration in seconds')

if beta_test:
    beta_correct_predictions = Counter('beta_correct_predictions',
                                'Total number of requests giving \
                                correct prediction to beta')
    beta_incorrect_predictions = Counter('beta_incorrect_predictions',
                                    'Total number of requests giving \
                                        incorrect prediction to beta')
    beta_model_accuracy = Gauge('beta_model_accuracy',
                        'Measure of prediction accuracy of beta model based on feedback')