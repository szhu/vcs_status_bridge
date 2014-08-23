from os import getenv

env_var = 'STATUS_BRIDGE_CIRCLECI_API_TOKEN'
CIRCLECI_API_TOKEN = getenv(env_var)
assert CIRCLECI_API_TOKEN, '$%s not set' % env_var

env_var = 'STATUS_BRIDGE_GITHUB_API_TOKEN'
GITHUB_API_TOKEN = getenv(env_var)
assert GITHUB_API_TOKEN, '$%s not set' % env_var
