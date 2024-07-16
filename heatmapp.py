import glob
from flask import Flask, render_template, request, flash
from pathlib import Path
#import
app = Flask(__name__)

@app.route('/')
def dropdown():
    htmlswdir = glob.glob("templates/heatmap*.html")
    htmls = [Path(x).stem +".html" for x in htmlswdir]
    return render_template("input.html", htmls=htmls)

@app.route('/render/', methods=['GET','POST'])
def render():
    tts = request.form.get('state')
    print(tts)
    return render_template(tts)
if __name__ == '__main__':
    app.run(debug=True)