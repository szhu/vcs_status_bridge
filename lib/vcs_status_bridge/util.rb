require 'active_support'

module VcsStatusBridge
  module Util
    class << self
      def Util.err(*args)
        $stderr.print(*args)
        $stderr.flush
      end

      def Util.errf(*args)
        $stderr.printf(*args)
        $stderr.flush
      end

      def Util.errln(*args)
        $stderr.puts(*args)
      end

      def format_iso_date(iso_date, timezone_name)
        require 'date'
        require 'active_support/core_ext/date_time'
        require 'active_support/core_ext/time'
        begin
          Date.iso8601(iso_date).in_time_zone(timezone_name)
              .strftime('on %h %d, %Y at %I:%M %p %Z')
        rescue ArgumentError
          return "at #{iso_date}"
        end
      end
    end
  end
end
