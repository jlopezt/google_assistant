import subprocess

def pc_query(custom_data):
    p = subprocess.run(["ping", "-c", "1", "10.68.2.11"], stdout=subprocess.PIPE)
    state = p.returncode == 0
    return {"on": state, "online": True}

def pc_action(custom_data, command, params):
    if command == "action.devices.commands.OnOff":
        if params['on']:
            #subprocess.run(["wakeonlan", "-i", "10.68.2.255", "00:11:22:33:44:55"])
            subprocess.run(["ls", "-ltr"])
        else:
            #subprocess.run(["sh", "-c", "echo shutdown -h | ssh clust@10.68.2.11"])
            subprocess.run(["ls", "-ltr"])
        return {"status": "SUCCESS", "states": {"on": params['on'], "online": True}}
    else:
        return {"status": "ERROR"}
