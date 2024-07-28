import numpy as np
import json


init = '{}'
for weeks in range(7):
    dataTest = '{}'
    for time in range(2):
        load = json.loads(dataTest)
        days = {"day": "Senin"}
        load.update(days)

    getLoad = json.loads(init)
    getLoad.update(dataTest)

print(init)