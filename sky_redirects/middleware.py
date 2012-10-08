from sky_redirects.models import DomainRedirect, RegexPathRedirect
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


class RegexRedirectMiddleware(object):
    def process_request(self, request):
        # import pdb; pdb.set_trace()
        path = request.path
        domain = request.get_host()
        redirects = RegexPathRedirect.objects.cached_index()
        for redir in redirects:
            regex = redir.compiled_regex
            matches = regex.match(path)
            if matches:
                if '://' in redir.redirect_to:
                    return HttpResponseRedirect(redir.redirect_to)
                else:
                    new_uri = '%s://%s%s%s' % (
                        'https' if request.is_secure() else 'http',
                        domain,
                        redir.redirect_to % matches.groupdict(),
                        (request.method == 'GET' and len(request.GET) > 0) and '?%s' % request.GET.urlencode() or ''
                    )
                    return HttpResponseRedirect(new_uri)

