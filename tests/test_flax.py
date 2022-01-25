import unittest

import jax
import jax.numpy as jnp
import numpy as np
import optax

from flax import linen as nn
from flax.training import train_state 


class TestFlax(unittest.TestCase):

    def test_pooling(self):
        x = jnp.full((1, 3, 3, 1), 2.)
        mul_reduce = lambda x, y: x * y
        y = nn.pooling.pool(x, 1., mul_reduce, (2, 2), (1, 1), 'VALID')
        np.testing.assert_allclose(y, np.full((1, 2, 2, 1), 2. ** 4))

    def test_cnn(self):
        class CNN(nn.Module):
            @nn.compact
            def __call__(self, x):
                x = nn.Conv(features=32, kernel_size=(3, 3))(x)
                x = nn.relu(x)
                x = nn.avg_pool(x, window_shape=(2, 2), strides=(2, 2))
                x = nn.Conv(features=64, kernel_size=(3, 3))(x)
                x = nn.relu(x)
                x = nn.avg_pool(x, window_shape=(2, 2), strides=(2, 2))
                x = x.reshape((x.shape[0], -1))
                x = nn.Dense(features=256)(x)
                x = nn.relu(x)
                x = nn.Dense(features=120)(x)   
                x = nn.log_softmax(x)
                return x
            
        def create_train_state(rng, learning_rate, momentum):
            cnn = CNN()
            params = cnn.init(rng, jnp.ones([1, 224, 224, 3]))['params']
            tx = optax.sgd(learning_rate, momentum)
            return train_state.TrainState.create(
            apply_fn=cnn.apply, params=params, tx=tx)

        rng = jax.random.PRNGKey(0)
        rng, init_rng = jax.random.split(rng)

        learning_rate = 2e-5
        momentum = 0.9
        state = create_train_state(init_rng, learning_rate, momentum)
        self.assertEqual(0, state.step)


