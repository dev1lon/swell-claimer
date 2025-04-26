import asyncio
import aiohttp
from web3 import AsyncWeb3
from aiohttp import ContentTypeError, ClientHttpProxyError
from aiohttp_proxy import ProxyConnector
from fake_useragent import UserAgent
from web3.exceptions import Web3Exception

from utils import logger, semaphore, abi
import settings


logger = logger.get_logger()


async def checker(private_key, proxy, transfer_address):
    async with semaphore.semaphore:

        w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(
            endpoint_uri='https://rpc.ankr.com/swell',
            request_kwargs={'proxy': f'http://{proxy}'}
        ))
        account = w3.eth.account.from_key(private_key)


        headers = {'user-agent': UserAgent().random}
        params = {
            'user': account.address,
            'chainIds': '1923',
        }

        connector = ProxyConnector.from_url(f'http://{proxy}')

        for i in range(0,3):
            try:
                async with aiohttp.ClientSession(connector=connector) as session:
                    async with session.get(url='https://api.merkl.xyz/v3/rewards', headers=headers, params=params) as response:
                        data = await response.json()
                        if data == {}:
                            logger.success(f"{account.address} | Not eligible")
                            return
                        logger.success(f"{account.address} | Eligible | {int(data['1923']['campaignData']['0x8e3bc463fbc3479a2703a240e69cd12ff4724af0caa9be787cfb4c7b2a0de4b5']['Swellchain King Claim']['accumulated']) / 10 ** 18}")
                        proof = data['1923']['tokenData']['0x2826D136F5630adA89C1678b64A61620Aab77Aea']['proof']
                        break
            except ClientHttpProxyError:
                logger.error(f'{account.address} | Proxy not working')
                return
            except ContentTypeError:
                logger.warning(f'{account.address} | Failed request. Retry')
                await asyncio.sleep(15)
            logger.error(f'{account.address} | Failed request. Attempts finished')

        if settings.claimer:
            logger.info(f'{account.address} | Start claim')
            contract = w3.eth.contract(
                address=AsyncWeb3.to_checksum_address('0x918261fa5Dd9C3b1358cA911792E9bDF3c5CCa35'),
                abi=abi.ABI
            )

            args = [
                [account.address],
                [AsyncWeb3.to_checksum_address('0x2826D136F5630adA89C1678b64A61620Aab77Aea')],
                [1000000000000000000000],
                [proof]
            ]

            tx_params = {
                'chainId': await w3.eth.chain_id,
                'nonce': await w3.eth.get_transaction_count(account.address),
                'from': AsyncWeb3.to_checksum_address(account.address),
                'to': AsyncWeb3.to_checksum_address('0x3Ef3D8bA38EBe18DB133cEc108f4D14CE00Dd9Ae'),
                'gasPrice': int(await w3.eth.gas_price),
                'data': contract.encodeABI('claim', args=args),
            }

            gas = await w3.eth.estimate_gas(tx_params)
            tx_params['gas'] = int(gas)

            tx_hash = None
            try:
                sign = w3.eth.account.sign_transaction(tx_params, private_key)
                tx_hash = await w3.eth.send_raw_transaction(sign.rawTransaction)
            except Exception as error:
                logger.warning(f'{account.address} | {error}')

            if tx_hash:
                try:
                    data = await w3.eth.wait_for_transaction_receipt(tx_hash, timeout=200)
                    if data.get('status') == 1:
                        logger.success(f'{account.address} | tx_hash - {tx_hash.hex()} | Success claim')
                    else:
                        raise Web3Exception(f'transaction failed {data["transactionHash"].hex()}')
                except Exception as err:
                    logger.error(f'{account.address} | Claim failed. Error - {err}')

        if settings.claimer and settings.transfer:
            logger.debug(f'Сон 15 секунд между клэймом и трансфером')
            await asyncio.sleep(15)

        if settings.transfer:
            logger.info(f'{account.address} | Start transfer')
            token_contract = w3.eth.contract(
                address=AsyncWeb3.to_checksum_address('0x2826D136F5630adA89C1678b64A61620Aab77Aea'),
                abi=abi.TokenABI
            )
            balance = await token_contract.functions.balanceOf(account.address).call()
            if balance == 0:
                logger.warning(f'{account.address} | На кошельке нет токенов')
                return

            args = [
                transfer_address,
                balance
            ]

            tx_params = {
                'chainId': await w3.eth.chain_id,
                'nonce': await w3.eth.get_transaction_count(account.address),
                'from': AsyncWeb3.to_checksum_address(account.address),
                'to': AsyncWeb3.to_checksum_address('0x2826D136F5630adA89C1678b64A61620Aab77Aea'),
                'data':token_contract.encodeABI('transfer',args=args),
                'gasPrice': int(await w3.eth.gas_price),
            }

            gas = await w3.eth.estimate_gas(tx_params)
            tx_params['gas'] = int(gas)

            tx_hash = None
            try:
                sign = w3.eth.account.sign_transaction(tx_params, private_key)
                tx_hash = await w3.eth.send_raw_transaction(sign.rawTransaction)
            except Exception as error:
                logger.warning(f'{account.address} | {error}')

            if tx_hash:
                try:
                    data = await w3.eth.wait_for_transaction_receipt(tx_hash, timeout=200)
                    if data.get('status') == 1:
                        logger.success(f'{account.address} | tx_hash - {tx_hash.hex()} | Success transfer to {transfer_address}')
                    else:
                        raise Web3Exception(f'transaction failed {data["transactionHash"].hex()}')
                except Exception as err:
                    logger.error(f'{account.address} | Claim failed. Error - {err}')