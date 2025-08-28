import numpy as np

class Sampler:
    def __init__(self, seed: int):
        self.rng = np.random.default_rng(seed)

    def exp_minutes(self, mean):
        return max(0.01, float(self.rng.exponential(mean)))

    def lognormal_minutes(self, mean, sigma=0.6):
        mu = np.log(mean) - 0.5 * sigma**2
        return max(0.5, float(self.rng.lognormal(mu, sigma)))
