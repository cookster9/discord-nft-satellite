import aiohttp
import asyncio
import logging

from typing import Union
from models.opensea import FloorPrice
from discord.ext import commands, tasks
from discord import Activity, ActivityType
from assets import creds


log = logging.getLogger(__name__)


async def get_opensea_floor_price(alias: str) -> Union[FloorPrice, bool]:

    """Queries the API endpoint of an NFT collection on OpenSea and parses the response to retrieve the floor price.

    .. note:
        API endpoint of a collection, e.g. https://api.opensea.io/collection/boredapeyachtclub
    .. todo:
        Check the base currency of the floor price returned is always in ETH.

    :param url: str
        URL of the collection to call.
    :param alias: str
        Name of the collection, i.e. BAYC.
    :returns:
        NFTPrice object if successful, otherwise False.
    """

    source = "OpenSea"
    url="https://api.opensea.io/collection/"+alias

    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            async with session.get(url) as response:
                content = await response.json()
                if content:
                    price = content['collection']['stats']['floor_price']
                    one_day_sales = content['collection']['stats']['one_day_sales']
                    return FloorPrice(source=source, price=f"{price}", project=alias, one_day_sales=f"{one_day_sales}")
    except Exception as error:
        log.error(f"[ENDPOINT] [{source}] API response was invalid {error}.")
        return False
    if content:
        log.error(f"[ENDPOINT] [{source}] API request did not return the expected response: {content}.")
    else:
        log.error(f"[ENDPOINT] [{source}] API request did not return the expected response.")
    return False


class NFT(commands.Cog):

    """Discord satellite that displays OpenSea NFT floor prices as a user in Discord servers.
     ___________________________________
    |                                  |
    |  35.5 ETH                        |
    |  Watching BAYC floor price on .. |
    |__________________________________|
    """

    def __init__(self,
                 bot: commands.Bot,
                 alias_dict: dict):

        self.bot = bot
        self.bot_type = self.__class__.__name__

        self.alias_dict = alias_dict
        
        self.channel_id=creds.nft_pings

        self.price = {}
        self.status = "floor prices"
        self.member_of_guilds = None
        self.one_day_sales = {}

        self.updater.start()

    async def update_interface_elements(self, guild_id: int) -> None:

        """Updates the nickname for this bot within a given discord server (guild_id).

        :param guild_id:
            `guild_id` to perform update.
        """

        guild = self.bot.get_guild(guild_id)
        bot_instance = guild.me
        nickname_override = 'mousebot'
        #await bot_instance.edit(nick=nickname_override)

        #log.info(f"[UPDATE] [{self.bot_type}] - [{guild}] - [{self.alias}] Nickname: {nickname_override} Activity: {self.status}")

    async def update_nft_floor_price(self, alias: str) -> bool:

        """Fetches latest NFT price from sources to update the price and status attributes.

        :returns: bool
            True if successful else False
        """

        nft_floor_price = await get_opensea_floor_price(alias=alias)

        if nft_floor_price:
            self.price[alias] = f"{nft_floor_price.price}"
            #self.status[alias] = f"{nft_floor_price.project} floor price on {nft_floor_price.source}"
            self.one_day_sales[alias] = f"{nft_floor_price.one_day_sales}"

            return True
        return False
    
    async def send_message(self, message: str) -> None:        
        channel = self.bot.get_channel(self.channel_id)
        await channel.send(message)

    @tasks.loop(minutes=10)
    async def updater(self):

        """Task to fetch new data and update the bots nickname and activity in Discord.

        .. note:

            Discord nicknames and roles are local to the server, whereas an activity is universal across all servers.

            `nickname` is updated by creating an self.update_interface_elements(guild_id) task for all servers this bot
                is a member of.
                UI: '35.5 ETH'
            `activity` is updated with self.bot.change_presence()
                UI: 'Watching BAYC floor price on OpenSea'
        """

        #pinged_today=False        

        self.member_of_guilds = [guild.id for guild in self.bot.guilds]
        await self.send_message(f":rocket: :rocket: :rocket: :rocket: :rocket: :rocket: :rocket: :rocket: :rocket: :rocket:")
        for key in self.alias_dict:
            valid_response = await self.update_nft_floor_price(key)

            if valid_response:
                await self.send_message(f"Floor price of {key}: {self.price[key]}")
                if float(self.price[key]) > float(self.alias_dict[key]):
                    await self.send_message(f"@here")
                await self.bot.change_presence(activity=Activity(type=ActivityType.watching, name=self.status))
                update_jobs = [self.update_interface_elements(guild_id) for guild_id in self.member_of_guilds]
                await asyncio.gather(*update_jobs)

    @updater.before_loop
    async def before_update(self):

        """Ensure this bot is initialized before updating its nickname or status."""

        await self.bot.wait_until_ready()
        self.member_of_guilds = [guild.id for guild in self.bot.guilds]

        log.info(f"[INIT] [{self.bot_type}] - Bot started successfully, active on {len(self.member_of_guilds)} servers.")

    def __str__(self):
        return f"Discord NFT satellite for {self.alias}"

    def __repr__(self):
        return f"<Discord NFT satellite for {self.alias}>"
