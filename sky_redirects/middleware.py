from sky_redirects.models import DomainRedirect
from django.utils.http import urlquote
from django.http import HttpResponseRedirect


class DomainRedirectMiddleware(object):
    def process_request(self, request):
        host = request.get_host()
        domain_index = DomainRedirect.objects.cached_index()
        if host in domain_index:
            domain_redirect = domain_index[host]
            new_uri = '%s://%s%s%s' % (
                'https' if request.is_secure() else 'http',
                domain_redirect.redirect_to.domain,
                urlquote(request.path),
                (request.method == 'GET' and len(request.GET) > 0) and '?%s' % request.GET.urlencode() or ''
            )
            return HttpResponseRedirect(new_uri)