# defrag-server
A collection of scripts and tools for running a defrag server, these were built for ubuntu 16.04 i386, but likely will work on other versions


## How to use
First customize the `config.json` file, then:

 * `./install.sh`
 * Needs customization~ `cp interfaces /etc/network/interfaces`
 * Needs customization~ `cp df_servers.service /etc/systemd/system/`
 * `cp df_maps.service /etc/systemd/system/`
 * `systemctl enable df_servers.service`
 * `systemctl enable df_maps.service`
 * copy `pak0.pk3` through `pak8.pk3` to `quake3-base/baseq3`
 * copy `qagamei386.so` to `proxymod-base/defrag`
 * copy `mysqlconnection.info` to `proxymod-base/defrag`
 * copy entire modules directory to `proxymod-base/defrag`
 * copy any maps you have to `defrag-maps/defrag`
 * Download a copy of [ipv4db.dat](edawn-mod.org/binaries/ip4db.dat)
 * copy `ipv4db.dat` to `quake3-base/` (for `/locations` to function)
 * restart the server and everything should be up and running
 * modify `latest_map` to be the latest map you hae downloaded



## How to attach to a server console
Since I'm using tmux you can type `tmux attach -t <server_name>` to attach to a servers console

for example `tmux attach -t mixed-1`

all tmux sessions can be viewed with `tmux ls`
```
root@eggplant:~# tmux ls
beta: 1 windows (created Mon Jul  8 21:54:27 2019) [80x23]
fastcaps-1: 1 windows (created Mon Jul  8 21:54:27 2019) [80x23]
mixed-1: 1 windows (created Mon Jul  8 21:54:27 2019) [134x37]
teamrun-1: 1 windows (created Mon Jul  8 21:54:27 2019) [80x23]
```

to detach do `ctrl + b` then press `d`

to scroll do `ctrl + b` then `page up`


## TODO

 * `install.sh` should be using `-j $(nproc)` when compiling
 * config regeneration should happen on a single server restart (on crash too?)
 * separate other runtime artifacts (like logs) from maps directory
 * separate maps directory per server
 * strip out everything from pk3 except for bsp to save space
