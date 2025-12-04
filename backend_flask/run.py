from app import create_app

app = create_app()

if __name__ == '__main__':
    # use_reloader=False 可以避免 Windows 上的 socket 錯誤
    # 但在開發時仍保留 debug 模式的其他功能
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
