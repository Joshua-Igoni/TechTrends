import sqlite3
import logging, os, sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
from werkzeug.wrappers import response

# Setup logging
logger = os.getenv("UDACITY LOGGER", "DEBUG").upper()
logger = (
      getattr(logging, logger)
      if logger in ["CRITICAL", "DEBUG", "ERROR", "INFO", "WARNING",]
      else logging.DEBUG
  )

standout = logging.StreamHandler(sys.stdout)
standerr = logging.StreamHandler(sys.stderr)
standout.setLevel(logging.DEBUG)
standerr.setLevel(logging.DEBUG)

formatlog ='%(asctime)s - %(name)s - %(levelname)s - %(message)s'

handlers = [standout,standerr]

logging.basicConfig(format = formatlog, level = logger, handlers=handlers)


# Function to get a database connection.
# This function connects to database with the name `database.db`

no_of_connections = 0

def get_db_connection():
    global no_of_connections
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    no_of_connections = no_of_connections + 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    global post_count
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    logging.info("Article '{0}' retrieved".format(post['title']))
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

#Define the health status of the application
@app.route('/healthz')
def healthcheck():
    response=app.response_class(
        response=json.dumps({"result":"Ok-healthy"}),
        status=200,
)
    return response

#Define the app metrics
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    response = app.response_class(
        response=json.dumps({"status": "success", "code": 0, "data": {"db_connection_count": no_of_connections, "post_count": len(posts)}}),
        status=200,
        mimetype='application/json'
    )
    app.logger.info('Metrics request successfull')
    return response

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      logging.info("article does not exist")  
      return render_template('404.html'), 404
    else:
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logging.info("About us page retrieved")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            logging.info("Article with title '{0}' created".format(title))
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
