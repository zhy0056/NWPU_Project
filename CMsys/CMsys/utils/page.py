from rest_framework.pagination import LimitOffsetPagination


class LimitPagination(LimitOffsetPagination):
    default_limit = 5
    max_limit = 50
    limit_query_param = 'limit'
