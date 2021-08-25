# Simple data mapping
Your task is to create a simple script that will pull the newest articles 
from the provided API every 5 minutes, then map them into a format defined in
the models.py file (class Article) and finally print them out. 
We will assess your code performance, readability, reusability and resilience to errors.

The API endpoints you need to use:
* list of articles: GET https://mapping-test.fra1.digitaloceanspaces.com/data/list.json
* details of an article: GET https://mapping-test.fra1.digitaloceanspaces.com/data/articles/{article_id}.json
* media of an article: GET https://mapping-test.fra1.digitaloceanspaces.com/data/media/{article_id}.json

Requirements:
1. Create a public repository for your code
2. Create a basic README for your code. In the readme remember to add instructions
how to start your code and write how long it took to create it
3. After starting, the script should execute automatically every 5 minutes
4. The example API has very limited data. Write your solution so that it is optimal
   for processing few thousand articles per day.
5. Sections that contain text should be stripped of any html elements, but keeping the content

