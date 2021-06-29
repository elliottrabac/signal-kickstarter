from http.server import BaseHTTPRequestHandler
from urllib import parse
import requests
import json
import pandas as pd
from datetime import datetime, date, timedelta
from bs4 import BeautifulSoup
import re


# utils // GET domain.com based on Kickstarter profile page
def get_websites(url):
    exclusion_websites = ["facebook", "youtube", "flickr", "twitter", "instagram", "twitch", "patreon"]

    about_page_url = url + "/about"

    try:
        response = requests.get(about_page_url)
        response.raise_for_status()
    except Exception as e:
        print(e)

    if response.status_code != 200:
        print("Error fetching page")
    else:
        soup = BeautifulSoup(response.content, 'html.parser')

    try:
        websites_title = soup.find("h5", text=re.compile("Websites"))
        websites_tags = websites_title.parent.next_sibling.next_sibling.find_all('a', href=True)

        websites = [a["href"] for a in websites_tags if not any(website in a["href"] for website in exclusion_websites)]
        return websites
    except:
        return []

#main
def fetch_kickstarter():
    has_more = True
    state = "successful"
    sort = "end_date"
    raised = 2
    page = 1
    limit = None

    completed_at = date.today() - timedelta(days=1)

    df = pd.DataFrame()

    while has_more:
        try:
            url = f"https://www.kickstarter.com/discover/advanced?state={state}&raised={raised}&sort={sort}&page={page}"

            payload={}
            headers = {
            'authority': 'www.kickstarter.com',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'x-requested-with': 'XMLHttpRequest',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            response.raise_for_status()

            if response.status_code != 200:
                print("Error fetching page")
            else:
                r = response.json()

            df_temp = pd.json_normalize(r["projects"], sep='_')

            df = df = df.append(df_temp)

            min_deadline = df["deadline"].min()
            dt_min_deadline = date.fromtimestamp(min_deadline)

            has_more = r["has_more"]
            page += 1

            if dt_min_deadline < completed_at:
                break

        except Exception as e:
            print(e)

    if limit:
        df = df[:limit]

    df["deadline_date"] = df.deadline.apply(lambda x: date.fromtimestamp(x))
    df = df[["id", "name", "blurb", "goal", "pledged", "state", "deadline", "deadline_date", "created_at", "launched_at", "backers_count", "converted_pledged_amount", "creator_id", "creator_name", "creator_urls_web_user", "location_displayable_name", "category_name", "urls_web_project", "urls_web_rewards"]]

    df = df[(df['deadline_date'] == completed_at)]

    #df["websites"] = df["creator_urls_web_user"].apply(get_websites)

    result = df.to_json(orient="records")

    print("fetch_kickstarter done")
    print(df.shape)

    return result