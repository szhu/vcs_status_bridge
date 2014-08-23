from api_circle import CircleStatusProjectApi
from api_github import GithubStatusApi
from auth import GITHUB_API_TOKEN, CIRCLECI_API_TOKEN


class CircleGithubRepo(object):
    def __init__(self, name):
        self.name = name

    def push_github_status(self, *args, **kwargs):
        github = GithubStatusApi(self.name, (GITHUB_API_TOKEN, 'x-oauth-basic'))
        github_req = github.post_status(*args, **kwargs)
        assert github_req.status_code == 201, 'Non-201 response from GitHub:\n%s\n%s' % (github_req.status_code, github_req.text)
        return github_req.json()

    def push_all_recent_statuses_single_request(self, limit, offset):
        circle = CircleStatusProjectApi(self.name, CIRCLECI_API_TOKEN)
        circle_statuses = circle.get_recent_circle_statuses_single_request(limit, offset)
        # Newer tests should override older tests
        circle_statuses.reverse()
        self.push_circle_statuses(circle_statuses)

    def push_all_recent_statuses(self, limit, offset):
        circle = CircleStatusProjectApi(self.name, CIRCLECI_API_TOKEN)
        circle_statuses = circle.get_recent_circle_statuses(limit, offset)
        # Newer tests should override older tests
        circle_statuses.reverse()
        self.push_circle_statuses(circle_statuses)

    def push_all_statuses_after(self, num):
        circle = CircleStatusProjectApi(self.name, CIRCLECI_API_TOKEN)
        circle_statuses = circle.get_all_circle_statuses_after(num)
        # Newer tests should override older tests
        circle_statuses.reverse()
        self.push_circle_statuses(circle_statuses)

    @property
    def save_file_path(self):
        from os.path import expanduser
        return expanduser('~/.config/circle-github-status-bridge/check-head/%s' % self.name)

    def get_check_head(self):
        with open(self.save_file_path, 'r') as f:
            return int(f.read().strip())

    def set_check_head(self, num):
        from os import makedirs
        from os.path import dirname
        try:
            makedirs(dirname(self.save_file_path))
        except OSError:
            pass
        with open(self.save_file_path, 'w') as f:
            f.write(str(num))

    def push_all_statuses_after_check_head(self):
        check_head = self.get_check_head()

        circle = CircleStatusProjectApi(self.name, CIRCLECI_API_TOKEN)
        circle_statuses = circle.get_all_circle_statuses_after(check_head)

        statuses, check_head = self.convert_statuses_and_find_check_head(circle_statuses)
        # Newer tests should override older tests
        statuses.reverse()
        self.push_statuses(statuses)

        if check_head is not None:
            self.set_check_head(check_head)

    def convert_statuses_and_find_check_head(self, circle_statuses):
        from sys import stderr
        from status import status_from_circle_status
        earliest_pending_build = None
        statuses = []
        for circle_status in circle_statuses:
            status = status_from_circle_status(circle_status)
            if status.pending:
                earliest_pending_build = status.num
            statuses.append(status)
        if len(statuses) == 0:
            print >> stderr, 'check head will not be modified'
            check_head = None
        elif earliest_pending_build is None:
            last_build = statuses[0].num
            print >> stderr, 'no builds pending, but last build is #%d (= new check head)' % last_build
            check_head = last_build
        else:
            print >> stderr, 'earliest pending build is #%d (= new check head)' % earliest_pending_build
            check_head = earliest_pending_build - 1
        return statuses, check_head

    def push_statuses(self, statuses):
        for status in statuses:
            self.push_status(status)

    def push_circle_statuses(self, circle_statuses):
        from status import status_from_circle_status
        for circle_status in circle_statuses:
            status = status_from_circle_status(circle_status)
            self.push_status(status)

    def push_status(self, status):
        from sys import stderr
        print >> stderr, 'Push status %s %s %s %s ...' % (
            status.commit[:7],
            '#%d' % status.num,
            status.status.ljust(7),
            status.message,
        ),
        stderr.flush()
        self.push_github_status(*status.github)
        print >> stderr, 'done'
