# get_sentiment_mlnet
This is an OpenFaaS function that uses [ML.NET](https://www.microsoft.com/net/learn/apps/machine-learning-and-ai/ml-dotnet) to analyze the sentiment of a supplied list of phrases. It requires the included sentiment.model file to be included as part of the function build. The sentiment model file was generated using my sample sentiment analysis application that is available [here](https://github.com/lucasalexander/mlnet-samples/tree/master/sentiment-analysis). You can use this application with different training data to generate an updated sentiment.model file, rebuild and redeploy the function.

This is a sample request for sentiment analysis on two phrases.
```
{
    "Phrases":[
        "This is good.",
        "This is horrible."
    ]
}
```

The response would look like this.
```
{
    "Phrases": [
        {
            "Phrase": "This is good.",
            "Sentiment": "Positive"
        },
        {
            "Phrase": "This is horrible.",
            "Sentiment": "Negative"
        }
    ]
}
```