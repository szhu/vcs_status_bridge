require 'active_support'
require 'active_support/core_ext/hash'
require 'active_support/core_ext/string/strip'
require 'httparty'
require_relative 'strict_ostruct'
require_relative 'util'

module VcsStatusBridge
  # https://circleci.com/docs/api
  module Circle
    # The status of a CircleCI build.
    class Status < StrictOpenStruct
      allow_all_keys
      require_key :build_num, :build_url, :vcs_revision, :outcome, :status, :lifecycle, :usage_queued_at

      def evaluate
        self.build_num = Integer(build_num)
      end
    end

    # A CircleCI project, which corresponds to a GitHub repo, that has statuses.
    class Project
      include HTTParty
      headers 'accept' => 'application/json'
      MAX_LIMIT = 100
      INITIALIZE_DEFAULT_OPTS = {
        use_env: true
      }
      DEFAULT_OPTS = {
        verbose: true,
        chronological: false  # default reverse-chronological
      }
      RECENT_STATUSES_DEFAULT_OPTS = {
        limit: MAX_LIMIT,
        offset: 0
      }

      def initialize(name, opts = {})
        opts.reverse_merge!(INITIALIZE_DEFAULT_OPTS)
        if opts[:use_env]
          require_relative 'env'
          opts.merge!(circle_token: Env.circleci_api_token)
        end
        raise "required param `circle_token' not given" if opts[:circle_token].nil?
        @url = "https://circleci.com/api/v1/project/#{name}"
        @query = { 'circle-token' => opts[:circle_token] }
      end

      def recent_statuses_single_request(opts = {})
        opts.reverse_merge!(DEFAULT_OPTS)
        Util.err 'Get recent Circle CI statuses... ' if opts[:verbose]

        response = self.class.get(@url, query: @query.merge(opts.slice(:limit, :offset)))
        unless response.code == 200
          raise <<-EOF.strip_heredoc

            Non-200 response from Circle CI: #{response.code} #{response.message}
            #{response.body}
          EOF
        end
        statuses = JSON.parse(response.body).map do |status_as_hash|
          Status.new status_as_hash
        end
        Util.errln "#{statuses.length} statuses received" if opts[:verbose]
        statuses.reverse! if opts[:chronological]
        statuses
      end

      # The Circle API does not allow a `limit` above MAX_LIMIT (currently 100).
      # This method allows the limit to be increased beyond that by combining
      # multiple requests.
      def recent_statuses(opts = {})
        opts.reverse_merge!(RECENT_STATUSES_DEFAULT_OPTS).reverse_merge!(DEFAULT_OPTS)
        # opts to pass to recent_statuses_single_request
        request_opts = { verbose: false }
        limit = opts[:limit].to_i
        offset = opts[:offset].to_i
        Util.err 'Get recent Circle CI statuses... ' if opts[:verbose]

        statuses = []
        while limit > 0
          Util.err "#{offset}... " if opts[:verbose]
          request_opts.merge! limit: [limit, MAX_LIMIT].min, offset: offset
          statuses.concat recent_statuses_single_request(request_opts)
          offset += MAX_LIMIT
          limit -= MAX_LIMIT
        end
        Util.errln "#{statuses.length} statuses received" if opts[:verbose]
        statuses.reverse! if opts[:chronological]
        statuses
      end

      # Get statuses in reverse chronological order until all build numbers
      # higher than `target_num` have been encountered.
      def statuses_after(target_num, opts = {})
        opts.reverse_merge!(DEFAULT_OPTS)
        target_num = Integer(target_num)
        # opts to pass to recent_statuses_single_request
        request_opts = { verbose: false, limit: MAX_LIMIT }
        offset = 0
        num = Float::INFINITY
        Util.err "Get Circle CI statuses after build ##{target_num}... " if opts[:verbose]

        statuses = []
        # Edge case example:
        # Assume we want to get all statuses after #1234 (= target_num).
        # We can stop as soon as num is #1235 (= num).
        while num > target_num + 1
          Util.err "#{offset}... " if opts[:verbose]
          request_opts.merge! offset: offset
          recent_statuses_single_request(request_opts).each do |status|
            num = status.build_num
            Util.err "##{num} " if opts[:verbose]
            break unless num > target_num
            statuses.push status
            offset += MAX_LIMIT
          end
          Util.errln if opts[:verbose]
        end
        Util.errln "#{statuses.length} statuses received" if opts[:verbose]
        statuses.reverse! if opts[:chronological]
        statuses
      end
    end
  end
end
