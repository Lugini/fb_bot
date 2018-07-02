import json
import requests

import praw

import configs
from app import send_message
from models import User


class URLAnalyzer(object):
    def __init__(self):
        self.replasers = {
            "amazon.com": self.amazon_ref_replace
        }
    @staticmethod
    def is_ref_link(url):
        is_ref = False
        for tag in configs.URL_TYPES.values():
            if tag in url:
                is_ref = True
                break
        return is_ref

    def ref_code_replace(self, url):

        for domain in configs.REF_CODES:
            if domain in url:
                return self.replasers[domain](url)

    @staticmethod
    def amazon_ref_replace(url):
        str_1 = url.split("ref=")
        str_2 = str_1[1].split("?")
        str_2[0] = configs.REF_CODES["amazon.com"]
        new_url = "{}ref={}".format(str_1[0], configs.REF_CODES["amazon.com"])
        if len(str_2) > 1:
            new_url += "?{}".format('?'.join(str_2[1:]))
        return new_url


if __name__ == '__main__':
    url_analyzer = URLAnalyzer()
    reddit = praw.Reddit(client_id='QGgquYDRm7jKqQ',
                         client_secret='kIU_Rxo4gfO1jKP-XXMMHQH6Mug', password='131199artur',
                         user_agent='PrawTut', username = 'Lugini')

    subreddit = reddit.subreddit('GameDeals')
    i=0
    for submission_id in subreddit.stream.submissions():
        try:
            i += 1
            print(30*'_{}_'.format(i))
            submission = reddit.submission(id=submission_id)
            if submission.ups >= configs.MIN_UPVOTES and url_analyzer.is_ref_link(submission.url):
                for user in User.query.all():
                    new_url = url_analyzer.ref_code_replace(submission.url)
                    send_message(user.id_user, "{}\n{}".format(submission.title, new_url))

            else:
                continue
        except praw.exceptions.PRAWException as e:
            pass