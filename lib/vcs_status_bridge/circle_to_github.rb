require 'active_support'
require 'active_support/core_ext/hash'
require 'active_support/core_ext/string/strip'
require 'fileutils'
require_relative 'circle'
require_relative 'github'
require_relative 'util'

module VcsStatusBridge
  module Circle
    class Status
      THE_BUILD = 'The Circle CI build'

      def to_github
        require_relative 'env'
        status_opts = {}

        if %w(finished scheduled).include? lifecycle
          case outcome
          when 'success'
            status_opts[:state] = 'success'
            status_opts[:description] = "#{THE_BUILD} passed"
          when 'failed'
            status_opts[:state] = 'failure'
            status_opts[:description] = "#{THE_BUILD} failed"
          when 'canceled'
            status_opts[:state] = 'error'
            status_opts[:description] = "#{THE_BUILD} was canceled"
          when 'timedout'
            status_opts[:state] = 'error'
            status_opts[:description] = "#{THE_BUILD} timed out"
          when 'infrastructure_fail'
            status_opts[:state] = 'error'
            status_opts[:description] = "The Circle CI infrastructure failed"
          else
            status_opts[:state] = 'error'
            status_opts[:description] = "#{THE_BUILD} returned outcome: #{outcome}"
          end
          # sometimes outcome != status == 'fixed' and let's convey that too
          status_opts[:description] << " (#{status})" unless status == outcome

        elsif lifecycle == 'running'
          status_opts[:state] = 'pending'
          status_opts[:description] = "#{THE_BUILD} is running"
        elsif usage_queued_at
          queue_date = format_iso_date(usage_queued_at, Env.timezone)
          status_opts[:state] = 'pending'
          status_opts[:description] = "#{THE_BUILD} was queued #{queue_date}"
        elsif lifecycle == 'queued'
          status_opts[:state] = 'pending'
          status_opts[:description] = "#{THE_BUILD} is queued"
        elsif lifecycle == 'not_running'
          status_opts[:state] = 'error'
          status_opts[:description] = "#{THE_BUILD} is not running"
        else
          Util.errln <<-EOF.strip_heredoc
            --- Unparseable status: ---
            #{as_json}
            --- End of status ---
          EOF
          status_opts[:state] = 'error'
          status_opts[:description] = "The Circle CI-GitHub bridge could not understand the status from Circle CI"
        end

        status_opts.merge! commit: vcs_revision, target_url: build_url, build_num: build_num
        Github::Status.new status_opts
      end
    end
  end

  class CircleToGithub
    attr_reader :name
    DEFAULT_OPTS = {
      verbose: true,
      use_env: true
    }

    def initialize(name)
      @name = name
    end

    def load_check_head
      File.open(check_head_save_path, 'r') do |file|
        file.read
      end
    end

    def save_check_head(num)
      FileUtils.mkdir_p File.dirname(check_head_save_path)
      File.open(check_head_save_path, 'w') do |file|
        file.write(num.to_s)
      end
    end

    def check_head_save_path
      require_relative 'env'
      "#{Env.check_head_save_path_prefix}/#{name}"
    end

    def push_statuses_after_check_head(opts = {})
      opts.reverse_merge!(DEFAULT_OPTS)
      check_head = load_check_head

      circle_project = Circle::Project.new(@name, opts)
      github_repo = Github::Repo.new(@name, opts)

      statuses = circle_project.statuses_after(
                    check_head,
                    opts.merge(chronological: true)
                  ).map(&:to_github)
      statuses.each do |status|
        github_repo.push_status status
      end

      check_head = Github::Status.find_check_head(statuses)
      save_check_head(check_head) unless check_head.nil?
      nil
    end
  end
end
