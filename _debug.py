#!/usr/bin/env python
# Some functions that were helpful in building this project. If the API changes,
# or needs to be debugged, these might be helpful again. These functions
# probably are not completely working right now, so use with caution.


def find_circle_status_by_commit(commit):
    from api_circle import CircleStatusProjectApi
    from auth import CIRCLECI_API_TOKEN

    circle = CircleStatusProjectApi('IFTTT/ifttt_front_end', CIRCLECI_API_TOKEN)
    data = circle.get_recent().json()
    try:
        for status in data:
            if status['vcs_revision'].startswith(commit):
                return status
        else:
            raise ValueError('Commit %s not found' % commit)
    except:
        print data
        raise


def push_status_by_commit(commit):
    from api_github import GithubStatusApi
    from auth import GITHUB_API_TOKEN
    from status import circle_status_to_github_status
    from pprint import pprint
    circle_status = find_circle_status_by_commit(commit)
    pprint(circle_status)

    commit = circle_status['vcs_revision']
    url = circle_status['build_url']
    status, message = circle_status_to_github_status(circle_status)
    print commit, status, url, message

    print
    raw_input('[enter] to continue')
    print

    github = GithubStatusApi('IFTTT/ifttt_front_end', GITHUB_API_TOKEN)
    github_req = github.post_status(commit, status, url, message, 'continuous-integration/circle')
    pprint(github_req)


def test_circle():
    from api_circle import CircleStatusProjectApi
    from auth import CIRCLECI_API_TOKEN
    # from pprint import pprint

    circle = CircleStatusProjectApi('IFTTT/ifttt_front_end', CIRCLECI_API_TOKEN)
    circle_req = circle.get_recent()
    data = circle_req.json()
    commit = data[1]
    print commit['build_url']
    print commit['outcome']
    print commit['vcs_revision']


def test_circle_get_recent():
    from pprint import pprint
    from circle_github_repo import CircleGithubRepo
    ife = CircleGithubRepo('IFTTT/ifttt_front_end')
    recent_circle_statuses = ife.get_recent_circle_statuses(100, 300)
    for circle_status in recent_circle_statuses:
        pprint(circle_status)
        # s = circle_status['queued_at'] if 'queued_at' in circle_status else circle_status.keys()
        # print circle_status['build_url'], s


def test_github():
    from pprint import pprint
    from api_github import GithubStatusApi
    from auth import GITHUB_API_TOKEN

    github = GithubStatusApi('IFTTT/ifttt_front_end', (GITHUB_API_TOKEN, 'x-oauth-basic'))
    github_req = github.post_status(
        '5bb5be8c12b8a6d00a2ee4ef65b85fbb3693bc86',
        'success',
        'https://circleci.com/gh/IFTTT/ifttt_front_end/9862',
        'YAAAAAAAAYYYYYY (test by szhu)'
    )
    data = github_req.json()
    pprint(data)
