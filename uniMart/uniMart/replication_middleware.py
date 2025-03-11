import sys
import random
class ReplicationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'GET':
            request.db = random.choice(['replica', 'replica-2'])
            if 'test' in sys.argv:
                request.db = 'default'
        else:
            request.db = 'default'
        return self.get_response(request)