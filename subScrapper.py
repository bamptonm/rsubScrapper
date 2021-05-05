#!/usr/bin/env python
# coding: utf-8

import pandas as pd #for data transformation
import praw         #to access reddit data
import re #for regex on scraped text
import requests # for posting messag
import sys, getopt

def main(argv):
   inputfile = ''
   outputfile = ''
   
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["iSubReddit="])
   except getopt.GetoptError:
      print ('test.py -i <input subReddit>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print ('test.py -i <input subReddit>')
         sys.exit()
      elif opt in ("-i", "--iSubReddit"):
         inputfile = arg

   print ("Preparing to search r/" +  inputfile.replace(" ", ""))
   
if __name__ == "__main__":
   main(sys.argv[1:])
   
subReddit = sys.argv[2]

reddit = praw.Reddit(
    client_id = "",
    client_secret = "",
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
)

df = []

for post in reddit.subreddit(subReddit).hot(limit=1500):
    
    content = {
        "title" : post.title,
        "text" : post.selftext
    }
    df.append(content)

df = pd.DataFrame(df)


# Step 2: Analyze word frequency
regex = re.compile('[^a-zA-Z ]')
word_dict = {}

for (index, row) in df.iterrows():
    # titles
    title = row['title']
    
    title = regex.sub('', title)
    title_words = title.split(' ')
    
    # content
    content = row['text']
    
    content = regex.sub('', content)
    content_words = content.split(' ')
    
    # combine
    words = title_words + content_words
    
    for x in words:
        
        if x in ['A', 'B', 'GO', 'ARE', 'ON', 'IT', 'ALL', 'NEXT', 'PUMP', 'AT', 'NOW', 'FOR', 'TD', 'CEO', 'AM', 'K', 'BIG', 'BY', 'LOVE', 'CAN', 'BE', 'SO', 'OUT', 'STAY', 'OR', 'NEW','RH','EDIT','ONE','ANY']:
            pass
        elif x in word_dict:
            word_dict[x] += 1
        else:
            word_dict[x] = 1

word_df = pd.DataFrame.from_dict(list(word_dict.items())).rename(columns = {0:"Term", 1:"Freq"})


# Step 3: Get a list of stock tickers
ticker_df = pd.read_csv('tickers.csv').rename(columns = {"Symbol":"Term", "Name":"Company_Name"})


# Step 4: Compare tickers and words scraped
stonks_df = pd.merge(ticker_df, word_df, on="Term")
stonks_df = stonks_df.sort_values(by="Freq", ascending = False, ignore_index = True).head(20)


# Step 5: post top 10 most discussed stocks
print("\n\n~~Top 10 Stonks on r/"+ subReddit + "~~\n") 

for x in range(10):
  print(str(x+1) + ") (" + stonks_df['Term'][x] + ") " + stonks_df['Company_Name'][x] + " - " + str(stonks_df['Freq'][x]) + " mentions\n")


