import asyncio
from wakeonlan import send_magic_packet


async def wake_on_lan(mac_address: str) -> None:
    await asyncio.to_thread(send_magic_packet, mac_address)
