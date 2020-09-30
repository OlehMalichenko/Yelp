## Requirement

`python 3.8`

## Install

#### Clone repository
`https://github.com/OlehMalichenko/Yelp.git`

#### Install requirements
`python3.8 -m pip install -r requirements.txt`

## RUN
`cd yelp`


### URL argument
`scrapy crawl yelpspider -a url=<url of business> -o <file_name.json>`

### FILE argument
`scrapy crawl yelpspider -a file=<path to file> -o <file_name.json>`

## OUT
for out in json-format add argument `-o <file_name.json>`

