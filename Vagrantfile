# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/jammy64"

  # =========================================================================
  # SERVIDOR 1: BACKEND (Microservicios FastAPI + SQLite + Systemd)
  # =========================================================================
  config.vm.define "backend" do |backend|
    backend.vm.hostname = "backend-server"
    backend.vm.network "private_network", ip: "192.168.56.10"

    # Redirección de puertos opcional para depuración directa desde el Host
    backend.vm.network "forwarded_port", guest: 8001, host: 8001, auto_correct: true
    backend.vm.network "forwarded_port", guest: 8002, host: 8002, auto_correct: true
    backend.vm.network "forwarded_port", guest: 8003, host: 8003, auto_correct: true

    backend.vm.provider "virtualbox" do |vb|
      vb.name = "gestpro-backend-vm"
      vb.memory = 2048
      vb.cpus = 2
    end

    # Aprovisionamiento con Ansible Local (compatible nativamente con Windows)
    backend.vm.provision "ansible_local" do |ansible|
      ansible.playbook = "ansible/backend.yml"
    end
  end

  # =========================================================================
  # SERVIDOR 2: FRONTEND (Servidor Web Nginx + Reverse Proxy + SPA Dashboard)
  # =========================================================================
  config.vm.define "frontend" do |frontend|
    frontend.vm.hostname = "frontend-server"
    frontend.vm.network "private_network", ip: "192.168.56.20"

    # Redirección del puerto HTTP 80 al puerto 8080 en el host
    frontend.vm.network "forwarded_port", guest: 80, host: 8080, auto_correct: true

    frontend.vm.provider "virtualbox" do |vb|
      vb.name = "gestpro-frontend-vm"
      vb.memory = 1024
      vb.cpus = 1
    end

    # Aprovisionamiento con Ansible Local (compatible nativamente con Windows)
    frontend.vm.provision "ansible_local" do |ansible|
      ansible.playbook = "ansible/frontend.yml"
    end
  end
end
