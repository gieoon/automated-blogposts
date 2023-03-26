import openai
import time
import calendar
import firebase_admin
from firebase_admin import credentials, firestore
import re
from constants import OPENAI_API_KEY

cred = credentials.Certificate("./livefeed-jobs-1f0968160681.json")
app = firebase_admin.initialize_app(cred)

db = firestore.client()

openai.api_key = OPENAI_API_KEY

def save_blogpost_to_db(blog_post):

    # gmt stores current gmtime
    gmt = time.gmtime()
    print("gmt:-", gmt)
    
    # ts stores timestamp
    ts = calendar.timegm(gmt)

    db.collection(u'CMS').document('careers_org').collection(u'Articles').document(str(ts)).set(blog_post, merge=True)
    
    print('saved to db successfully')
    return

def get_keywords():
    
    save_count = 0

    # Get keywords
    messages=[
        {"role": "user", "content": "Keywords about IT jobs"}
    ]

    keywords = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    
    keywords = keywords.choices[0].message.content
    # print('keywords', keywords)

    keywords = list(map(lambda x: re.sub(r'\d*?\.|\)', '', x).strip(), keywords.split('\n')))

    print('keywords after regex', keywords)

    for keyword in keywords:

        # Generate blogpost for keyword.
        print("current keyword", keyword)
        
        messages=[
            {"role": "user", 
            "content": f'A list of 10 viral titles for blog posts about IT jobs in New Zealand with the keyword: "{keyword}" separated by <<'}
        ]

        # Titles
        
        blog_titles = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        blog_titles = blog_titles.choices[0].message
        print('\nall blog titles: ', blog_titles, '\n\n')
        blog_titles = re.split('<<|"|\n', blog_titles.content)
        # blog_titles = blog_titles.split('"')
        # blog_titles = blog_titles.split('\n')
        blog_titles = list(filter(lambda x: len(x) > 10, blog_titles))
        # blog_titles = list(filter(lambda x: len(x) > 10, blog_titles.content.split('<<')))
        # print('\n after split', blog_titles, '\n\n')
        blog_titles = list(map(lambda x: re.sub(r'\d*?\.|\)', '', x).strip(), blog_titles))
        # print('\n after removing leading numbers', blog_titles, '\n\n')

        # print('all blog titles: ', blog_titles, '\n\n')

        for blog_title in blog_titles:
            blog_title = re.sub(r'<<', '', blog_title)
            blog_title = re.sub(r'>>', '', blog_title)
            blog_title = re.sub(r'\n', '', blog_title)
            blog_title = re.sub('"', '', blog_title)
            if len(blog_title) > 400:
                # Bypass this for now.
                continue

            print('one blog_title => ', blog_title)

            blog_content = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": f'A long informative and humorous blog post without a conclusion with the title: "{blog_title}"'}
                ]
            )
            
            blog_content = blog_content.choices[0].message.content

            print('blog_post =>\n\n', blog_content, '\n\n')
            # is_ok = input('is this ok? (y/n) (Add option to extend later)')
            # print('is_ok', is_ok)
            is_ok = 'y'
            # if is_ok === 'e':

            #     # messages.append(completion.choices[0].message)
            #     messages = [
            #         {"role": "user", "content": f'A long blog post with the title: "{blog_title}"'}
            #     ]
            #     messages.append({"role": "assistant", "content": blog_content})
            #     messages.append({"role": "user", "content": "great, now continue the list please with another 10 examples."})

            #     continuation = openai.ChatCompletion.create(
            #         model="gpt-3.5-turbo",
            #         messages=messages
            #     )

            #     print('continue the list please', completion.choices[0].message)

            if is_ok == 'y':
                # Save to DB
                save_count += 1
                print('saving to db', save_count)
                blog_post = {
                    u'title': blog_title,
                    u'content': blog_content,
                    u'date': firestore.SERVER_TIMESTAMP,
                    u'createdOn': firestore.SERVER_TIMESTAMP,
                    u'orderInList': None,#0,
                    u'images': [],
                    u'files': [],
                    u'fields': [],
                    u'audio': [],
                    u'additionalDate': "",
                    u'was_generated': True,
                }
                save_blogpost_to_db(blog_post)
                
            if is_ok == 'n':
                print('not saving to db')

get_keywords()