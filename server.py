import asyncio
import os
import subprocess
import sys
from collections.abc import Callable

import update
from commons import Commands

HOST = "0.0.0.0"
PORT = 62775

cmd_fns: dict[Commands, Callable[[], None]] = {
    Commands.UPDATE: lambda: update_and_restart(),
    Commands.LOGOUT: lambda: run_cmd("shutdown /l"),
    Commands.SHUTDOWN: lambda: run_cmd("shutdown /s /t 0"),
    Commands.REBOOT: lambda: run_cmd("shutdown /r /t 0"),
    Commands.HIBERNATE: lambda: run_cmd("shutdown /h"),
}


def update_and_restart():
    update.main()
    python = sys.executable
    os.execl(python, python, *sys.argv)


def run_cmd(cmd: str):
    subprocess.run(cmd.split(" "))


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info("peername")
    client_ip = f"{addr[0]}:{addr[1]}"
    print(f"Connection with {client_ip} opened.")

    data = await reader.read()

    try:
        cmd = Commands(int.from_bytes(data))
        cmd_fn = cmd_fns[cmd]
        cmd_fn()

    except ValueError:
        print("Invalid command.")

    writer.close()
    await writer.wait_closed()
    print(f"Connection with {client_ip} closed.")


async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)

    for socket in server.sockets:
        addr = socket.getsockname()
        server_ip = f"{addr[0]}:{addr[1]}"
        print(f"Serving on {server_ip}.")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server closed.")
