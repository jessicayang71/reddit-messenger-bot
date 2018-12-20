import praw
import random
import time
import os


def bot_loggin():
    """"This function return your session in Reddit as an instance"""
    reddit = praw.Reddit(username='******',
                         password='*****',
                         client_id='',
                         client_secret='',
                         user_agent='')
    return reddit


def get_memes_bot(reddit):
    """"Returns a list with the first most populars images in the subreddit /memes"""
    jpg_url = []
    for submission in reddit.subreddit('memes').top('all'):
        if submission.url.endswith(".jpg"):
            jpg_url.append(submission.url)
            print(submission.url)
    return jpg_url


def get_thoughts_bot(reddit):
    """"Returns a list with the first most populars images in the subreddit /Showerthoughts"""
    jpg_url = []
    for submission in reddit.subreddit('Showerthoughts').hot(limit=30):
        jpg_url.append(submission.title)
        print(submission.title)

    return jpg_url


def random_url(lst):
    random_choice = random.choice(lst)
    return random_choice


if __name__ == '__main__':

    import webbrowser

    reddit = bot_loggin()
    if not reddit.read_only:
        print("Logged to Reddit!!")
    list_urls = get_memes_bot(reddit)
    picture_day = random_url(list_urls)

    while True:
        number_pictures = len(list_urls)
        if number_pictures == 1:
            print("This is my last pick-me-up for you")
            last_one = list_urls[-1]
            webbrowser.open(last_one)
            break

        ask_user = raw_input("Are you having a bad day? Y or N ?")
        if ask_user == "Y":     
            print("I have %i memes to cheer you up" % (number_pictures))
            check = raw_input("Do you want a meme? Y or N ?")
            if check == "Y":
                webbrowser.open(picture_day)
                list_urls.remove(picture_day)
                picture_day = random_url(list_urls)
                print("I need a short break")
                time.sleep(5)

            else:
                print("Ok, see you soon!")
                break

        else:
            print("That's the spirit! Have a good one!")
            break
