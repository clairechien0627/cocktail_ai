from textblob import TextBlob

def analyze_sentiment(text):
    """
    分析文字的情感傾向

    Args:
        text: 要分析的文字

    Returns:
        情感分數 (-1.0 到 1.0)，負數表示負面，正數表示正面
    """
    try:
        # 使用 TextBlob 進行情感分析
        blob = TextBlob(text)
        # polarity 範圍是 -1.0 到 1.0
        return blob.sentiment.polarity

    except Exception as e:
        print(f"情感分析錯誤: {str(e)}")
        return 0.0  # 預設為中性


def get_sentiment_label(score):
    """
    將情感分數轉換為標籤

    Args:
        score: 情感分數

    Returns:
        情感標籤（正面、中性、負面）
    """
    if score > 0.3:
        return "正面"
    elif score < -0.3:
        return "負面"
    else:
        return "中性"


def should_warn_about_drinking(text, sentiment_score):
    """
    判斷是否需要提醒責任飲酒

    Args:
        text: 用戶訊息
        sentiment_score: 情感分數

    Returns:
        是否需要警告
    """
    # 檢查關鍵字
    warning_keywords = ['開車', '駕駛', '懷孕', '未成年', '喝很多', '喝太多', '醉了', '難過', '憂鬱']

    text_lower = text.lower()
    for keyword in warning_keywords:
        if keyword in text_lower:
            return True

    # 如果情感非常負面，也建議提醒
    if sentiment_score < -0.5:
        return True

    return False
