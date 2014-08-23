# This file is likely a temporary solution, but hey it works for now, makes
# things easy to manage, and will report Util.errors readily.
require 'set'

# An OpenStruct-like type that requires certain keys to be defined
class StrictOpenStruct
  def self.json_create(hash_as_json)
    require 'json'
    hash = JSON.parse hash_as_json
    new hash
  end

  def initialize(hash)
    @hash = begin
      sym_hash = {}
      hash.each { |k, v| sym_hash[k.to_sym] = v }
      sym_hash
    end
    evaluate
    check_keys
  end

  def ai(options)
    require 'ap'
    ap = AwesomePrint::Inspector.new(options)
    ap.awesome @hash
  end

  def as_json
    @hash
  end

  def filter(*keys)
    @hash.select { |key, _| keys.include? key }
  end

  def to_json
    require 'json'
    @hash.to_json
  end

  def [](name)
    @hash[name.to_sym]
  end

  # def []=(name, value)
  #   @hash[name.to_sym] = value
  # end

  protected

  def evaluate; end

  private

  def check_keys
    current_keys = @hash.keys.to_set
    unless (missing = self.class.required_keys - current_keys).empty?
      raise "required keys #{missing.to_a} missing in input hash #{@hash.inspect}"
    end
    return if self.class.all_keys_allowed
    unless (extra = current_keys - self.class.registered_keys).empty?
      raise "extra keys #{extra.to_a} in input hash #{@hash.inspect}"
    end
  end

  class << self
    @all_keys_allowed = false
    attr_reader :all_keys_allowed

    def allow_all_keys
      @all_keys_allowed = true
    end

    def required_keys
      @required_keys ||= Set.new
    end

    def optional_keys
      @optional_keys ||= Set.new
    end

    def registered_keys
      required_keys.merge(optional_keys)
    end

    protected

    def require_key(*keys)
      required_keys.merge keys
      accessor_key(*keys)
    end

    def optional_key(*keys)
      optional_keys.merge keys
      accessor_key(*keys)
    end

    def accessor_key(*keys)
      reader_key(*keys)
      writer_key(*keys)
    end

    def reader_key(*keys)
      keys.each do |key|
        define_method(:"#{key}") do
          @hash[key]
        end
      end
    end

    def writer_key(*keys)
      keys.each do |key|
        define_method(:"#{key}=") do |value|
          @hash[key] =  value
        end
      end
    end
  end
end
