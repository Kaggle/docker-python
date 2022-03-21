import unittest
import tensorflow as tf
import tf_agents

class TestTFAgents(unittest.TestCase):
    def test_tf_agents(self):
        action_spec = tf_agents.specs.BoundedTensorSpec(
            (),
            tf.int32,
            minimum=0,
            maximum=3,
            name="action"
        )
        observation_spec = tf_agents.specs.BoundedTensorSpec(
            (3,3),
            tf.uint8,
            minimum=0,
            maximum=1,
            name="observation"
        )
        reward_spec = tf_agents.specs.BoundedTensorSpec(
            (),
            tf.float32,
            minimum=0.0,
            maximum=1.0,
            name="reward"
        )
        time_step_spec = tf_agents.trajectories.time_step.time_step_spec(
            observation_spec,
            reward_spec,
        )
        random_policy = tf_agents.policies.random_tf_policy.RandomTFPolicy(
            time_step_spec=time_step_spec,
            action_spec=action_spec
        )
        random_env = tf_agents.environments.RandomTFEnvironment(
            time_step_spec,
            action_spec
        )

        time_step = random_env.reset()

        action_step = random_policy.action(time_step=time_step)
        self.assertTrue(isinstance(action_step, tf_agents.trajectories.PolicyStep))

        next_time_step = random_env.step(action_step.action)
        self.assertTrue(isinstance(next_time_step, tf_agents.trajectories.time_step.TimeStep))

