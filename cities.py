import csv
import openai
import time
import calendar
import firebase_admin
from firebase_admin import credentials, firestore
import re
from constants import OPENAI_API_KEY

cred = credentials.Certificate("sheets2website-1598313088115-firebase-adminsdk-qimn1-ea791cb7a9.json")
app = firebase_admin.initialize_app(cred)

db = firestore.client()

openai.api_key = OPENAI_API_KEY

def save_blogpost_to_db(blog_post):

    # gmt stores current gmtime
    gmt = time.gmtime()
    print("gmt:-", gmt)
    
    # ts stores timestamp
    ts = calendar.timegm(gmt)

    db.collection(u'CMS').document('webbi_co_nz').collection(u'Blogs').document(str(ts)).set(blog_post, merge=True)
    
    print('saved to db successfully')
    return

def get_keywords():
    
    save_count = 0
    
    with open('cities.csv') as f:
        reader = csv.DictReader(f)
        
        is_allowed = False

        for row in reader:
            print(row['name'], '<==>', row['country'])
            
            keyword = row['name']
            
            # Resume from last keyword
            if keyword == 'Farah':
                is_allowed = True
            
            if not is_allowed:
                continue
                

            # Generate blogpost for keyword.
            print("current keyword", keyword)
            
            messages=[
                {"role": "user", 
                "content": f"A post advertising Webbi Digital Studio's website design services for people in '{keyword}' helping businesses with local SEO through a world class global team."}
            ]

            # Titles
            
            blog_content = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", #"babbage"
                messages=messages
            )

            # blog_titles = blog_titles.choices[0].message
            # print('\nall blog titles: ', blog_titles, '\n\n')
            # blog_titles = re.split('<<|"|\n', blog_titles.content)
            # print('\n after removing leading numbers', blog_titles, '\n\n')

            # print('all blog titles: ', blog_titles, '\n\n')

            # print('blog_title => ', blog_title)

            # blog_content = openai.ChatCompletion.create(
            #     model="gpt-3.5-turbo",
            #     messages=[
            #         {"role": "user", "content": f'A long informative and humorous blog post without a summary or conclusion at the end with the title: "{blog_title}"'}
            #     ]
            # )
            
            blog_content = blog_content.choices[0].message.content
            blog_title = f"We're in {keyword}, {row['country']}"
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
            def keyword_to_collectionname(city_name):
                city_name = re.sub(r'[ ]{2,}',' ', city_name)
                city_name = re.sub(r'[ ]','-', city_name)
                print('new city name', city_name)
                return city_name.lower()

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
                    u'fields': [{
                        "slug": "we-are-in-" + keyword_to_collectionname(keyword),
                        "type": "slug",
                    }],
                    u'audio': [],
                    u'additionalDate': "",
                    u'was_generated': True,
                }
                save_blogpost_to_db(blog_post)
                
            if is_ok == 'n':
                print('not saving to db')

get_keywords()