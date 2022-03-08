import uuid
import logging
import argparse

from discord.ext import commands
from utils.logging import setup_logging

from cogs.satellites import NFT
from assets import creds

log = logging.getLogger(__name__)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Bot to display the NFT floor price of a collection on OpenSea.")
    parser.add_argument('--discord-token',
                        '-t',
                        type=str,
                        required=False,
                        help="The token for this Discord bot.")
    parser.add_argument('--alias',
                        '-a',
                        type=str,
                        required=False,
                        help="Alias for collection to display in the Discord activity (i.e. BAYC).")
    parser.add_argument('--url',
                        '-u',
                        type=str,
                        required=False,
                        help="OpenSea API URL of any collection.")

    args = parser.parse_args()
    
    #dictionary = {opensea alias: price to trigger alert}
    alias_array = creds.alias_array

    token_to_use=creds.bot_key

    satellite = commands.Bot(command_prefix=str(uuid.uuid4()))
    satellite.add_cog(NFT(bot=satellite, alias_dict=alias_array))
    
    with setup_logging():
        satellite.run(token_to_use)
