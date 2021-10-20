import requests
import settings


def get_used_percentage_cpu():
    response = requests.post(settings.GET_ACCOUNT_INFO_URL, json={'account_name': settings.ACCOUNT_NAME}).json()
    cpu_limit = response.get('cpu_limit')
    used_cpu = cpu_limit.get('used')
    max_cpu = cpu_limit.get('max')

    percentage_used = round((used_cpu * 100) / max_cpu)
    print(percentage_used)

    return percentage_used
