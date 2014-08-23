#!/usr/bin/env python

from circle_github_repo import CircleGithubRepo
from api_circle import CircleStatusProjectApi
from auth import CIRCLECI_API_TOKEN


def main(command, repo_name, *args):

    if command == 'get_recent_circle_statuses':
        ife = CircleStatusProjectApi(repo_name, CIRCLECI_API_TOKEN)
        from pprint import pprint
        pprint(ife.get_recent_circle_statuses(*args))

    elif command == 'push_all_recent_statuses':
        ife = CircleGithubRepo(repo_name)
        ife.push_all_recent_statuses(*args)

    elif command == 'get_all_circle_statuses_after':
        ife = CircleStatusProjectApi(repo_name, CIRCLECI_API_TOKEN)
        from pprint import pprint
        pprint(ife.get_all_circle_statuses_after(*args))

    elif command == 'push_all_statuses_after_check_head':
        ife = CircleGithubRepo(repo_name)
        ife.push_all_statuses_after_check_head()

    elif command == 'set_check_head':
        ife = CircleGithubRepo(repo_name)
        ife.set_check_head(*args)
        print 'Check head is now #%s' % ife.get_check_head()

    elif command == 'get_check_head':
        ife = CircleGithubRepo(repo_name)
        print(ife.get_check_head(*args))

    else:
        raise ValueError('command %s not valid' % command)

from sys import argv
try:
    main(*argv[1:])
    exit(0)
except (KeyboardInterrupt, EOFError), exc:
    from sys import stderr
    print >> stderr, exc
    exit(1)
