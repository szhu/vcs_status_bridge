module VcsStatusBridge
  module Env
    class << self
      def required_env_var(env_var)
        ENV[env_var] || (raise "environment variable #{env_var} not set")
      end

      def circleci_api_token
        required_env_var 'STATUS_BRIDGE_CIRCLECI_API_TOKEN'
      end

      def github_api_token
        required_env_var 'STATUS_BRIDGE_GITHUB_API_TOKEN'
      end

      def check_head_save_path_prefix
        ENV['STATUS_BRIDGE_CHECK_HEAD_SAVE_PATH'] || "#{ENV['HOME']}/.config/circle-github-status-bridge/check-head"
      end

      def timezone
        ENV['STATUS_BRIDGE_TIMEZONE'] || 'US/Pacific'
      end
    end
  end
end
