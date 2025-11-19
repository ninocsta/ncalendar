from threading import local

_thread_locals = local()


def get_current_company():
    """Retorna a company do usuário logado"""
    return getattr(_thread_locals, 'company', None)


class CompanyMiddleware:
    """Middleware que armazena a company do usuário na thread"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            _thread_locals.company = request.user.company
        else:
            _thread_locals.company = None
        
        response = self.get_response(request)
        return response
