import numpy as np
def percentile(arr, p):
    return float(np.percentile(arr, p)) if len(arr) else float("nan")
