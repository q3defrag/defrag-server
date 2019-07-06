# defrag-server
A collection of scripts and tools for running a defrag server, these were built for ubuntu 16.04 i386, but likely will work on other versions


## How to use
First customize the `config.json` file, then:

 * `./install.sh`
 * Needs customization~ `cp interfaces /etc/network/interfaces`
 * Needs customization~ `cp df_servers.service /etc/systemd/system/`
 * `systemctl enable df_servers.service`
 * copy `pak0.pk3` through `pak8.pk3` to `quake3-base/baseq3`
 * copy `qagamei386.so` to `proxymod-base/defrag`
 * copy `mysqlconnection.info` to `proxymod-base/defrag`
 * copy any maps you have to `defrag-maps/defrag`
 * restart the server and everything should be up and running



## How to attach to a server console
Since I'm using tmux you can type `tmux attach -t <server_name>` to attach to a servers console

for example `tmux attach -t mixed-1`

all tmux sessions can be viewed with `tmux ls`

to detach do `ctrl + b` then press `d`

to scroll do `ctrl + b` then `page up`
