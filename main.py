from bs4 import BeautifulSoup
import pandas
import urllib.parse
import requests
import csv
import time  

class Article:
    def __init__(self, title, subtitle, content, dateTime, publisher):
        self.title = title
        self.subtitle = subtitle
        self.content = content
        self.dateTime = dateTime
        self.publisher = publisher


def removeNewLines():
    # Remove all new lines from csv
    file = pandas.read_csv(fileName)

    for col in file:
        file[col] = file[col].replace("\n", " ", regex = True).replace("\r", " ", regex = True)

    file.to_csv(fileName, index = False, quoting=csv.QUOTE_ALL)


def getScrapeURL():
    # Get URL to scrape
    print("Please provide OTS Link to scrape (e.g. '/pressemappe/199/spoe-parlamentsklub')")
    nextPage = input("> ")
    
    if not urllib.parse.urlsplit(nextPage).query:
        return urllib.parse.urlparse(nextPage).path
    else:
        return urllib.parse.urlsplit(nextPage).path + "?" + urllib.parse.urlsplit(nextPage).query


def getCSVFileName():
    # Get filename of the csv to be saved
    print("Please provide the output filename (e.g. 'spoe_aussendungen.csv')")
    fileName = input("> ")
    return fileName


def getNumberOfPagesToScrape():
    # Loop until correct user input was given
    numberOfPagesToScrape = 0
    while (numberOfPagesToScrape < 1):
        print("Please provide the number of pages to be scraped (e.g. '25')")
        try:
            numberOfPagesToScrape = int(input("> "))
        except ValueError:
            print('\033[93mError: Please enter a number\033[0m')
            numberOfPagesToScrape = 0

    return numberOfPagesToScrape


def createSoupObjectForURL(URL):
    # Get content of provided URL and check if URL is valid
    try:
        html_text = requests.get(f'https://www.ots.at{URL}')
        html_text.encoding = 'UTF-8'
        html_text = html_text.text
    except requests.exceptions.RequestException as error:
        print("\033[93mError establishing a connection. Please make sure that the provided URL is valid and that you're connected to the internet.\033[0m Debug information:")
        raise SystemExit(error)

    return BeautifulSoup(html_text, 'lxml')


def convertSecondsToAppropriateFormat(duration):
    # Convert seconds to best suited time format
    timeFormat = "seconds"
    
    if (duration > 60):
        duration = duration / 60
        timeFormat = "minutes"

    if (duration > 60):
        duration = duration / 60
        timeFormat = "hours"

    return [round(duration, 2), timeFormat]


def scrapePage(soup, writer, writeToCSV):
    cards = soup.find_all('div', class_ = 'aussendung')

    for card in cards:
        cardContent = card.find('div', class_ = 'aussendung-content')
        title = cardContent.find('h3', class_ = 'aussendung-title')
        link = title.find('a')['href']
        
        subSoup = createSoupObjectForURL(link)
        article = scrapeOneCard(subSoup)

        if writeToCSV:
            # Write to csv
            writer.writerow([article.title, article.subtitle, article.content, article.dateTime, article.publisher])
            print(f"Added {article.title}")


def scrapeOneCard(soup):
    articleTitle = soup.find('h1', {"itemprop" : "headline"}).text.strip()
    
    articleCaption = soup.find('h2', class_ = 'untertitel')

    # Sometimes there are articles without captions
    if articleCaption:
        articleCaption = articleCaption.text.strip()

    # Get content of the article
    # The article content and the publisher are not distinguishable via HTMl Tags -> The last <p class="text"> is the contact information
    articleText = soup.find_all('p', class_ = 'text')

    fullText = "" # Declare fullText (if the content of the article is empty fullText is never declared and an error is thrown in the return line)
    numberOfParagraphs = len(articleText)

    if numberOfParagraphs > 0:
        for index, paragraph in enumerate(articleText):
            # The last <p class="text"> is the contact information
            if (index == numberOfParagraphs - 1):
                if len(paragraph.text.split('\n')) > 0:
                    publisher = paragraph.text.split('\n')[0].strip()
            else: # every other <p class="text"> is part of the article
                if (index == 0):
                    fullText = paragraph.text.strip()
                else:
                    fullText += " " + paragraph.text.strip()

    dateContainer = soup.find('div', class_ = 'meta-top')
    date = dateContainer.find('div', class_ = "volltextDetails").text.strip()

    return Article(articleTitle, articleCaption, fullText, date, publisher)


def buffer(numberOfSeconds):
    print(f"Buffering for {numberOfSeconds} seconds", end='', flush=True)
    
    for i in range(numberOfSeconds):
        time.sleep(1)
        print(".", end='', flush=True)


def calculateTimeDelta(start_time, end_time):
    return round(end_time - start_time, 2)


def calculateRemainingTime(tracked_times, numberOfPagesToScrape):
    totalTime = 0
    for tracked_time in tracked_times:
        totalTime += tracked_time

    averageTime = totalTime / len(tracked_times)
    return averageTime * (numberOfPagesToScrape - (i + 1))


def estimateRuntime(URL, numberOfPagesToScrape):
    # Scrape one page to determine the expected runtime
    soup = createSoupObjectForURL(URL)
    start_time = time.time()
    scrapePage(soup, None, False)
    neededTime = calculateTimeDelta(start_time, time.time())
    
    return (neededTime + 3) * numberOfPagesToScrape


def printRuntimeAndAskConfirmation(timeEstimation):
    print(f"This operation will take approximately {timeEstimation[0]} {timeEstimation[1]}. Continue? (Y/N)")
    continueInput = input("> ")

    if continueInput != "Y" and continueInput != "y":
        exit()


if __name__ == "__main__":
    # Get user input
    nextPage = getScrapeURL()
    fileName = getCSVFileName()
    numberOfPagesToScrape = getNumberOfPagesToScrape()

    # Estimate runtime
    print("Estimating runtime... Please wait! (Depending on your hardware and internet connection this might take up to 60 seconds)")
    timeNeeded = estimateRuntime(nextPage, numberOfPagesToScrape)
    timeEstimation = convertSecondsToAppropriateFormat(timeNeeded)
    printRuntimeAndAskConfirmation(timeEstimation)

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

        soup = createSoupObjectForURL(nextPage)
        scrapePage(soup, writer, True)

        # Get next page
        nextPage = soup.find('a', class_ = 'next-results')

        # No next page available
        if not nextPage:
            print("\033[93mThere are no more pages available to scrape. The program will now terminate\033[0m")
            break
        else:
            nextPage = nextPage['href']

        # Spiecal Case: Last Page to be scraped
        if (i == numberOfPagesToScrape - 1):
            print(f"\033[92mScraping finished!\033[0m")
            print(f"{i+1} / {numberOfPagesToScrape} pages scraped succesfully | Articles were saved into {fileName}")
            break

        # Wait 3 seconds after scraping one page to prevent the server from being overloaded or the IP from being blocked
        buffer(3)

        # Track how long the scraping of one page took to provide accurate Time Remaining Feedback
        tracked_times.append(calculateTimeDelta(start_time, time.time()))
        timeNeeded = calculateRemainingTime(tracked_times, numberOfPagesToScrape)
        timeEstimation = convertSecondsToAppropriateFormat(timeNeeded)

        print(f" | {i+1} / {numberOfPagesToScrape} | {timeEstimation[0]} {timeEstimation[1]} remaining", flush=True)

    file.close()
    
    removeNewLines()