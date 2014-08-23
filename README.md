vcs_status_bridge
=================

This thing can pull build statuses from [Circle CI](http://circleci.com/) and push them onto GitHub. This gem lays out the framework to extend this functionality to other CI and VCS providers as well.

The gem was created because for some time, Circle CI [didn't allow fine-grained permissions](https://circleci.com/docs/github-permissions) and required repo write access just to post statuses. The status bridge solved the problem by using GitHub personal access tokens that allowed only updating statuses.

Circle CI now supports pushing statuses to GitHub with a minimal set of permissions, so this project is obsolete. However, it can be modified to bridge other CI and VCS systems.

## Usage

**Setting it up**

```sh
# set the earliest build that should be checked
bin/circle-to-github-status IFTTT/ifttt_front_end set_check_head 12345
```

**Using it**

```sh
export STATUS_BRIDGE_CIRCLECI_API_TOKEN=1234567890123456789012345678901234567890
export STATUS_BRIDGE_GITHUB_API_TOKEN=1234567890123456789012345678901234567890
bin/circle-to-github-status IFTTT/ifttt_front_end push_statuses_after_check_head
```

If you feel secure enough about it, you can put the two `export` lines in `.bashrc`.

**This thing is a RubyGem+executable too!**

```sh
make  # to build the gem
make install  # to install the gem
make uninstall  # to remove the gem
circle-to-github-status  # to do stuff
```


## About the output format of the script

- Progress and errors goes to `stderr`
- Return value-like output goes to `stdout`
