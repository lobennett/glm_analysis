import numpy as np
import pandas as pd

from network_analysis.glm.quality_control import est_contrast_vifs

def test_est_contrast_vifs():
    # TODO: Improve test cases.
    # Create design matrix with correlated regressors
    data = np.array([
        [1, 0, 0],
        [1, 0, 0],
        [0, 1, 0],
        [0, 1, 0],
        [0, 0, 1],
        [0, 0, 1],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ])
    desmat = pd.DataFrame(data, columns=['x1', 'x2', 'x3'])
    desmat['constant'] = 1

    # Define contrasts
    contrasts = {
        'x1 vs baseline': 'x1',
        'x2 vs baseline': 'x2',
        'x1 vs x2': 'x1 - x2',
    }

    vifs = est_contrast_vifs(desmat, contrasts)

    for contrast_name, vif in vifs.items():
        print(f'{contrast_name} has VIF={vif}')

    assert vifs['x1 vs baseline'] == 1.1111111111111112
    assert vifs['x2 vs baseline'] == 1.1111111111111112
    assert vifs['x1 vs x2'] == 0.8333333333333334
