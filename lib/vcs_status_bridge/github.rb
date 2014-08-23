require 'active_support'
require 'active_support/core_ext/hash'
require 'active_support/core_ext/string/strip'
require 'httparty'
require_relative 'strict_ostruct'
require_relative 'util'

module VcsStatusBridge
  # https://developer.github.com/v3/repos/statuses/
  module Github
    # The status of a CircleCI build.
    class Status < StrictOpenStruct
      require_key :commit, :state, :target_url, :description, :context, :build_num
      DEFAULT_OPTS = {
        verbose: true
      }

      def evaluate
        unless %w(success failure pending Util.error).include? state
          raise "unrecognized state given: #{state}"
        end
        self.context ||= 'continuous-integration/circle'
      end

      def pending?
        state == 'pending'
      end

      class << self
        def find_check_head(statuses, opts = {})
          opts.reverse_merge!(DEFAULT_OPTS)
          earliest_pending_build = nil
          statuses.reverse_each do |status|
            earliest_pending_build = status.build_num if status.pending?
          end
          if statuses.length == 0
            check_head = nil
            Util.errln 'check head will not be modified' if opts[:verbose]
          elsif earliest_pending_build.nil?
            last_build = statuses[0].build_num
            check_head = last_build
            Util.errln "no builds pending, but last build is ##{last_build} (= new check head)" if opts[:verbose]
          else
            check_head = earliest_pending_build - 1
            Util.errln "earliest pending build is ##{earliest_pending_build} (= new check head + 1)" if opts[:verbose]
          end
          check_head
        end
      end
    end

    # A GitHub repo that accepts pushed statuses.
    class Repo
      include HTTParty
      # https://developer.github.com/v3/#user-agent-required
      headers('accept' => 'application/json', 'user-agent' => 'HTTParty')
      DEFAULT_OPTS = {
        verbose: true,
        use_env: true
      }

      def initialize(name, opts = {})
        if opts[:use_env]
          require_relative 'env'
          opts.merge! username: Env.github_api_token, password: 'x-oauth-basic'
        end
        raise "required param `username' not given" if opts[:username].nil?
        raise "required param `password' not given" if opts[:password].nil?
        @name = name
        @options = {
          basic_auth: opts.slice(:username, :password)
        }
      end

      def push_status(status, opts = {})
        opts.reverse_merge!(DEFAULT_OPTS)
        Util.errf('Push status %s #%d %10s %s ... ', status.commit[0...7],
                  status.build_num, status.state, status.description) if opts[:verbose]

        url = "https://api.github.com/repos/#{@name}/statuses/#{status.commit}"
        request_data = status.filter :state, :target_url, :description, :context
        response = self.class.post(url, @options.merge(body: request_data.to_json))
        unless response.code == 201
          raise <<-EOF.strip_heredoc

            Non-201 response from GitHub:
            #{response.code} #{response.message}
            #{response.body}
          EOF
        end
        Util.errln 'done' if opts[:verbose]
        response
      end
    end
  end
end
