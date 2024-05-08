# OTS Scraper

OTS Scraper is a simple command line Python script that allows you to scrape articles from the APA's "Originaltext-Service" (OTS). The script creates a csv file that will contain Title, Subtitle, Content, Publishing Date and Author of each article.

## Installation

### Installation using the provided executable (Recommended)

#### Windows

Download the .exe file from the [releases section]() and execute it.

#### Linux

1. Download the linux version of OTS Scraper from the [releases section]().
2. Make the downloaded file executable

```
sudo chmod +x OTS\ Scraper
```

3. Run the file

```
./OTS\ Scraper
```

#### MacOS

Please refer to the [Installation using the command line](<#installation-using-the-command-line-(advanced-users)>).

### Installation using the command line (Advanced Users)

Make sure you have a working installation of Python 3 on your operating system. It is recommended to create a new [Virtual Environment](https://docs.python.org/3/library/venv.html) before running the below commands.

1. Download repository

```
git clone ...
```

2. Install Dependencies

```
pip install -r requirements.txt
```

3. Run Script

```
python3 main.py
```

## Usage

```
Please provide OTS Link to scrape (e.g. '/pressemappe/199/spoe-parlamentsklub')
>
```

1. The script first asks you to provide the URL of the OTS page you wish to scrape. While it is recommended to only enter the path part of the URL (e.g. `https://www.ots.at/pressemappe/199/spoe-parlamentsklub -> /pressemappe/199/spoe-parlamentsklub`) you should also be able to enter the whole URL (e.g. `https://www.ots.at/pressemappe/199/spoe-parlamentsklub`)

```
Please provide the output filename (e.g. 'spoe_aussendungen.csv')
>
```

2. Here you can enter the filename of the output file. Please make sure that the file extension .csv is also specified. Alternatively, other file extensions can also be specified, but the output is always in csv format.

```
Please provide the number of pages to be scraped (e.g. '25')
>
```

3. The OTS Website lists 15 articles on each page. Enter the amount of pages that should be scraped (e.g. entering 3 will scrape 3 pages -> 3 \* 15 = 45 articles)

```
Estimating runtime... Please wait! (Depending on your hardware and internet connection this might take up to 60 seconds)
```

4. The script will now scrape a single page to determine the speed in which your machine is able to scrape the OTS webpage (Speed depends on your machines hardware, internet connection and load of the OTS Server) and determine how long it will approximately take to fulfill your request.

## Troubleshooting

```
Error establishing a connection. Please make sure that the provided URL is valid and that you're connected to the internet. Debug information:
...
```

This error occurs when the connection to the server could not be established. Please check if the URL you entered is correct and if your machine has access to the internet.

<hr>

```
Traceback (most recent call last):
...
```

If an error occurs that starts with `Traceback (most recent call last):` followed by any error message, please open an issue on GitHub and provide the following information:

- The full error message
- The plattform you're on (Windows, Mac, Linux)
- The URL you were trying to scrape
- The settings you have entered in the script
- Any additional steps you may have taken that resulted in this error

I'll try to look into it ASAP and will publish a fix for the problem.
