import asyncio
import os
import subprocess
import sys

import update
from commons import Commands

HOST = "0.0.0.0"
PORT = 62775


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

    while True:
        data = await reader.read()

        if not data:
            break

        match Commands(int.from_bytes(data)):
            case Commands.UPDATE:
                update_and_restart()

            case Commands.LOGOUT:
                run_cmd("shutdown /l")

            case Commands.SHUTDOWN:
                run_cmd("shutdown /s /t 0")

            case Commands.REBOOT:
                run_cmd("shutdown /r /t 0")

            case Commands.HIBERNATE:
                run_cmd("shutdown /h")

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
