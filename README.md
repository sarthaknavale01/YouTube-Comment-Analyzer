# YouTube-Comment-Analysis

This tool analyzes the sentiment of comments on YouTube videos. It uses sentiment analysis to classify comments as positive, negative, or neutral, and provides visualizations to display the distribution of these sentiments.


## 🚀 Features

- **YouTube Comment Analysis**: Fetch and analyze comments on a YouTube video.
- **Sentiment Classification**: Categorizes comments into Positive, Negative, or Neutral sentiments.
- **Visualization**: Displays sentiment distribution as bar and pie charts.
- **Notable Comments**: Highlights the most positive and negative comments with sentiment scores.

## 🛠️ Technologies/ Tools

* Jupyter Notebook 
* Python 3+
* Python packages
  * Google API Client - `pip install google-api-python-client`
  * VaderSentiment - `pip install vaderSentiment`
  * Matplotlib - `pip install matplotlib`
  * Emoji - `pip install emoji`
  * Numpy - `pip install numpy`
  * Flask - `pip install flask`
* HTML5
* CSS3

Use the Analysis

   * Open your browser and go to `http://127.0.0.1:5000/`.
   * Enter the YouTube video URL in the provided input field.
   * Click on **"Analyze Comments"** to process the comments of the video.
   * The results page will display the sentiment analysis results along with sentiment distribution charts.
  
## 📝 How This Works

1. **Extract Video ID**: The user provides a YouTube video URL, which is parsed to extract the video ID.
2. **Fetch Comments**: The YouTube Data API fetches up to 1000 comments from the video.
3. **Clean and Filter Comments**: The comments are cleaned (HTML tags removed) and filtered for relevance.
4. **Sentiment Analysis**: Each comment is analyzed using **Vader Sentiment Analysis** to classify it as positive, negative, or neutral.
5. **Visualization**: Visual representations of sentiment distributions are displayed as bar and pie charts.
6. **Display Results**: Results, including sentiment statistics and notable comments, are shown to the user.

