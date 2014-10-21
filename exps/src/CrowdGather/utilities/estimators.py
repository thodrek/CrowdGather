# Module containing auto-regressive estimators
import statsmodels.tsa.ar_model as ts
import statsmodels.tsa.api as stap
import numpy as np

def trainPredictARMA(observedData):
    # Initialize auto-regressive(AR) model
    model = ts.AR(observedData, freq='D')
    # Fit AR model
    result = model.fit(maxlag = 3,method = 'cmle',trend = 'c',maxiter = 35,disp = -1)
    model = result.model
    params = result.params
    # Predict for new query
    prediction = model.predict(params = params, start = len(observedData)-1, end = len(observedData) +10)
    return round(prediction[2])


def trainPredictVARMA(observedData,intervals=None):
    # Initialize input to vector auto-regressive(VAR) model
    data = np.array(observedData)
    data = data.transpose()

    # Initialize model
    model = stap.VAR(data)

    # Fit model
    result = model.fit()
    lag_order = result.k_ar
    if intervals is None:
        prediction = result.forecast(data[-lag_order:], 1)
        sampleSize = prediction[0][0]
        newItems = prediction[0][1]
        return sampleSize, newItems
    else:
        prediction = result.forecast_interval(data[-lag_order:], 1)
        mid_sampleSize = prediction[0][0][0]
        mid_newItems = prediction[0][0][1]
        min_sampleSize = prediction[1][0][0]
        min_newItems = prediction[1][0][1]
        max_sampleSize = prediction[2][0][0]
        max_newItems = prediction[2][0][1]
        return min_sampleSize, min_newItems, mid_sampleSize, mid_newItems, max_sampleSize, max_newItems






