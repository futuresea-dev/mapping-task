from abc import ABC
from datetime import datetime
from typing import Optional, Set, List, Union, Literal
from pydantic import BaseModel, HttpUrl, Field
import requests
from dateutil import parser
from io import StringIO
from html.parser import HTMLParser
import schedule


class Section(BaseModel):
    pass


class HeaderSection(Section):
    type: Literal["header"] = Field(..., description="Section type - 'header'", example="header")
    level: int = Field(
        ...,
        description="The level of the header. The higher the number, the less important.",
        example="1",
    )
    text: str = Field(
        ...,
        description="Content of the header.",
        example="This is how you define a header",
    )


class TitleSection(Section):
    type: Literal["title"] = Field(..., description="Section type - 'title'", example="title")
    text: str = Field(
        ...,
        description="Content of the title.",
        example="This is how you define a title.",
    )


class LeadSection(Section):
    type: Literal["lead"] = Field(..., description="Section type - 'lead'", example="lead")
    text: str = Field(
        ...,
        description="Content of the lead.",
        example="This is how you define a lead.",
    )


class TextSection(Section):
    type: Literal["text"] = Field(..., description="Section type - 'text'", example="text")
    text: str = Field(
        ...,
        description="Content of the text.",
        example="This is how you define a text.",
    )


class ImageSection(Section):
    type: Literal["image"] = Field(..., description="Section type - 'image'", example="image")
    url: HttpUrl = Field(
        ..., description="Url to the image", example="https://url.to.image/image.jpg"
    )
    alt: Optional[str] = Field(
        None,
        description="Alternative text to display if image does not appear.",
        example="The alternative text.",
    )
    caption: Optional[str] = Field(
        None,
        description="The description of the image.",
        example="The description of the image.",
    )
    source: Optional[str] = Field(
        None,
        description="An Author or Organization Name",
        example="Pawel Glimos",
    )


class MediaSection(Section):
    type: Literal["media"] = Field(..., description="Section type - 'media'", example="media")
    id: str = Field(
        ...,
        description="Provider internal id of the media",
        example="media_id",
    )
    url: HttpUrl = Field(
        ..., description="Url to the media", example="https://some.website/media.mp4"
    )
    thumbnail: Optional[HttpUrl] = Field(
        None,
        description="Url to the thumbnail of the media",
        example="https://some.website/article/thumb.jpg",
    )
    caption: Optional[str] = Field(
        None, description="Caption of the media", example="This video shows a tutorial"
    )
    author: Optional[str] = Field(
        None, description="Name of the author of the media", example="Some Author"
    )
    publication_date: datetime = Field(
        ..., description="Datetime of media publication", example="2020-07-08T20:50:43Z"
    )
    modification_date: Optional[datetime] = Field(
        None, description="Datetime of media modification", example="2020-07-08T20:50:43Z"
    )
    duration: Optional[int] = Field(
        None, description="Duration of the media in seconds", example=120
    )


SECTION_TYPES = Union[
    TextSection,
    TitleSection,
    LeadSection,
    HeaderSection,
    ImageSection,
    MediaSection
]


class Article(BaseModel):
    id: str = Field(..., description="Internal provider id", example="article_id")
    original_language: str = Field(
        ..., description="Article original language", example="en"
    )
    # url: HttpUrl = Field(
    #     ...,
    #     description="Url to the article",
    #     example="https://some.website/article.html",
    # )
    thumbnail: Optional[HttpUrl] = Field(
        None,
        description="Url to the thumbnail of the article",
        example="https://some.website/article/thumb.jpg",
    )
    categories: Optional[Set[str]] = Field(
        None, description="List of article categories", example=["news", "local"]
    )
    tags: Optional[Set[str]] = Field(
        None, description="List of article tags", example=["news", "local"]
    )
    author: Optional[str] = Field(
        None, description="Name of the author of the article", example="Some Author"
    )
    publication_date: datetime = Field(
        ..., description="Datetime of article publication", example="2020-07-08T20:50:43Z"
    )
    modification_date: Optional[datetime] = Field(
        description="Datetime of article modification", default_factory=datetime.now
    )
    sections: List[Union[SECTION_TYPES]]


class MLStripper(HTMLParser, ABC):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


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
