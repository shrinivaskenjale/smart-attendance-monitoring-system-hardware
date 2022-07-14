PRODUCTION_MODE = True


if(PRODUCTION_MODE is True):
    BACKEND_BASE_URL = 'https://smart-attendance-monitoring.herokuapp.com'
else:
    BACKEND_BASE_URL = 'http://localhost:8080'


print(BACKEND_BASE_URL)
