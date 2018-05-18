using System;
using Microsoft.ML.Models;
using Microsoft.ML.Runtime;
using Microsoft.ML.Runtime.Api;
using Microsoft.ML.Trainers;
using Microsoft.ML.Transforms;
using System.Collections.Generic;
using System.Linq;
using Microsoft.ML;
using Newtonsoft.Json;

namespace Function
{
    public class FunctionHandler
    {
        public void Handle(string input) {
			var request = JsonConvert.DeserializeObject<SentimentRequest>(input);
            var phrases = request.Phrases;
			var model = PredictionModel.ReadAsync<SentimentData, SentimentPrediction>("sentiment.model").Result;
			Predict(model, phrases);
        }
		
		public void Predict(PredictionModel<SentimentData, SentimentPrediction> model, string[] phrases)
        {
			
			List<SentimentData> sentiments = new List<SentimentData>();
			foreach(var phrase in phrases)
			{
				sentiments.Add(new SentimentData{SentimentText = phrase, Sentiment = 0});
			}

            IEnumerable<SentimentPrediction> predictions = model.Predict(sentiments);

            var sentimentsAndPredictions = sentiments.Zip(predictions, (sentiment, prediction) => new { sentiment, prediction });
			
			List<ResponsePhrase> responsesphrases = new List<ResponsePhrase>();

            foreach (var item in sentimentsAndPredictions)
            {
                responsesphrases.Add(new ResponsePhrase{Phrase = item.sentiment.SentimentText, Sentiment = (item.prediction.Sentiment ? "Positive" : "Negative")});
            }
            var response = new SentimentResponse{Phrases = responsesphrases.ToArray()};
            Console.WriteLine(JsonConvert.SerializeObject(response));
        }
    }
	
	public class ResponsePhrase
	{
		public string Phrase;
		public string Sentiment;
	}
	
	public class SentimentRequest
	{
		public string[] Phrases;
	}
	
	public class SentimentResponse
	{
		public ResponsePhrase[] Phrases;
	}
	
	public class SentimentData
    {
        [Column(ordinal: "0")]
        public string SentimentText;
        [Column(ordinal: "1", name: "Label")]
        public float Sentiment;
    }

    public class SentimentPrediction
    {
        [ColumnName("PredictedLabel")]
        public bool Sentiment;
    }
}
