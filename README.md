# Generates SEO blog posts for website

1. Generates keywords for blogpost
1. With the keywords, generates full articles
1. Programmatically inserts these articles into the DB as blog posts.
1. Watch SEO grow :)

# How it works

After generating the blog posts, they are saved into an external Firebase/Firestore DB, which is configured to automatically show up in the website I have created based on [this](https://github.com/gieoon/NextJS-Blank-Template) NextJS Template.

# Virtual Environment

$ python3 -m venv env

$ python3 -m pip install openai
$ python3 -m pip install firebase-admin
$ python3 -m pip freeze > requirements.txt