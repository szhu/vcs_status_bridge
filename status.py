from timezones import TIMEZONE


def convert_date(iso_date, timezone_name):
    from dateutil.parser import parse as dateparse
    from pytz import timezone

    try:
        utcdate = dateparse(iso_date)
        localdate = utcdate.astimezone(timezone(timezone_name))
        return localdate.strftime("on %h %d, %Y at %I:%M %p %Z")
    except ValueError:
        return 'at %s' % iso_date


def circle_status_to_github_status(circle_status):
    outcome = circle_status['outcome']
    status = circle_status['status']
    lifecycle = circle_status['lifecycle']
    queued_at = circle_status['usage_queued_at'] if 'usage_queued_at' in circle_status else None

    # sometimes status == 'fixed' and let's convey that too
    if status != outcome:
        status_append = ' (%s)' % status
    else:
        status_append = ''

    if lifecycle == 'finished' or lifecycle == 'scheduled':

        if outcome == 'success':
            return 'success', 'The Circle CI build passed' + status_append

        elif outcome == 'failed':
            return 'failure', 'The Circle CI build failed' + status_append

        elif outcome == 'canceled':
            return 'error', 'The Circle CI build was canceled' + status_append

        elif outcome == 'timedout':
            return 'error', 'The Circle CI build timed out' + status_append

        elif outcome == 'infrastructure_fail':
            return 'error', 'The Circle CI infrastructure failed' + status_append

        else:
            return 'error', 'The Circle CI build returned outcome: %s' % outcome + status_append

    elif lifecycle == 'running':
        return 'pending', 'The Circle CI build is running'

    elif queued_at:
        queue_date = convert_date(queued_at, TIMEZONE)
        return 'pending', 'The Circle CI build was queued %s' % queue_date

    elif lifecycle == 'queued':
        return 'pending', 'The Circle CI build is queued'

    elif lifecycle == 'not_running':
        return 'error', 'The Circle CI build is not running'

    return 'error', 'The Circle CI bridge could not understand the status returned by Circle CI'


class Status(object):
    def __init__(self, circle_status):
        commit = circle_status['vcs_revision']
        url = circle_status['build_url']
        status, message = circle_status_to_github_status(circle_status)

        self.circle = circle_status
        self.github = [commit, status, url, message, 'continuous-integration/circle']

        self.commit = commit
        self.message = message
        self.num = circle_status['build_num']
        self.pending = status == 'pending'
        self.status = status


def status_from_circle_status(circle_status):
    return Status(circle_status)
