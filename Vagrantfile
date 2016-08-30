Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.provision "shell" do |s|
    s.path = "bootstrap.sh"
  end
  config.vm.network "forwarded_port", guest: 6667, host: 6667
  config.vm.network "forwarded_port", guest: 6697, host: 6697
  config.vm.synced_folder ".", "/legobot"
  config.vm.provision "shell", inline: "/usr/sbin/ngircd -f /legobot/ngircd.conf &"
end
