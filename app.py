# app.py
from flask import Flask, render_template, request, jsonify, session
from googleapiclient.discovery import build
import re
import emoji
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import io
import base64
import os
import json
from matplotlib.figure import Figure
import numpy as np
import html

# Set your YouTube API key here
API_KEY = 'AIzaSyCzlLINvJjmDims_aUiMKT02M_22k5Bnxk'  # Replace with your actual API key

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

def extract_video_id(url):
    """Extract YouTube video ID from various URL formats"""
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\\.(com|be)/'
        '(watch\\?v=|embed/|v/|.+\\?v=)?([^&=%\\?]{11})')
    
    match = re.match(youtube_regex, url)
    if match:
        return match.group(6)
    return url[-11:] if len(url) >= 11 else None

def analyze_youtube_comments(video_url):
    """Analyze YouTube comments and return sentiment data"""
    try:
        # Extract video ID
        video_id = extract_video_id(video_url)
        if not video_id:
            return {"error": "Invalid YouTube URL"}
        
        # Initialize YouTube API
        youtube = build('youtube', 'v3', developerKey=API_KEY)
        
        # Get channel ID of video uploader
        video_response = youtube.videos().list(
            part='snippet',
            id=video_id
        ).execute()
        
        # Check if video exists
        if not video_response.get('items'):
            return {"error": "Video not found"}
        
        video_snippet = video_response['items'][0]['snippet']
        uploader_channel_id = video_snippet['channelId']
        video_title = video_snippet['title']
        
        # Fetch comments
        comments = []
        nextPageToken = None
        while len(comments) < 1000:
            request = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=100,
                pageToken=nextPageToken
            )
            response = request.execute()
            
            if not response.get('items'):
                break
                
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']
                # Filter out comments from video uploader
                if comment['authorChannelId']['value'] != uploader_channel_id:
                    comments.append(clean_html_tags(comment['textDisplay']))
            
            nextPageToken = response.get('nextPageToken')
            if not nextPageToken:
                break
        
        # Filter comments
        hyperlink_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        threshold_ratio = 0.65
        relevant_comments = []
        
        for comment_text in comments:
            comment_text = comment_text.lower().strip()
            emojis = emoji.emoji_count(comment_text)
            text_characters = len(re.sub(r'\s', '', comment_text))
            
            if (any(char.isalnum() for char in comment_text)) and not hyperlink_pattern.search(comment_text):
                if emojis == 0 or (text_characters / (text_characters + emojis)) > threshold_ratio:
                    relevant_comments.append(comment_text)
        
        # Analyze sentiment
        sentiment_object = SentimentIntensityAnalyzer()
        polarity = []
        positive_comments = []
        negative_comments = []
        neutral_comments = []
        
        for comment in relevant_comments:
            sentiment_dict = sentiment_object.polarity_scores(comment)
            polarity_score = sentiment_dict['compound']
            polarity.append(polarity_score)
            
            if polarity_score > 0.05:
                positive_comments.append(comment)
            elif polarity_score < -0.05:
                negative_comments.append(comment)
            else:
                neutral_comments.append(comment)
        
        # Calculate statistics
        avg_polarity = sum(polarity) / len(polarity) if polarity else 0
        sentiment_result = ""
        if avg_polarity > 0.05:
            sentiment_result = "Positive"
        elif avg_polarity < -0.05:
            sentiment_result = "Negative"
        else:
            sentiment_result = "Neutral"

        # Find most positive and negative comments
        most_positive_comment = relevant_comments[polarity.index(max(polarity))] if polarity else ""
        most_negative_comment = relevant_comments[polarity.index(min(polarity))] if polarity else ""
        
        # Prepare chart data
        positive_count = len(positive_comments)
        negative_count = len(negative_comments)
        neutral_count = len(neutral_comments)
        
        # Generate charts
        charts = generate_charts(positive_count, negative_count, neutral_count)
        
        return {
            "success": True,
            "video_title": video_title,
            "comments_analyzed": len(relevant_comments),
            "avg_polarity": avg_polarity,
            "sentiment_result": sentiment_result,
            "most_positive_comment": most_positive_comment,
            "most_positive_score": max(polarity) if polarity else 0,
            "most_negative_comment": most_negative_comment,
            "most_negative_score": min(polarity) if polarity else 0,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "bar_chart": charts["bar_chart"],
            "pie_chart": charts["pie_chart"]
        }
    
    except Exception as e:
        return {"error": str(e)}

def clean_html_tags(text):
    """Remove HTML tags from text and decode HTML entities"""
    # First remove HTML tags
    text = re.sub(r'<.*?>', ' ', text)
    # Then decode HTML entities like &#39; (apostrophe)
    text = html.unescape(text)
    return text

def generate_charts(positive_count, negative_count, neutral_count):
    """Generate bar and pie charts for sentiment analysis with consistent dimensions"""
    labels = ['Positive', 'Negative', 'Neutral']
    comment_counts = [positive_count, negative_count, neutral_count]
    colors = ['#4CAF50', '#F44336', '#9E9E9E']
    
    # Set consistent figure size for both charts
    fig_size = (8, 6)
    
    # Set font sizes
    label_size = 20
    tick_size = 20
    percent_size = 20
    
    # Bar chart
    fig_bar = Figure(figsize=fig_size)
    ax_bar = fig_bar.add_subplot(1, 1, 1)
    ax_bar.bar(labels, comment_counts, color=colors)
    ax_bar.set_xlabel('Sentiment', fontsize=label_size)
    ax_bar.set_ylabel('Comment Count', fontsize=label_size)
    ax_bar.tick_params(axis='both', which='major', labelsize=tick_size)
    fig_bar.tight_layout()
    
    buf_bar = io.BytesIO()
    fig_bar.savefig(buf_bar, format='png', dpi=100)
    buf_bar.seek(0)
    bar_chart = base64.b64encode(buf_bar.getbuffer()).decode('ascii')
    
    # Pie chart
    fig_pie = Figure(figsize=fig_size)
    ax_pie = fig_pie.add_subplot(1, 1, 1)
    ax_pie.pie(comment_counts, labels=labels, autopct='%1.1f%%', colors=colors, 
               textprops={'fontsize': percent_size})
    fig_pie.tight_layout()
    
    buf_pie = io.BytesIO()
    fig_pie.savefig(buf_pie, format='png', dpi=100)
    buf_pie.seek(0)
    pie_chart = base64.b64encode(buf_pie.getbuffer()).decode('ascii')
    
    return {"bar_chart": bar_chart, "pie_chart": pie_chart}

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    video_url = request.form.get('video_url')
    
    if not video_url:
        return render_template('index.html', error="Please enter a YouTube URL")
    
    results = analyze_youtube_comments(video_url)
    
    if "error" in results:
        return render_template('index.html', error=results["error"])
    
    # Store results in session for potential reuse
    session['analysis_results'] = json.dumps(results)
    
    return render_template('results.html', 
                          results=results,
                          bar_chart=results["bar_chart"],
                          pie_chart=results["pie_chart"])

if __name__ == '__main__':
    app.run(debug=True)
