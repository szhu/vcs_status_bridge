require_relative 'circle_to_github'
require 'pry'

project = ::VcsStatusBridge::CircleToGithub.new('IFTTT/ifttt_front_end')
project.save_check_head 10486
puts project.load_check_head
project.push_statuses_after_check_head

# binding.pry
