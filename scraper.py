import aiohttp
import asyncio
from bs4 import BeautifulSoup
import discord_Utils as discordU
import json
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC




async def fetch_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
async def fetch_json_zephyr(session, url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Referer": "https://zephyrepic.com/shop/category/trading-card-games/pokemon/?mtp=1",
        "X-NewRelic-Id": "UAQAVVFRABAFU1RbAgcDXlM=",
        "Token": "50cH7aNwHqR&BQ3rJC7HP^j@jmq&C5Gt",  
    }

    async with session.get(url, headers=headers) as response:
        if response.status == 200:  # Check for success
            return await response.json()  # Parse JSON response
        else:
            error_text = await response.text()  # Log error details
            print(f"Failed to fetch data from {url}, Status code: {response.status}, Error: {error_text}")
            return None


#zephyr sale events
def parseZephyrSales(html_resp):
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
                with open('zephyrSaleEvents.txt', "a", encoding="utf-8") as file:
                    file.write(f"\n{link}")

async def zephyrSaleEvents():
    url = 'https://zephyrepic.com/sale-events/'
    result = await fetch_url(url)
    with open("response.html", "w", encoding="utf-8") as file:
        file.write(result)
    parseZephyrSales(result)

#zephyr all pokemon 
async def zephyrPokemon():
    counter = 0
    data = ''

    #get json file response of all products
    try:
        while (len(data) < 20):
            if counter >5:
                break
            counter += 1
            url = "https://zephyrepic.com/wp-json/zepic/get-products/"  # API endpoint
            async with aiohttp.ClientSession() as session:
                data = await fetch_json_zephyr(session, url)
    except aiohttp.ClientError as e:
            print("failed get zephyr products client error")
    except asyncio.TimeoutError:
        print("failed get zephyr products timed out.")

    await asyncio.sleep(1) 

    #filter pokemon ones only and store in pokeProduccts
    pokeProducts = []
    for dataP in data:
        if dataP['brand_slug'] == 'pokemon':
            pokeProducts.append(dataP)

    #look at our old pokeProducts
    with open('ZephyrProducts.json', "r", encoding="utf-8") as file:
        oldPokeProducts = json.load(file)


    #see if no changes since last check and leave if so
    if pokeProducts == oldPokeProducts:
        print('No changes detected')
        return
    else:
        def dict_diff(list1, list2):
            diff1 = [d for d in list1 if d not in list2]
            diff2 = [d for d in list2 if d not in list1]
            return diff1, diff2

        old, new = dict_diff(oldPokeProducts, pokeProducts)


    for item in new:  
        if item['is_in_stock'] == True:
            indexInOld = next((i for i, dic in enumerate(old) if dic.get('ID') == item['ID']), None)               

            #new product
            if indexInOld == None:
                discordU.send_discord_notification('New zephyr epic item + '+ item['name'] + '\n'+item['link'])
                
            #not new product but some change
            else:
                #check if new sale
                if item['sale_price'] != "" and old[indexInOld]['sale_price'] == "":
                    discordU.send_discord_notification('Zephyr epic item went on sale + '+ item['name'] + 'for '+ item['sale_price'] + '\n'+item['link'])
                    continue
                #if no longer on sale ignore
                if item['sale_price'] == "" and old[indexInOld]['sale_price'] != "":
                    continue

                #if price lowered for sale
                if item['sale_price'] != "" and old[indexInOld]['sale_price'] != "":
                    if round(float(item['sale_price']), 2) < round(float(old[indexInOld]['sale_price']), 2):
                        discordU.send_discord_notification('Zephyr epic item on sale reduced in price + '+ item['name'] + 'for '+ item['sale_price'] + '\n'+item['link'])
                        continue
                #price lowered non sale
                if item['regular_price'] != "" and old[indexInOld]['regular_price'] != "":
                    if round(float(item['regular_price']), 2) < round(float(old[indexInOld]['regular_price']), 2):
                        discordU.send_discord_notification('Zephyr epic item reduced in price + '+ item['name'] + 'for '+ item['regular_price'] + '\n'+item['link'])
                        continue

                #if stock change we post
                if item['is_in_stock'] and not old[indexInOld]['is_in_stock']:
                    discordU.send_discord_notification('Zephyr epic item back in stock + '+ item['name'] + '\n'+item['link'])

    #save over old listing 
    output_file = "ZephyrProducts.json"
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(pokeProducts, file, indent=4, ensure_ascii=False)

    return




async def main():
    while True:
        await asyncio.gather(
            zephyrPokemon(),
            zephyrSaleEvents(),
        )
        # Adjust the sleep time based on how frequently you want to check for updates
        await asyncio.sleep(10)  # Check every 10 seconds

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())


