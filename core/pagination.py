from rest_framework.pagination import PageNumberPagination
from django.http import JsonResponse

class StandardResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 20

    def get_paginated_response(self, data):
        return JsonResponse({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results_count': self.page.paginator.count,
            'results': data,
        })

class LargeResultsPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 200

    def get_paginated_response(self, data):
        return JsonResponse({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results_count': self.page.paginator.count,
            'results': data,
        })