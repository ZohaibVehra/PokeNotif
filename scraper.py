import aiohttp
import asyncio
from bs4 import BeautifulSoup
import discord_Utils as discordU


async def fetch_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()


def parseZephyrSales(html_resp):

    #read prior event links
    with open("zephyrSaleEvents.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()
    links = [line.strip() for line in lines]

    soup = BeautifulSoup(html_resp, 'html.parser')   
    outer_grid = soup.select_one("html > body > div:nth-of-type(1) > main > article > section > div > div")
    if outer_grid:
        child_elements = outer_grid.find_all('div', class_='grid__item one-whole sm-one-half md-one-third')       
        
    for child in child_elements:
        firstLayer = child.find_all(True)
        first_element = firstLayer[0]

        if first_element.name == 'a' and first_element.has_attr('href'):
            link = first_element['href'] 
            if link not in links:
                discordU.send_discord_notification('New Zephyr Sale Event \n'+link)



        

async def zephyrSaleEvents():
    url = 'https://zephyrepic.com/sale-events/'
    result = await fetch_url(url)
    with open("response.html", "w", encoding="utf-8") as file:
        file.write(result)
    parseZephyrSales(result)



async def main():
    await zephyrSaleEvents()

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())