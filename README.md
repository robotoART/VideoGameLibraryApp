# Video Game Library
by robotoART

### Objective of this sample application
Using a basic sample Item Catalog project from Udacity's GitHub pages learn the fundamentals of the Backend to a Web application. Discover how to setup a Python database, a Flask framework, JSON endpoints, OAuth authorization, using CRUD, Agile and iterative principles.

**Udacity's sample project:** The example project used as a guide for my Video Game Library Application example can be found at: https://github.com/udacity/OAuth2.0

# Requirements to Run Application
## Install the Vagrant VM
### Git

If you don't already have Git installed, [download Git from git-scm.com.](http://git-scm.com/downloads) Install the version for your operating system.

On Windows, Git will provide you with a Unix-style terminal and shell (Git Bash).  
(On Mac or Linux systems you can use the regular terminal program.)

You will need Git to install the configuration for the VM.

### VirtualBox

VirtualBox is the software that actually runs the VM. [You can download it from virtualbox.org, here.](https://www.virtualbox.org/wiki/Downloads)  Install the *platform package* for your operating system.  You do not need the extension pack or the SDK. You do not need to launch VirtualBox after installing it.

**Ubuntu 14.04 Note:** If you are running Ubuntu 14.04, install VirtualBox using the Ubuntu Software Center, not the virtualbox.org web site. Due to a [reported bug](http://ubuntuforums.org/showthread.php?t=2227131), installing VirtualBox from the site may uninstall other software you need.

### Vagrant

Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem.  [You can download it from vagrantup.com.](https://www.vagrantup.com/downloads) Install the version for your operating system.

**Windows Note:** The Installer may ask you to grant network permissions to Vagrant or make a firewall exception. Be sure to allow this.

## Fetch the Source Code and VM Configuration

**Windows:** Use the Git Bash program (installed with Git) to get a Unix-style terminal.  
**Other systems:** Use your favorite terminal program.

Using the terminal, change directory to wherever you want the project to reside.

From the terminal, run:

    git clone https://github.com/robotART/Video-Game-Library-App

This will give you a directory named **vagrant** complete with the source code for the flask application, a vagrantfile, and a bootstrap.sh file for installing all of the necessary tools.

## Run the virtual machine!

Using the terminal, change directory to vagrant (**cd /vagrant**), then type **vagrant up** to launch your virtual machine.


## Running the Video Library App
Once it is up and running, type **vagrant ssh**. This will log your terminal into the virtual machine, and you'll get a Linux shell prompt. When you want to log out, type **exit** at the shell prompt.  To turn the virtual machine off (without deleting anything), type **vagrant halt**. If you do this, you'll need to run **vagrant up** again before you can log into it.


Now that you have Vagrant up and running type **vagrant ssh** to log into your VM.  change to the /vagrant directory by typing **cd /vagrant/catalog**. This will take you to the shared folder between your virtual machine and host machine.

Type **ls** to ensure that you are inside the directory that contains project.py, database_setup.py, and two directories named 'templates' and 'static'

Type **python application.py** to run the Flask web server. In your browser visit **http://localhost:5000** to view the restaurant menu app.  You should be able to view, add, edit, and delete menu items and restaurants.

To stop running the local Flask web server switch to your terminal and hit the "control+C" keys.

To log out of the VM after stopping the Flask web server, type:

    exit

Now you can shutdown/(turn off) the virtual machine safely.

#### Starting with an empty database
If you want to start with a fresh empty database, you will have to delete the database file named **"videogamelibrary.db"** found in **/vagrant/catalog** folder.

Then type and run **python database_setup.py** to create the empty database named **"videogamelibrary.db"**.

If you ever want to use the sample database items, just run the **sampleitems.py** file while in **/vagrant/catalog** folder.
