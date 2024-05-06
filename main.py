from bs4 import BeautifulSoup
import pandas
import requests
import csv
import time

# Get user input
print("Please provide OTS Link to scrape (e.g. '/pressemappe/199/spoe-parlamentsklub')")
nextPage = input("> ")

print("Please provide the output filename (e.g. 'spoe_aussendungen.csv')")
fileName = input("> ")

print("Please provide the number of pages to be scraped (e.g. '667')")
try:
    numberOfPagesToScrape = int(input("> "))
except ValueError:
    print('\033[93mError: Please enter a number\033[0m')
    exit()

timeNeeded = float(numberOfPagesToScrape) * (17.37 + 3)
timeFormat = "seconds"

# Convert to appropriate format
if (timeNeeded > 60):
    timeNeeded = timeNeeded / 60
    timeFormat = "minutes"

if (timeNeeded > 60):
    timeNeeded = timeNeeded / 60
    timeFormat = "hours"

print(f"This operation will take approximately {round(timeNeeded, 2)} {timeFormat}. Continue? (Y/N)")
continueInput = input("> ")

if continueInput != "Y" and continueInput != "y":
    exit()

tracked_times = []

# Create csv
file = open(fileName, "w")
# Always use quotes to separate entries (, between "" don't count as a new csv item)
writer = csv.writer(file, quoting=csv.QUOTE_ALL)

# Create first row of csv
writer.writerow(["TITEL", "UNTERTITEL", "INHALT", "DATUM", "HERAUSGEBER"])

for i in range(numberOfPagesToScrape):
    # Track how long the scraping of one page takes to provide accurate Time Remaining Feedback
    start_time = time.time()

    # Get content of provided URL and check if URL is valid
    try:
        html_text = requests.get(f'https://www.ots.at{nextPage}')
        html_text.encoding = 'UTF-8'
        html_text = html_text.text
    except requests.exceptions.RequestException as error:  # This is the correct syntax
        print("\033[93mError establishing a connection. Please check if the provided URL is valid.\033[0m More information:")
        raise SystemExit(error)

    soup = BeautifulSoup(html_text, 'lxml')

    cards = soup.find_all('div', class_ = 'aussendung')

    for card in cards:
        details = card.find('div', class_ = 'aussendung-content')
        title = details.find('h3', class_ = 'aussendung-title')
        link = title.find('a')['href']
        
        subpage = requests.get(f'https://www.ots.at{link}')
        subpage.encoding = 'UTF-8'
        subpage = subpage.text
        subSoup = BeautifulSoup(subpage, 'lxml')

        articleTitle = subSoup.find('h1', {"itemprop" : "headline"}).text
        
        articleCaption = subSoup.find('h2', class_ = 'untertitel')

        # Sometimes there are articles without captions
        if articleCaption:
            articleCaption = articleCaption.text
            articleCaption = articleCaption.strip()

        articleText = subSoup.find_all('p', class_ = 'text')
        fullText = ''
        publisher = ''

        length = len(articleText)

        for index, paragraph in enumerate(articleText):
            if index == length - 1:
                if len(paragraph.text.split('\n')) > 0:
                    publisher = paragraph.text.split('\n')[0]
            else:
                fullText += " " + paragraph.text.strip()

        dateContainer = subSoup.find('div', class_ = 'meta-top')
        date = dateContainer.find('div', class_ = "volltextDetails").text

        # Remove newlines and blank spaces
        articleTitle = articleTitle.strip()
        if articleCaption:
            articleCaption = articleCaption.strip()
        fullText = fullText.strip()
        date = date.strip()
        publisher = publisher.strip()

        writer.writerow([articleTitle, articleCaption, fullText, date, publisher])
        
        print(f"Added {articleTitle}")

    # Get next page
    nextPage = soup.find('a', class_ = 'next-results')

    # No next page available
    if not nextPage:
        print("\033[93mThere are no more pages available to scrape. The program will now terminate\033[0m")
        break
    else:
        nextPage = nextPage['href']

    print("Waiting for 3 seconds", end='', flush=True)
    time.sleep(1)
    print(".", end='', flush=True)
    time.sleep(1)
    print(".", end='', flush=True)
    time.sleep(1)
    print(".", end='', flush=True)

    # Track how long the scraping of one page took to provide accurate Time Remaining Feedback
    end_time = time.time()

    time_delta = round(end_time - start_time, 2)
    tracked_times.append(time_delta)

    totalTime = 0
    for tracked_time in tracked_times:
        totalTime += tracked_time

    averageTime = totalTime / len(tracked_times)
    timeNeeded = averageTime * (numberOfPagesToScrape - (i + 1))

    # Convert to appropriate format
    timeFormat = "seconds"

    if (timeNeeded > 60):
        timeNeeded = timeNeeded / 60
        timeFormat = "minutes"

    if (timeNeeded > 60):
        timeNeeded = timeNeeded / 60
        timeFormat = "hours"

    print(f" | {i+1} / {numberOfPagesToScrape} | {round(timeNeeded, 2)} {timeFormat} remaining", flush=True)

file.close()

# Remove all new lines from csv
file = pandas.read_csv(fileName)

for col in file:
    file[col] = file[col].replace("\n", " ", regex = True).replace("\r", " ", regex = True)

file.to_csv(fileName, index = False, quoting=csv.QUOTE_ALL)