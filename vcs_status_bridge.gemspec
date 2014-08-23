require './lib/vcs_status_bridge/version'

Gem::Specification.new do |gem|
  gem.name        = 'vcs_status_bridge'
  gem.summary     = 'Send Circle CI statuses to GitHub.'
  gem.description = <<-END
      Send Circle CI statuses to GitHub.
      This gem lays out the framework to extend this functionality to other
      CI and VCS providers as well.
    END

  gem.version     = VcsStatusBridge::VERSION
  gem.date        = '2014-08-15'

  gem.homepage    = 'https://github.com/IFTTT/vcs_status_bridge'
  gem.authors     = ['Sean Zhu']
  gem.email       = 'sean.zhu@ifttt.com'
  gem.license     = 'MIT'

  gem.add_dependency 'activesupport', '~> 4.1'
  gem.add_dependency 'httparty', '~> 0.13'
  gem.executables = ['circle-to-github-status']
  gem.files       = `git ls-files`.split($RS)
  gem.require_paths = ['lib']
end
