from api_generic import GenericApi


class GithubStatusApi(GenericApi):
    '''
    https://developer.github.com/v3/repos/statuses/
    '''
    BASE_URL_TEMPLATE = 'https://api.github.com/repos/%s/statuses/'

    def __init__(self, name, auth):
        base_url = self.BASE_URL_TEMPLATE % name
        self.auth = auth
        base_headers = {
            'accept': 'application/json',
        }
        GenericApi.__init__(self, base_url, base_headers, {})

    def post_status(self, commit, state, target_url, description, context):
        from json import dumps
        data = {
            'state': state,
            'target_url': target_url,
            'description': description,
            'context': context,
        }
        return self.post(commit, data=dumps(data), auth=self.auth)
