class GenericApi(object):
    def __init__(self, base_url, base_headers, base_params):
        self.base_url = base_url
        self.base_params = base_params
        self.base_headers = base_headers

    def _merge_headers(self, headers):
        merged_headers = self.base_headers.copy()
        merged_headers.update(headers)
        return merged_headers

    def _merge_params(self, params):
        merged_params = self.base_params.copy()
        merged_params.update(params)
        return merged_params

    def _merge_url(self, slug):
        return self.base_url + slug

    def get(self, slug='', headers={}, params={}, *args, **kwargs):
        from requests import get
        return get(
            self._merge_url(slug),
            headers=self._merge_headers(headers),
            params=self._merge_params(params),
            *args, **kwargs
        )

    def post(self, slug='', headers={}, params={}, *args, **kwargs):
        from requests import post
        return post(
            self._merge_url(slug),
            headers=self._merge_headers(headers),
            params=self._merge_params(params),
            *args, **kwargs
        )
