# mapping-task


# strip html tag function
def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def main():
    # define session
    s = requests.Session()

    # get all article list
    api_list_url = "https://mapping-test.fra1.digitaloceanspaces.com/data/list.json"
    r = s.get(api_list_url)

    # check status code
    if r.status_code == 200:
        # convert content to json
        article_list = r.json()

        # for loop each article and get article id
        for article in article_list:
            data = {}
            article_id = article["id"]

            # make article url and get article data
            arc_data_url = "https://mapping-test.fra1.digitaloceanspaces.com/data/articles/{id}.json".format(id=article_id)
            get_data = s.get(arc_data_url)
            if get_data.status_code == 200:
                # convert content to json
                data = get_data.json()
                categories = [data["category"]]
                # modify data , add field depend on Article model
                data["categories"] = categories
                data["publication_date"] = datetime.strptime(data["pub_date"], '%Y-%m-%d-%H;%M;%S')
                if "mod_date" in data:
                    data["modification_date"] = datetime.strptime(data["mod_date"], '%Y-%m-%d-%H:%M:%S')
                else:
                    data["modification_date"] = datetime.now()

                # if sections's length big than 4  then slice it
                if len(data["sections"]) > 4:
                    data["sections"] = data["sections"][:4]

                # make temp sections and put it
                tmp_section = []
                for idx, section in enumerate(data["sections"]):
                    tmp = {}

                    # make each temp section
                    for k, v in section.items():
                        if k == "text":
                            tmp[k] = strip_tags(v)
                        elif k == "type" and v == "media":
                            tmp["text"] = "media"
                            tmp["type"] = "text"
                        else:
                            tmp[k] = v
                    tmp_section.append(tmp)

                # put sections
                data["sections"] = tmp_section

                # get media data
                arc_media_url = "https://mapping-test.fra1.digitaloceanspaces.com/data/media/{id}.json".format(id=article_id)
                get_data = s.get(arc_media_url)

                # if status code == 200
                if get_data.status_code == 200:
                    # get image, media data and modify section
                    img_data = get_data.json()

                    # put image section
                    data["sections"].append(img_data[0])

                    # modify media section and put section
                    img_data[1]["publication_date"] = datetime.strptime(img_data[1]["pub_date"], '%Y-%m-%d-%H;%M;%S')
                    if "mod_date" in img_data[1]:
                        img_data[1]["modification_date"] = datetime.strptime(img_data[1]["mod_date"], '%Y-%m-%d-%H:%M:%S')
                    else:
                        img_data[1]["modification_date"] = datetime.now()
                    data["sections"].append(img_data[1])
                # else create empty section.
                else:
                    image_section = {"type": "image", "url": "https://google.com", "alt": "none", "caption": "none",
                                     "source": "none"}
                    media_section = {"type": "media", "id": "None", "url": "https://google.com", "thumbnail": "https"
                                                                                                              "://google.com", "author": "none", "caption": "none", "publication_date": datetime.now(), "modification_date": datetime.now(), "duration": 0}
                    data["sections"].append(image_section)
                    data["sections"].append(media_section)
                user = Article(**data)
                print (user)
            else:
                pass
    else:
        print("invalid status : " + str(r.status_code))


if __name__ == "__main__":

    # create schedule running function every 5 minutes.
    schedule.every(5).minutes.do(main)
    while True:
        schedule.run_pending()
    # main()
    # print ("done")

