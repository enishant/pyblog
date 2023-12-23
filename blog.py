import os
import openai
import json

openai.api_key = 'sk-YOUR-KEY-HERE' # Update API key here
messages = [ {"role": "system", "content":"You are a intelligent assistant."} ]
current_directory=os.getcwd()
wordpress_directory='/var/www/html'
article_count = 0;

# Write new article with content
def write_article(article_number, content):
    if os.path.isfile('./articles/' + str(article_number) + '.txt') == False:
        with open('./articles/' + str(article_number) + '.txt', 'w') as f:
            f.write(content + '\n')

# Read existing article by article number to get title & content
def read_article(article_number):
    count = 0
    title = ''
    content = ''
    if os.path.isfile('./articles/' + str(article_number) + '.txt') == True:
        with open('./articles/' + str(article_number) + '.txt', 'r') as f:
            while(True):
                count += 1
                line = f.readline()
                if not line:
                    break
                if count == 1:
                    title = line.strip()
                    title = title.replace('Title:', '').strip()
                    continue
                if count == 2:
                    continue
                else:
                    content += line
    write_article(str(article_number) + '_content',content)
    return {'title': title, 'content':content}

def get_article_title(article_number):
    article = read_article(article_number)
    return article['title']

def get_article_content(article_number):
    article = read_article(article_number)
    return article['content']

# Log chatgpt conversation
def write_chatgpt_log(messages):
    if os.path.isfile('chatgpt.json') == True:
        with open("chatgpt.json", "w") as outfile:
            json.dump(messages, outfile)

# Read existing chatgpt conversation
def read_chatgpt_log(messages):
    if os.path.isfile('chatgpt.json') == True:
        outfile = open('chatgpt.json')
        messages = json.load(outfile)
    return messages

# Create WordPress post with wpcli
def wp_create_post(article_number):
    if os.path.isdir(wordpress_directory):
        article = read_article(article_number)
        post_title = article['title']
        post_content = article['content']

        os.chdir(wordpress_directory)
        wp_current_directory=os.getcwd()

        print("wp post create " + wordpress_directory + "/pyblog/articles/" + str(article_number) + "_content.txt --post_title='" + post_title + "' --post_status='draft'")
        os.system("wp post create " + wordpress_directory + "/pyblog/articles/" + str(article_number) + "_content.txt --post_title='" + post_title + "' --post_status='draft'")
        # os.system("wp post create --post_title='" + post_title + "' --post_content='" + post_content + "' --post_status='draft'")

        os.chdir(current_directory)
        os.unlink(wordpress_directory + "/pyblog/articles/" + str(article_number) + "_content.txt")

# Use this function manually to write last article from chatgpt conversation
def write_last_article():
    article_count = 0
    if article_count == 0:
        article_count = os.popen('ls articles/*.txt | wc -l').read()
    article_count = int(article_count) + 1
    messages = read_chatgpt_log([])
    reply = messages[-1]['content']
    write_article(article_count,reply)
    wp_create_post(article_count)

if __name__=='__main__':
    while(True):
        os.system('clear')
        print('Default WordPress path is: ' + wordpress_directory)
        wordpress_dir_path = input("Enter path for different WordPress directory: ")
        if wordpress_dir_path == '':
            os.system('clear')
            print('Moving forward with Default WordPress path: ' + wordpress_directory)
            os.system('sleep 2')
            break

        is_dir = os.path.isdir(wordpress_dir_path)
        if is_dir == True:
            wordpress_directory = wordpress_dir_path
            break
        else:
            os.system('clear')
            print('Provided path does not exists. Default WordPress path is: ' + wordpress_directory)
            retry = input("Wish to use default path? Please answer Yes OR No: ")
            retry = retry.lower()
            if retry == 'yes':
                continue
            if retry == 'no':
                break
            else:
                continue
            os.system('sleep 2')

    while(True):
        os.system('clear')
        chatgpt_conversation_flag = input("Log chatgpt conversation? Please answer Yes OR No: ")
        chatgpt_conversation_flag = chatgpt_conversation_flag.lower()
        if chatgpt_conversation_flag == 'yes' or chatgpt_conversation_flag == 'no':
            break
        else:
            os.system('clear')
            print('Please confirm about creating log.')
            os.system('sleep 2')
            continue

    messages = read_chatgpt_log(messages)

    if chatgpt_conversation_flag == 'yes':
        write_chatgpt_log(messages)

    if article_count == 0:
        article_count = os.popen('ls articles/*.txt | wc -l').read()

    while(True):
        os.system('clear')
        message = input("Article topic: ")
        if message:
            article_count = int(article_count) + 1
            blog_article = 'Create a WordPress blog article for topic: ' + message + '. Need professional content with SEO readablity.'
            messages.append(
                {"role": "user", "content": blog_article}, 
            )
            chat = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages 
            )
            reply = chat.choices[0].message.content 
            messages.append({"role": "assistant", "content": reply})

            if chatgpt_conversation_flag == 'yes':
                write_chatgpt_log(messages)

            write_article(article_count,reply)

            wp_create_post(article_count)

            os.system('sleep 2')
        else:
           respond("No topic has been provided.")
           os.system('sleep 2')
