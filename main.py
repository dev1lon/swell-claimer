import os
import asyncio
from pathlib import Path

from utils import utils, checker
import settings


BASE_DIR = Path(__file__).resolve().parent
private_keys = utils.read_file(os.path.join(BASE_DIR, "private_keys.txt"))
proxies = utils.read_file(os.path.join(BASE_DIR, "proxies.txt"))

if settings.transfer:
    transfer_addresses = utils.read_file(os.path.join(BASE_DIR, "transfer_addresses.txt"))
    if len(private_keys) != len(transfer_addresses):
        raise Exception('Количество приватников и адресов для пересылки не совпадает!')
else:
    transfer_addresses = [None] * len(private_keys)

async def main():
    if len(private_keys) != len(proxies):
        raise Exception('Приватные ключи не соответствуют количеству прокси')
    elif len(private_keys) == 0 or len(proxies) == 0:
        raise Exception('Нет прокси и приватников')

    tasks = []
    for private_key, proxy, transfer_address in zip(private_keys, proxies, transfer_addresses):
        tasks.append(checker.checker(private_key=private_key, proxy=proxy, transfer_address=transfer_address))

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())