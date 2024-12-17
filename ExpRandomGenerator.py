import numpy as np

class ExpRandGenerator:
    """
    Generates exponentially distributed random values based on a given rate parameter λ.
    """

    def gen_random(self, lamda):
        """
        Generate a random value from an exponential distribution with the given rate λ.

        :param lamda: The rate parameter (λ). Must be positive.
        :return: A random exponentially distributed value (float) in seconds.
        """
        if lamda <= 0:
            raise ValueError("Rate parameter λ must be positive.")
        scale = 1.0 / lamda
        return np.random.exponential(scale)
