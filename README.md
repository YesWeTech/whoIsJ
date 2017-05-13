# Who is J?

One of the main goals of the ‘Yes We Tech’ community is contributing to create an inclusive space where we can celebrate diversity, provide visibility to women-in-tech, and ensure that everybody has an equal chance to learn, share and enjoy technology related disciplines.

As co-organisers of the JOTB event we are happy to see that the number of women speakers has been doubled this year from 5 to 10, representing a 20,8% of the total.

But, Is this diversity enough? How can we know that we have succeeded in our goal? and more importantly, how can we get a more diverse event in future editions?

This repository contains the source code used to analyse and present the findings made in order to investigate the diversity of the J On The Beach conference.

## How to use it
1. Clone or download the project
2. Execute `pip`to install following libraries
```
pip install twython
pip install sexmachine
pip install tweepy
pip install analyze
pip install argparse
pip install unidecode
pip install json
```

3. Execute `python index.py <twitter_username>`
4. The output is given in a `json` format under the `out/` folder

You can also analyse latest tweets from an account
1. Execute `python tweets.py <twitter_username> <number_of_tweets>`
2. The output is given in a `json` format under the `out/` folder
