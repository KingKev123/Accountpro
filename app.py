if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Starting AccountPro")
    print(f"📍 Running on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
