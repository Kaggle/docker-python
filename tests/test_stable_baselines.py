import unittest

import numpy as np
import gym
from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO1

class TestStableBaselines(unittest.TestCase):
    def test_PPO1(self):
        # make the environment
        env = gym.make('CartPole-v1')
        env = DummyVecEnv([lambda: env])  
        # create and train an agent/model
        model = PPO1(MlpPolicy, env, verbose=0)
        model = model.learn(total_timesteps=1000)
        # predict with the trained agent/model
        obs = env.reset()
        action, _states = model.predict(obs)
        # assert statements
        self.assertTrue(type(action) == np.ndarray)
        self.assertTrue(len(action) == 1)
        self.assertTrue(type(action[0]) in [np.int64, int])