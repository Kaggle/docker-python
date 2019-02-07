import unittest
import numpy as np
from pykalman import KalmanFilter
from pykalman import UnscentedKalmanFilter
from pykalman.sqrt import CholeskyKalmanFilter, AdditiveUnscentedKalmanFilter

class TestPyKalman(unittest.TestCase):
    def test_kalman_filter(self):
        kf = KalmanFilter(transition_matrices = [[1, 1], [0, 1]], observation_matrices = [[0.1, 0.5], [-0.3, 0.0]])
        measurements = np.asarray([[1,0], [0,0], [0,1]])  # 3 observations
        kf = kf.em(measurements, n_iter=5)
        (filtered_state_means, filtered_state_covariances) = kf.filter(measurements)
        (smoothed_state_means, smoothed_state_covariances) = kf.smooth(measurements)
        return filtered_state_means
       
    def test_kalman_missing(self):
        kf = KalmanFilter(transition_matrices = [[1, 1], [0, 1]], observation_matrices = [[0.1, 0.5], [-0.3, 0.0]])
        measurements = np.asarray([[1,0], [0,0], [0,1]])  # 3 observations
        measurements = np.ma.asarray(measurements)
        measurements[1] = np.ma.masked
        kf = kf.em(measurements, n_iter=5)
        (filtered_state_means, filtered_state_covariances) = kf.filter(measurements)
        (smoothed_state_means, smoothed_state_covariances) = kf.smooth(measurements)
        return filtered_state_means

    def test_unscented_kalman(self):
        ukf = UnscentedKalmanFilter(lambda x, w: x + np.sin(w), lambda x, v: x + v, transition_covariance=0.1)
        (filtered_state_means, filtered_state_covariances) = ukf.filter([0, 1, 2])
        (smoothed_state_means, smoothed_state_covariances) = ukf.smooth([0, 1, 2])
        return filtered_state_means

    def test_online_update(self):
        kf = KalmanFilter(transition_matrices = [[1, 1], [0, 1]], observation_matrices = [[0.1, 0.5], [-0.3, 0.0]])
        measurements = np.asarray([[1,0], [0,0], [0,1]])  # 3 observations
        measurements = np.ma.asarray(measurements)
        measurements[1] = np.ma.masked   # measurement at timestep 1 is unobserved
        kf = kf.em(measurements, n_iter=5)
        (filtered_state_means, filtered_state_covariances) = kf.filter(measurements)
        for t in range(1, 3):
            filtered_state_means[t], filtered_state_covariances[t] = \
                kf.filter_update(filtered_state_means[t-1], filtered_state_covariances[t-1], measurements[t])
        return filtered_state_means

    def test_robust_sqrt(self):
        kf = CholeskyKalmanFilter(transition_matrices = [[1, 1], [0, 1]], observation_matrices = [[0.1, 0.5], [-0.3, 0.0]])
        ukf = AdditiveUnscentedKalmanFilter(lambda x, w: x + np.sin(w), lambda x, v: x + v, observation_covariance=0.1)
        
