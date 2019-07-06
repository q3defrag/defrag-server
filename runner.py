# -*- coding: utf-8 -*-
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from collections.abc import Mapping



REQUIRED_SOFTWARE = ['unionfs-fuse']
QUAKE_CFG_FORMAT = 'seta "{}" "{}"\n'

def dict_merge(dct, merge_dct, add_keys=True):
    dct = dct.copy()
    if not add_keys:
        merge_dct = {
            k: merge_dct[k]
            for k in set(dct).intersection(set(merge_dct))
        }

    for k, v in merge_dct.items():
        if isinstance(dct.get(k), dict) and isinstance(v, Mapping):
            dct[k] = dict_merge(dct[k], v, add_keys=add_keys)
        else:
            dct[k] = v

    return dct

def write_config(config, path):
    # outputting the config
    config_file_dirname = os.path.dirname(path)

    if not os.path.exists(config_file_dirname):
        print("config file does not exist... creating")
        os.makedirs(config_file_dirname)

    print("writing config {}".format(path))

    with open(path, 'w') as outputConfig:
        outputConfig.write('// ######################################\n'
                           '// # This config file is auto generated #\n'
                           '// # Edit the JSON config file instead  #\n'
                           '// ######################################\n')
        outputConfig.write('echo loading config: {}\n'.format(path))

        # Write the settings to config file
        for key, value in config['config'].items():
            outputConfig.write(QUAKE_CFG_FORMAT.format(key, value))

        # Write the map to the config, this command doesn't use 'seta'
        # So we just write it directly at the end
        outputConfig.write('map {}'.format(config['map']))


def generate_config(server_name, config):
    server_config = dict()
    server_data = config['servers'][server_name]

    # Apply the templates
    if 'templates' in server_data:
        for template_name in server_data['templates']:
            server_config = dict_merge(server_config, config['templates'][template_name])

    # Apply the server config
    server_config = dict_merge(server_config, server_data)

    # Register self as idle config unless specified otherwise
    if 'df_sv_script_idleCfg' not in server_config['config']:
        server_config['config']['df_sv_script_idleCfg'] = 'cfgs/{}.cfg'.format(server_name)

    # Write the modules to the config
    server_config['config']['rs_modules'] = ' '.join(server_config['modules'])

    return server_config

def prepare_filesystem(root, server_name):
    mountpoint = '{}/servers/mount/{}'.format(root, server_name)

    # Make sure we're not already mounted
    if os.path.ismount(mountpoint):
        print("Filesystem already mounted... proceeding".format(mountpoint))
    else:
        # Create the mountpoint if it doesn't exist
        if not os.path.exists(mountpoint):
            os.mkdir(mountpoint)

        # Make sure the mountpoint is directory
        if not os.path.isdir(mountpoint):
            print("The file {} is not a directory".format(mountpoint))
            return 1


        # Make sure directory is empty
        if os.listdir(mountpoint):
            print("The directory {} is not empty".format(mountpoint))
            return 1


        #TODO Currently all artifacts are written to defrag-maps directory
        #     This is caused by the RW designation on that directory.

        # Mount the filesystem
        try:
            subprocess.run(['sudo', 'unionfs-fuse', *[
                '-o', 'cow,max_files=32768',
                '-o', 'allow_other',
                '{0}/servers/conf/{1}/=RO:'
                '{0}/proxymod-base=RO:'
                '{0}/defrag-base=RO:'
                '{0}/quake3-base=RO:'
                '{0}/defrag-maps=RW'.format(root, server_name),
                mountpoint
            ]], check=True)
            print("Successfully mounted filesystem {}".format(mountpoint))

        except subprocess.CalledProcessError:
            print("Unable to mount the filesystem to {}".format(mountpoint))
            return 1

def process_arguments(argv):
    parser = argparse.ArgumentParser(description="DeFRaG server runner")

    parser.add_argument('-c', '--config',
        metavar='CONFIG_FILE',
        dest='config',
        required=True,
        help="The JSON config file")

    parser.add_argument('-s', '--servers',
        metavar='SERVER_NAMES',
        dest='servers',
        required=True,
        nargs="+",
        help="The servers that you want to run, separated by spaces")

    return parser.parse_args(argv[1:])


def main(argv):
    args = process_arguments(argv)

    # Check the required software, stop if there are any missing
    for s in REQUIRED_SOFTWARE:
        if shutil.which(s) is None:
            print("{} is required for this script to run, please install it.".format(s))
            return 127

    # Load the JSON config file
    with open(args.config) as input_file:
        config = json.load(input_file)

    # Store all the server configs
    configs = {}
    for server_name in args.servers:
        configs[server_name] = generate_config(server_name, config)

        # Write the config to disk, this is loaded by the q3 server
        config_path = '{0}/servers/conf/{1}/defrag/cfgs/{1}.cfg'.format(config['root'], server_name)
        write_config(configs[server_name], config_path)

        prepare_filesystem(config['root'], server_name)


        q3directory = '{}/servers/mount/{}'.format(config['root'], server_name)
        q3binary = '{}/{}'.format(q3directory, config['engine'])

        # Delete the old q3config output
        q3config_server_path = '{}/defrag/q3config_server.cfg'.format(q3directory)
        if os.path.exists(q3config_server_path):
            os.remove(q3config_server_path)

    # The filesystem is set up for us, start quake & keep it running
    while True:
        try:
            sessions = subprocess.check_output(['tmux', 'ls']).decode('utf-8').splitlines()
            sessions = [x.split(':')[0] for x in sessions]
            down = list(set(sessions) - set(args.servers))
        except subprocess.CalledProcessError:
            print("No tmux sessions found")
            down = args.servers

        for server_name in down:
            # If someone on the system starts tmux we don't want to crash this process
            if server_name not in configs:
                continue

            q3args = [
                '+set fs_homepath {}/servers/mount/{}'.format(config['root'], server_name),
                '+set net_ip {}'.format(configs[server_name]['config']['net_ip']),
                '+set net_enabled {}'.format(configs[server_name]['config']['net_enabled']),
                '+set net_port {}'.format(configs[server_name]['port']),
                '+set rs_server_id {}'.format(configs[server_name]['rs_server_id']),
                '+set com_hunkmegs {}'.format(configs[server_name]['config']['com_hunkmegs']),
                '+set com_protocol {}'.format(configs[server_name]['config']['com_protocol']),
                '+set sv_pure {}'.format(configs[server_name]['config']['sv_pure']),
                '+set fs_game defrag',
                '+set dedicated 2',
                '+set vm_game 2',
                '+set ttycon_ansicolor 1',
                '+set bot_enable 0',
                '+exec cfgs/{}.cfg'.format(server_name)
            ]

            if 'net_ip6' in configs[server_name]['config']:
                q3args.append('+set net_ip6 {}'.format(configs[server_name]['config']['net_ip6']))

            
            print("Starting server '{}'".format(server_name))
            # Run the q3e dedicated server in tmux so we can
            # freely attach and detatch from this session
            subprocess.run(['tmux', 'new', '-d', '-s', server_name,
                            "{} {}".format(q3binary, ' '.join(q3args))],
                            cwd=q3directory,
                            shell=False)

        # Take a 5 second nap before we try to start the servers again
        time.sleep(5)

if __name__ == '__main__':
    sys.exit(main(sys.argv))

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
