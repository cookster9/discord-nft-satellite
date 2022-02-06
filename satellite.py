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
    
    #args.url
 
    if args.alias == '':
        alias_to_use=creds.alias
    else:
        alias_to_use=args.alias

    if args.url == '':
        url_to_use="https://api.opensea.io/collection/"+alias_to_use
    else:
        url_to_use=args.url

    if args.discord_token == '':
        token_to_use=creds.bot_key
    else:
        token_to_use=args.discord_token
        
    alias_to_use=creds.alias
    url_to_use="https://api.opensea.io/collection/"+alias_to_use
    token_to_use=creds.bot_key

    satellite = commands.Bot(command_prefix=str(uuid.uuid4()))
    satellite.add_cog(NFT(bot=satellite, alias=alias_to_use, url=url_to_use))
    
    with setup_logging():
        satellite.run(token_to_use)
