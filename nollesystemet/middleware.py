from django.conf import settings


class PageCallStackMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.stack_size = settings.PAGE_CALL_STACK_SIZE
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if hasattr(request, 'session'):
            page_call_stack = request.session.get('page_call_stack', [])

            if not request.META.get('HTTP_REFERER', None):
                page_call_stack.append(None)
            page_call_stack.append(request.path)

            if len(page_call_stack) >= 3 and page_call_stack[-1] == page_call_stack[-3]:
                page_call_stack = page_call_stack[:-2]

            while len(page_call_stack) > self.stack_size:
                page_call_stack.pop(0)

            request.session['page_call_stack'] = page_call_stack
            request.session['last_url'] = page_call_stack[-2] if len(page_call_stack) >= 2 else None

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

