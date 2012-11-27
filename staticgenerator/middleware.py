import re
from django.conf import settings
from staticgenerator import StaticGenerator

class StaticGeneratorMiddleware(object):
    """
    This requires settings.STATIC_GENERATOR_URLS tuple to match on URLs
    
    Example::
        
        STATIC_GENERATOR_URLS = (
            r'^/$',
            r'^/blog',
        )
        
    """
    urls = tuple([re.compile(url) for url in settings.STATIC_GENERATOR_URLS])
    excluded_urls = tuple([re.compile(url) for url in getattr(settings, 'STATIC_GENERATOR_EXCLUDE_URLS', [])])
    exclude_params = dict((key, 1) for key in getattr(settings, 'STATIC_GENERATOR_EXCLUDE_PARAMS',[]))
    gen = StaticGenerator()
    
    def process_response(self, request, response):
        path = request.path_info
        query_string = request.META.get('QUERY_STRING', '')
        if response.status_code == 200:
            if (getattr(settings, 'STATIC_GENERATOR_ANONYMOUS_ONLY', False)
                and not request.user.is_anonymous()):
                print "Not anonymous"
                return response

            excluded = False
            for url in self.excluded_urls:
                if url.match(path):
                    excluded = True
                    print "Excluding this url"
                    break

            intersect = list(
                set(request.GET.keys()) & 
                set(getattr(settings, 'STATIC_GENERATOR_EXCLUDE_PARAMS',[])))
            if len(intersect) > 0:
                print "Excluding because of params"
                excluded = True

            if not excluded:
                for url in self.urls:
                    if url.match(path):
                        print "Generating cache file"
                        self.gen.publish_from_path(path, query_string, response.content)
                        break

        return response
