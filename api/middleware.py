from django.conf import settings

counter = 0

def checkcounter():
    global counter
    return counter

def resetcounter():
    global counter
    counter = 0
    return counter

class CounterMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        global counter
        counter += 1
        response = self.get_response(request)
        return response
