from api_generic import GenericApi


class CircleStatusProjectApi(GenericApi):
    '''
    https://circleci.com/docs/api
    '''
    BASE_URL_TEMPLATE = 'https://circleci.com/api/v1/project/%s'
    CIRCLE_MAX_LIMIT = 100

    def __init__(self, name, circle_token):
        base_url = self.BASE_URL_TEMPLATE % name
        base_params = {'circle-token': circle_token}
        base_headers = {'accept': 'application/json'}
        GenericApi.__init__(self, base_url, base_headers, base_params)

    def get_recent(self, limit=None, offset=None):
        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        return self.get(params=params)

    def get_recent_circle_statuses_single_request(self, limit, offset, verbose=True):
        if verbose:
            from sys import stderr
            print >> stderr, 'Get recent Circle CI statuses...',
            stderr.flush()

        circle_req = self.get_recent(limit, offset)
        recent_circle_statuses = circle_req.json()
        assert circle_req.status_code == 200, 'Non-200 response from Circle CI:\n%r' % circle_req.text
        if verbose:
            print >> stderr, '%d statuses received' % len(recent_circle_statuses)
        return recent_circle_statuses

    def get_recent_circle_statuses(self, limit, offset, verbose=True):
        '''
        The Circle API does not allow a `limit` above self.CIRCLE_MAX_LIMIT
        (currently 100). This method allows the limit to be increased beyond
        that by combining multiple requests.
        '''
        limit = int(limit)
        offset = int(offset)
        max_limit = self.CIRCLE_MAX_LIMIT

        if verbose:
            from sys import stderr
            print >> stderr, 'Get recent Circle CI statuses...',
            stderr.flush()

        recent_circle_statuses = []
        while limit > 0:
            if verbose:
                print >> stderr, '%d...' % offset,
                stderr.flush()
            limit_for_this_request = min(limit, max_limit)
            recent_circle_statuses += self.get_recent_circle_statuses_single_request(limit_for_this_request, offset, verbose=False)
            offset += max_limit
            limit -= max_limit
        if verbose:
            print >> stderr, '%d statuses received' % len(recent_circle_statuses)
        return recent_circle_statuses

    def get_all_circle_statuses_after(self, target_num, verbose=True):
        '''
        Get statuses in reverse chronological order until all build numbers
        higher than `target_num` have been encountered.
        '''
        target_num = int(target_num)
        limit = self.CIRCLE_MAX_LIMIT
        num = float('inf')
        offset = 0

        if verbose:
            from sys import stderr
            print >> stderr, 'Get Circle CI statuses after build #%d...' % target_num
            stderr.flush()

        recent_circle_statuses = []
        # Edge case example:
        # Assume we want to get all statuses after #1234 (= target_num).
        # We can stop as soon as num is #1235 (= num).
        while num > target_num + 1:
            if verbose:
                print >> stderr, '%d...' % offset,
                stderr.flush()
            tmp_circle_statuses = self.get_recent_circle_statuses_single_request(limit, offset, verbose=False)
            for circle_status in tmp_circle_statuses:
                num = circle_status['build_num']
                if verbose:
                    print >> stderr, '#%d' % num,
                    stderr.flush()
                if not num > target_num:
                    break
                recent_circle_statuses.append(circle_status)
            offset += limit
            if verbose:
                print >> stderr
        if verbose:
            print >> stderr, '%d statuses received;' % len(recent_circle_statuses),
        return recent_circle_statuses
