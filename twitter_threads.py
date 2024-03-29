# from TwitterAPI import TwitterAPI  # type: ignore
import tweepy
from tqdm import tqdm  # type: ignore
from time import sleep

class Threader(object):
    def __init__(self, tweets, api, user=None, wait=None, max_char=280, end_string=True):
        """Create a thread of tweets.

        Note that you will need your Twitter API / Application keys for
        this to work.

        Parameters
        ----------
        tweets : list of strings
            The tweets to send out
        api : instance of TwitterAPI
            An active Twitter API object using the TwitterAPI package.
        user : string | None
            A user to include in the tweets. If None, no user will be
            included.
        wait : float | None
            The amount of time to wait between tweets. If None, they will
            be sent out as soon as possible.
        max_char : int
            The maximum number of characters allowed per tweet. Threader will
            check each string in `tweets` before posting anything, and raise an
            error if any string has more characters than max_char.
        end_string : bool
            Whether to include a thread count at the end of each tweet. E.g.,
            "4/" or "5x".
        """
        # Check twitter API
        if not isinstance(api, tweepy.Client):
            raise ValueError('api must be an instance of tweepy.Client')
        self.api = api

        # Check tweet list
        if not isinstance(tweets, list):
            raise ValueError('tweets must be a list')
        if not all(isinstance(it, str) for it in tweets):
            raise ValueError('all items in `tweets` must be a string')
        # if len(tweets) < 2:
        #     raise ValueError('you must pass two or more tweets')

        # Other params
        self.user = user
        self.wait = wait
        self.sent = False
        self.end_string = end_string
        self.max_char = max_char

        # Construct our tweets
        self.generate_tweets(tweets)

        # Check user existence
        if isinstance(user, str):
            self._check_user(user)

    def _check_user(self, user):
        if user is not None:
            print('Warning: including users in threaded tweets can get your '
                  'API token banned. Use at your own risk!')
        resp = self.api.request('users/lookup', params={'screen_name': user})

        if not isinstance(resp.json(), list):
            err = resp.json().get('errors', None)
            if err is not None:
                raise ValueError('Error in finding username: {}\nError: {}'.format(user, err[0]))

    def generate_tweets(self, tweets):
        # Set up user ID to which we'll tweet
        user = '@{} '.format(self.user) if isinstance(self.user, str) else ''

        # Add end threading strings if specified
        self._tweets_orig = tweets
        self.tweets = []
        len_tweets = len(tweets)
        for ii, tweet in enumerate(tweets):
            this_status = '{}{}'.format(user, tweet)
            if self.end_string is True and len_tweets > 1:
                end_str = '{}/{}'.format(ii + 1, len_tweets)
                this_status += ' {}'.format(end_str)
            else:
                this_status = tweet
            self.tweets.append(this_status)

        if not all(len(tweet) < int(self.max_char) for tweet in self.tweets):
            raise ValueError("Not all tweets are less than {} characters".format(int(self.max_char)))

    def send_tweets(self):
        """Send the queued tweets to twitter."""
        if self.sent is True:
            raise ValueError('Already sent tweets, re-create object in order to send more.')
        self.tweet_ids_ = []
        self.responses_ = []
        self.params_ = []

        # Now generate the tweets
        for ii, tweet in tqdm(enumerate(self.tweets)):
            # Create tweet and add metadata
            # params = {'status': tweet}
            params = dict()
            if len(self.tweet_ids_) > 0:
                params['in_reply_to_tweet_id'] = self.tweet_ids_[-1]

            # Send POST and get response

            resp = self.api.create_tweet(text=tweet, **params)
            if resp.errors :
                raise ValueError('Error in posting tweets:\n{}'.format(resp.errors))
            self.responses_.append(resp.data)
            self.params_.append(params)
            self.tweet_ids_.append(resp.data['id'])
            if isinstance(self.wait, (float, int)):
                sleep(self.wait)
        self.sent = True

    def __repr__(self):
        s = ['Threader']
        s += ['Tweets', '------']
        for tweet in self.tweets:
            s += [tweet]
        s = '\n'.join(s)
        return s
