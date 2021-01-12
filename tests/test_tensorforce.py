import unittest

from tensorforce import Agent, Environment

class TestTensorforce(unittest.TestCase):
    # based on https://github.com/tensorforce/tensorforce/tree/master#quickstart-example-code.
    def test_quickstart(self):
        environment = Environment.create(
            environment='gym', level='CartPole', max_episode_timesteps=500
        )

        agent = Agent.create(
            agent='tensorforce',
            environment=environment,  # alternatively: states, actions, (max_episode_timesteps)
            memory=1000,
            update=dict(unit='timesteps', batch_size=32),
            optimizer=dict(type='adam', learning_rate=3e-4),
            policy=dict(network='auto'),
            objective='policy_gradient',
            reward_estimation=dict(horizon=1)
        )

        # Train for a single episode.
        states = environment.reset()
        actions = agent.act(states=states)
        states, terminal, reward = environment.execute(actions=actions)

        self.assertEqual(4, len(states))
        self.assertFalse(terminal)
        self.assertEqual(1, reward)
