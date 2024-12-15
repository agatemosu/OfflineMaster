import asyncio

from commons import Commands

HOST = "127.0.0.1"
PORT = 62775


async def send(choice: int):
    try:
        _, writer = await asyncio.open_connection(HOST, PORT)

        writer.write(choice.to_bytes())
        await writer.drain()

        writer.close()
        await writer.wait_closed()

    except OSError as error:
        print(error.strerror)


async def main():
    print("Options:")
    for cmd in Commands:
        print(f"{cmd.value}: {cmd.name}")

    str_choice = input("Select an option: ")

    try:
        choice = int(str_choice)
        command = Commands(choice)
    except ValueError:
        print("Invalid option.")
        return

    print(f"Sending {command.name} to {HOST}:{PORT}.")
    await send(choice)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Aborted.")
